from __future__ import absolute_import, division, print_function


import time
import sys
import random
import csv
import torch.optim as optim
from torch.utils.data import DataLoader
from tensorboardX import SummaryWriter

import json

from utils import *
from kitti_utils import *
from layers import *

import datasets
import networks
from linear_warmup_cosine_annealing_warm_restarts_weight_decay import ChainedScheduler


# torch.backends.cudnn.benchmark = True


def time_sync():
    # PyTorch-accurate time
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    return time.time()


class Trainer:
    def __init__(self, options):
        self.opt = options
        self.configure_reproducibility()
        self.configure_dataset_options()
        self.log_path = os.path.join(self.opt.log_dir, self.opt.model_name)

        # checking height and width are multiples of 32
        assert self.opt.height % 32 == 0, "'height' must be a multiple of 32"
        assert self.opt.width % 32 == 0, "'width' must be a multiple of 32"

        self.models = {}
        self.models_pose = {}
        self.teacher_models = {}
        self.parameters_to_train = []
        self.parameters_to_train_pose = []

        self.device = torch.device("cpu" if self.opt.no_cuda else "cuda")
        self.profile = self.opt.profile

        self.num_scales = len(self.opt.scales)
        self.frame_ids = len(self.opt.frame_ids)
        self.num_pose_frames = 2 if self.opt.pose_model_input == "pairs" else self.num_input_frames

        assert self.opt.frame_ids[0] == 0, "frame_ids must start with 0"

        self.use_pose_net = not (self.opt.use_stereo and self.opt.frame_ids == [0])

        if self.opt.use_stereo:
            self.opt.frame_ids.append("s")

        self.models["encoder"] = networks.LiteMono(model=self.opt.model,
                                                   drop_path_rate=self.opt.drop_path,
                                                   width=self.opt.width, height=self.opt.height)

        self.models["encoder"].to(self.device)
        if self.opt.freeze_depth_encoder:
            self.freeze_module(self.models["encoder"])
        else:
            self.parameters_to_train += list(self.models["encoder"].parameters())

        self.models["depth"] = networks.DepthDecoder(self.models["encoder"].num_ch_enc,
                                                     self.opt.scales)
        self.models["depth"].to(self.device)
        self.parameters_to_train += list(self.models["depth"].parameters())

        if self.use_pose_net:
            if self.opt.pose_model_type == "separate_resnet":
                self.models_pose["pose_encoder"] = networks.ResnetEncoder(
                    self.opt.num_layers,
                    self.opt.weights_init == "pretrained",
                    num_input_images=self.num_pose_frames)

                self.models_pose["pose_encoder"].to(self.device)
                self.parameters_to_train_pose += list(self.models_pose["pose_encoder"].parameters())

                self.models_pose["pose"] = networks.PoseDecoder(
                    self.models_pose["pose_encoder"].num_ch_enc,
                    num_input_features=1,
                    num_frames_to_predict_for=2)

            elif self.opt.pose_model_type == "shared":
                self.models_pose["pose"] = networks.PoseDecoder(
                    self.models["encoder"].num_ch_enc, self.num_pose_frames)

            elif self.opt.pose_model_type == "posecnn":
                self.models_pose["pose"] = networks.PoseCNN(
                    self.num_input_frames if self.opt.pose_model_input == "all" else 2)

            self.models_pose["pose"].to(self.device)
            self.parameters_to_train_pose += list(self.models_pose["pose"].parameters())

        if self.opt.predictive_mask:
            assert self.opt.disable_automasking, \
                "When using predictive_mask, please disable automasking with --disable_automasking"

            # Our implementation of the predictive masking baseline has the the same architecture
            # as our depth decoder. We predict a separate mask for each source frame.
            self.models["predictive_mask"] = networks.DepthDecoder(
                self.models["encoder"].num_ch_enc, self.opt.scales,
                num_output_channels=(len(self.opt.frame_ids) - 1))
            self.models["predictive_mask"].to(self.device)
            self.parameters_to_train += list(self.models["predictive_mask"].parameters())

        self.model_optimizer = optim.AdamW(self.parameters_to_train, self.opt.lr[0], weight_decay=self.opt.weight_decay)
        if self.use_pose_net:
            self.model_pose_optimizer = optim.AdamW(self.parameters_to_train_pose, self.opt.lr[3], weight_decay=self.opt.weight_decay)

        self.model_lr_scheduler = ChainedScheduler(
                            self.model_optimizer,
                            T_0=int(self.opt.lr[2]),
                            T_mul=1,
                            eta_min=self.opt.lr[1],
                            last_epoch=-1,
                            max_lr=self.opt.lr[0],
                            warmup_steps=0,
                            gamma=0.9
                        )
        self.model_pose_lr_scheduler = ChainedScheduler(
            self.model_pose_optimizer,
            T_0=int(self.opt.lr[5]),
            T_mul=1,
            eta_min=self.opt.lr[4],
            last_epoch=-1,
            max_lr=self.opt.lr[3],
            warmup_steps=0,
            gamma=0.9
        )

        if self.opt.load_weights_folder is not None:
            self.load_model()

        if self.opt.mypretrain is not None:
            self.load_pretrain()

        if self.teacher_structure_enabled():
            self.load_teacher_model()

        print("Training model named:\n  ", self.opt.model_name)
        print("Models and tensorboard events files are saved to:\n  ", self.opt.log_dir)
        print("Training is using:\n  ", self.device)

        # data
        train_dataset, val_dataset = self.build_train_val_datasets()

        num_train_samples = len(train_dataset)
        self.num_total_steps = num_train_samples // self.opt.batch_size * self.opt.num_epochs
        if self.opt.max_train_steps > 0:
            self.num_total_steps = min(self.num_total_steps, self.opt.max_train_steps)

        self.train_loader = DataLoader(
            train_dataset, self.opt.batch_size, True,
            num_workers=self.opt.num_workers, pin_memory=True, drop_last=True)
        self.val_loader = DataLoader(
            val_dataset, self.opt.batch_size, True,
            num_workers=self.opt.num_workers, pin_memory=True, drop_last=True)
        self.val_iter = iter(self.val_loader)

        self.writers = {}
        for mode in ["train", "val"]:
            self.writers[mode] = SummaryWriter(os.path.join(self.log_path, mode))

        if not self.opt.no_ssim:
            self.ssim = SSIM()
            self.ssim.to(self.device)

        self.backproject_depth = {}
        self.project_3d = {}
        for scale in self.opt.scales:
            h = self.opt.height // (2 ** scale)
            w = self.opt.width // (2 ** scale)

            self.backproject_depth[scale] = BackprojectDepth(self.opt.batch_size, h, w)
            self.backproject_depth[scale].to(self.device)

            self.project_3d[scale] = Project3D(self.opt.batch_size, h, w)
            self.project_3d[scale].to(self.device)

        self.depth_metric_names = [
            "de/abs_rel", "de/sq_rel", "de/rms", "de/log_rms", "da/a1", "da/a2", "da/a3"]

        print("Using split:\n  ", self.opt.split)
        print("There are {:d} training items and {:d} validation items\n".format(
            len(train_dataset), len(val_dataset)))

        self.save_opts()

    def configure_dataset_options(self):
        """Resolve dataset-specific training options before model/data setup."""
        if not hasattr(self.opt, "depth_metric_crop"):
            self.opt.depth_metric_crop = "auto"
        if not hasattr(self.opt, "citrus_prepared_name"):
            self.opt.citrus_prepared_name = "prepared_training_dataset"
        if not hasattr(self.opt, "citrus_max_neighbor_delta_ms"):
            self.opt.citrus_max_neighbor_delta_ms = 200.0
        if not hasattr(self.opt, "citrus_color_aug_probability"):
            self.opt.citrus_color_aug_probability = 0.5
        if not hasattr(self.opt, "max_train_steps"):
            self.opt.max_train_steps = 0
        if not hasattr(self.opt, "freeze_depth_steps"):
            self.opt.freeze_depth_steps = 0
        if not hasattr(self.opt, "freeze_depth_encoder"):
            self.opt.freeze_depth_encoder = False
        if not hasattr(self.opt, "save_step_frequency"):
            self.opt.save_step_frequency = 0
        if not hasattr(self.opt, "temporal_geo_consistency"):
            self.opt.temporal_geo_consistency = False
        if not hasattr(self.opt, "temporal_geo_weight"):
            self.opt.temporal_geo_weight = 0.03
        if not hasattr(self.opt, "temporal_geo_warmup_steps"):
            self.opt.temporal_geo_warmup_steps = 100
        if not hasattr(self.opt, "temporal_consistency_scales"):
            self.opt.temporal_consistency_scales = [0]
        if not hasattr(self.opt, "visibility_aware_geo"):
            self.opt.visibility_aware_geo = False
        if not hasattr(self.opt, "visibility_cycle_threshold"):
            self.opt.visibility_cycle_threshold = 0.35
        if not hasattr(self.opt, "texture_ambiguity_weighting"):
            self.opt.texture_ambiguity_weighting = False
        if not hasattr(self.opt, "texture_ambiguity_weight"):
            self.opt.texture_ambiguity_weight = 0.5
        if not hasattr(self.opt, "texture_ambiguity_patch_size"):
            self.opt.texture_ambiguity_patch_size = 5
        if not hasattr(self.opt, "texture_ambiguity_shift"):
            self.opt.texture_ambiguity_shift = 5
        if not hasattr(self.opt, "texture_ambiguity_color_delta"):
            self.opt.texture_ambiguity_color_delta = 0.08
        if not hasattr(self.opt, "texture_ambiguity_photo_gap"):
            self.opt.texture_ambiguity_photo_gap = 0.02
        if not hasattr(self.opt, "texture_ambiguity_min_photo_multiplier"):
            self.opt.texture_ambiguity_min_photo_multiplier = 0.5
        if not hasattr(self.opt, "feature_cross_view_consistency"):
            self.opt.feature_cross_view_consistency = False
        if not hasattr(self.opt, "feature_consistency_weight"):
            self.opt.feature_consistency_weight = 0.01
        if not hasattr(self.opt, "feature_consistency_warmup_steps"):
            self.opt.feature_consistency_warmup_steps = 100
        if not hasattr(self.opt, "feature_consistency_scale"):
            self.opt.feature_consistency_scale = 2
        if not hasattr(self.opt, "teacher_structure_regularization"):
            self.opt.teacher_structure_regularization = False
        if not hasattr(self.opt, "teacher_structure_weight"):
            self.opt.teacher_structure_weight = 0.03
        if not hasattr(self.opt, "teacher_structure_warmup_steps"):
            self.opt.teacher_structure_warmup_steps = 500
        if not hasattr(self.opt, "teacher_structure_decay"):
            self.opt.teacher_structure_decay = 0.5
        if not hasattr(self.opt, "teacher_gradient_loss"):
            self.opt.teacher_gradient_loss = False
        if not hasattr(self.opt, "teacher_gradient_weight"):
            self.opt.teacher_gradient_weight = 0.01
        if not hasattr(self.opt, "teacher_ranking_loss"):
            self.opt.teacher_ranking_loss = False
        if not hasattr(self.opt, "teacher_ranking_weight"):
            self.opt.teacher_ranking_weight = 0.02
        if not hasattr(self.opt, "teacher_rank_samples"):
            self.opt.teacher_rank_samples = 512
        if not hasattr(self.opt, "teacher_confidence"):
            self.opt.teacher_confidence = False
        if not hasattr(self.opt, "teacher_confidence_threshold"):
            self.opt.teacher_confidence_threshold = 0.25
        if not hasattr(self.opt, "teacher_texture_ambiguity_emphasis"):
            self.opt.teacher_texture_ambiguity_emphasis = False
        if not hasattr(self.opt, "teacher_path"):
            self.opt.teacher_path = os.path.join("weights", "lite-mono")
        if not hasattr(self.opt, "structure_aware_teacher"):
            self.opt.structure_aware_teacher = False
        if not hasattr(self.opt, "structure_edge_boost_weight"):
            self.opt.structure_edge_boost_weight = 0.75
        if not hasattr(self.opt, "structure_rgb_edge_threshold"):
            self.opt.structure_rgb_edge_threshold = 0.04
        if not hasattr(self.opt, "structure_rgb_edge_ramp"):
            self.opt.structure_rgb_edge_ramp = 0.12
        if not hasattr(self.opt, "structure_teacher_edge_threshold"):
            self.opt.structure_teacher_edge_threshold = 0.04
        if not hasattr(self.opt, "structure_teacher_edge_ramp"):
            self.opt.structure_teacher_edge_ramp = 0.12
        if not hasattr(self.opt, "structure_edge_dilation"):
            self.opt.structure_edge_dilation = 5
        if not hasattr(self.opt, "sky_far_structure_loss"):
            self.opt.sky_far_structure_loss = False
        if not hasattr(self.opt, "sky_far_weight"):
            self.opt.sky_far_weight = 0.01
        if not hasattr(self.opt, "sky_far_margin"):
            self.opt.sky_far_margin = 0.35
        if not hasattr(self.opt, "sky_top_fraction"):
            self.opt.sky_top_fraction = 0.65
        if not hasattr(self.opt, "sky_lower_reference_start"):
            self.opt.sky_lower_reference_start = 0.55
        if not hasattr(self.opt, "sky_blue_margin"):
            self.opt.sky_blue_margin = 0.03
        if not hasattr(self.opt, "sky_confidence_temperature"):
            self.opt.sky_confidence_temperature = 0.08
        if not hasattr(self.opt, "sky_min_brightness"):
            self.opt.sky_min_brightness = 0.25
        if not hasattr(self.opt, "sky_min_saturation"):
            self.opt.sky_min_saturation = 0.05
        if not hasattr(self.opt, "sky_min_ratio"):
            self.opt.sky_min_ratio = 0.01
        if self.opt.max_train_steps < 0:
            raise ValueError(
                "--max_train_steps must be non-negative; "
                "use 0 to run the full requested epochs")
        if self.opt.freeze_depth_steps < 0:
            raise ValueError(
                "--freeze_depth_steps must be non-negative; "
                "use 0 to update depth from the first step")
        if self.opt.save_step_frequency < 0:
            raise ValueError(
                "--save_step_frequency must be non-negative; "
                "use 0 to keep epoch-only checkpointing")
        if self.opt.freeze_depth_encoder and self.opt.pose_model_type == "shared":
            raise ValueError(
                "--freeze_depth_encoder is not supported with "
                "--pose_model_type shared because the depth encoder is also "
                "used as the pose encoder")
        if (
            self.temporal_consistency_enabled()
            and (self.opt.use_stereo or len(self.opt.frame_ids) <= 1)
        ):
            raise ValueError(
                "Temporal cross-view consistency requires monocular source frames "
                "and PoseNet; check --frame_ids and --use_stereo")
        if self.opt.temporal_geo_weight < 0.0:
            raise ValueError("--temporal_geo_weight must be non-negative")
        if self.opt.temporal_geo_warmup_steps < 0:
            raise ValueError("--temporal_geo_warmup_steps must be non-negative")
        if self.opt.feature_consistency_weight < 0.0:
            raise ValueError("--feature_consistency_weight must be non-negative")
        if self.opt.feature_consistency_warmup_steps < 0:
            raise ValueError("--feature_consistency_warmup_steps must be non-negative")
        if self.opt.visibility_cycle_threshold <= 0.0:
            raise ValueError("--visibility_cycle_threshold must be greater than 0")
        if not 0.0 <= self.opt.texture_ambiguity_weight <= 1.0:
            raise ValueError("--texture_ambiguity_weight must be between 0 and 1")
        if self.opt.texture_ambiguity_patch_size < 1:
            raise ValueError("--texture_ambiguity_patch_size must be at least 1")
        if self.opt.texture_ambiguity_patch_size % 2 == 0:
            raise ValueError("--texture_ambiguity_patch_size must be odd")
        if self.opt.texture_ambiguity_shift < 1:
            raise ValueError("--texture_ambiguity_shift must be at least 1")
        if self.opt.texture_ambiguity_color_delta <= 0.0:
            raise ValueError("--texture_ambiguity_color_delta must be greater than 0")
        if self.opt.texture_ambiguity_photo_gap <= 0.0:
            raise ValueError("--texture_ambiguity_photo_gap must be greater than 0")
        if not 0.0 <= self.opt.texture_ambiguity_min_photo_multiplier <= 1.0:
            raise ValueError(
                "--texture_ambiguity_min_photo_multiplier must be between 0 and 1")
        for scale in self.opt.temporal_consistency_scales:
            if scale not in self.opt.scales:
                raise ValueError(
                    "--temporal_consistency_scales contains {}, but --scales is {}".format(
                        scale, self.opt.scales))
        if self.opt.feature_cross_view_consistency:
            if self.opt.feature_consistency_scale not in self.opt.scales:
                raise ValueError(
                    "--feature_consistency_scale={} must also be present in --scales {}".format(
                        self.opt.feature_consistency_scale, self.opt.scales))
            if self.opt.feature_consistency_scale < 2:
                raise ValueError(
                    "--feature_consistency_scale must be at least 2 for Lite-Mono "
                    "encoder-feature warping")
        if self.opt.teacher_structure_weight < 0.0:
            raise ValueError("--teacher_structure_weight must be non-negative")
        if self.opt.teacher_structure_warmup_steps < 0:
            raise ValueError("--teacher_structure_warmup_steps must be non-negative")
        if not 0.0 <= self.opt.teacher_structure_decay <= 1.0:
            raise ValueError("--teacher_structure_decay must be between 0 and 1")
        if self.opt.teacher_gradient_weight < 0.0:
            raise ValueError("--teacher_gradient_weight must be non-negative")
        if self.opt.teacher_ranking_weight < 0.0:
            raise ValueError("--teacher_ranking_weight must be non-negative")
        if self.opt.teacher_rank_samples < 1:
            raise ValueError("--teacher_rank_samples must be at least 1")
        if self.opt.teacher_confidence_threshold <= 0.0:
            raise ValueError("--teacher_confidence_threshold must be greater than 0")
        if self.opt.structure_edge_boost_weight < 0.0:
            raise ValueError("--structure_edge_boost_weight must be non-negative")
        if self.opt.structure_rgb_edge_threshold < 0.0:
            raise ValueError("--structure_rgb_edge_threshold must be non-negative")
        if self.opt.structure_rgb_edge_ramp <= 0.0:
            raise ValueError("--structure_rgb_edge_ramp must be greater than 0")
        if self.opt.structure_teacher_edge_threshold < 0.0:
            raise ValueError("--structure_teacher_edge_threshold must be non-negative")
        if self.opt.structure_teacher_edge_ramp <= 0.0:
            raise ValueError("--structure_teacher_edge_ramp must be greater than 0")
        if self.opt.structure_edge_dilation < 1:
            raise ValueError("--structure_edge_dilation must be at least 1")
        if self.opt.structure_edge_dilation % 2 == 0:
            raise ValueError("--structure_edge_dilation must be odd")
        if self.opt.sky_far_weight < 0.0:
            raise ValueError("--sky_far_weight must be non-negative")
        if self.opt.sky_far_margin < 0.0:
            raise ValueError("--sky_far_margin must be non-negative")
        if not 0.0 < self.opt.sky_top_fraction <= 1.0:
            raise ValueError("--sky_top_fraction must be in (0, 1]")
        if not 0.0 <= self.opt.sky_lower_reference_start < 1.0:
            raise ValueError("--sky_lower_reference_start must be in [0, 1)")
        if self.opt.sky_confidence_temperature <= 0.0:
            raise ValueError("--sky_confidence_temperature must be greater than 0")
        if self.opt.sky_min_ratio < 0.0:
            raise ValueError("--sky_min_ratio must be non-negative")
        if (self.opt.structure_aware_teacher or self.opt.sky_far_structure_loss) and not (
            self.opt.teacher_structure_regularization
            or self.opt.teacher_gradient_loss
            or self.opt.teacher_ranking_loss
        ):
            raise ValueError(
                "--structure_aware_teacher and --sky_far_structure_loss extend "
                "the teacher-anchor method; enable at least one teacher "
                "structure, gradient, or ranking loss.")
        if self.teacher_structure_enabled() and self.opt.pose_model_type == "shared":
            raise ValueError(
                "Teacher-anchored regularization is tested with the separate "
                "depth encoder path, not --pose_model_type shared")
        if not 0.0 <= self.opt.citrus_color_aug_probability <= 1.0:
            raise ValueError(
                "--citrus_color_aug_probability must be between 0 and 1, "
                "got {}".format(self.opt.citrus_color_aug_probability))

        if self.opt.dataset == "citrus":
            default_kitti_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "kitti_data"))
            current_data_path = os.path.abspath(os.path.expanduser(self.opt.data_path))
            if current_data_path == default_kitti_path:
                self.opt.data_path = os.path.join(
                    os.path.dirname(__file__), "citrus_project", "dataset_workspace")

            if self.opt.split == "eigen_zhou":
                self.opt.split = "citrus_prepared"
            elif self.opt.split != "citrus_prepared":
                raise ValueError(
                    "dataset='citrus' expects --split citrus_prepared, "
                    "got {}".format(self.opt.split))

            if self.opt.use_stereo:
                raise ValueError("dataset='citrus' currently supports monocular training only")

            if self.opt.depth_metric_crop == "auto":
                self.opt.depth_metric_crop = "none"
            elif self.opt.depth_metric_crop != "none":
                raise ValueError(
                    "dataset='citrus' requires --depth_metric_crop none; "
                    "got {}".format(self.opt.depth_metric_crop))
        else:
            if self.opt.split == "citrus_prepared":
                raise ValueError("--split citrus_prepared is only valid with --dataset citrus")
            if self.opt.depth_metric_crop == "auto":
                self.opt.depth_metric_crop = "kitti_eigen"

    def build_train_val_datasets(self):
        if self.opt.dataset == "citrus":
            return self.build_citrus_train_val_datasets()

        datasets_dict = {"kitti": datasets.KITTIRAWDataset,
                         "kitti_odom": datasets.KITTIOdomDataset}
        self.dataset = datasets_dict[self.opt.dataset]
        fpath = os.path.join(os.path.dirname(__file__), "splits", self.opt.split, "{}_files.txt")
        train_filenames = readlines(fpath.format("train"))
        val_filenames = readlines(fpath.format("val"))
        img_ext = '.png' if self.opt.png else '.jpg'

        train_dataset = self.dataset(
            self.opt.data_path, train_filenames, self.opt.height, self.opt.width,
            self.opt.frame_ids, 4, is_train=True, img_ext=img_ext)
        val_dataset = self.dataset(
            self.opt.data_path, val_filenames, self.opt.height, self.opt.width,
            self.opt.frame_ids, 4, is_train=False, img_ext=img_ext)
        return train_dataset, val_dataset

    def build_citrus_train_val_datasets(self):
        citrus_module_dir = os.path.join(
            os.path.dirname(__file__), "citrus_project", "milestones", "02_citrus_integration")
        if citrus_module_dir not in sys.path:
            sys.path.insert(0, citrus_module_dir)
        from citrus_prepared_dataset import CitrusPreparedDataset

        dataset_kwargs = {
            "dataset_workspace": self.opt.data_path,
            "prepared_name": self.opt.citrus_prepared_name,
            "image_size": (self.opt.width, self.opt.height),
            "load_depth": True,
            "frame_ids": self.opt.frame_ids,
            "num_scales": 4,
            "max_neighbor_delta_ms": self.opt.citrus_max_neighbor_delta_ms,
            "include_metadata": False,
            "color_augmentation_probability": self.opt.citrus_color_aug_probability,
        }
        train_dataset = CitrusPreparedDataset(split="train", is_train=True, **dataset_kwargs)
        val_dataset = CitrusPreparedDataset(split="val", is_train=False, **dataset_kwargs)
        return train_dataset, val_dataset

    def set_train(self):
        """Convert all models to training mode
        """
        for m in self.models.values():
            m.train()
        if self.opt.freeze_depth_encoder:
            self.models["encoder"].eval()

    def set_eval(self):
        """Convert all models to testing/evaluation mode
        """
        for m in self.models.values():
            m.eval()

    def train(self):
        """Run the entire training pipeline
        """
        self.epoch = 0
        self.step = 0
        self.start_time = time.time()
        for self.epoch in range(self.opt.num_epochs):
            self.run_epoch()
            if (self.epoch + 1) % self.opt.save_frequency == 0:
                self.save_model()
            if self.reached_max_train_steps():
                break

    def run_epoch(self):
        """Run a single epoch of training and validation
        """

        print("Training")
        self.set_train()
        if self.depth_updates_frozen():
            print("Freezing depth optimizer updates for the first {} training steps.".format(
                self.opt.freeze_depth_steps))

        self.model_lr_scheduler.step()
        if self.use_pose_net:
            self.model_pose_lr_scheduler.step()

        for batch_idx, inputs in enumerate(self.train_loader):
            if self.reached_max_train_steps():
                break

            before_op_time = time.time()

            outputs, losses = self.process_batch(inputs)

            self.model_optimizer.zero_grad()
            if self.use_pose_net:
                self.model_pose_optimizer.zero_grad()
            losses["loss"].backward()
            if not self.depth_updates_frozen():
                self.model_optimizer.step()
            if self.use_pose_net:
                self.model_pose_optimizer.step()

            duration = time.time() - before_op_time

            # log less frequently after the first 2000 steps to save time & disk space
            early_phase = batch_idx % self.opt.log_frequency == 0 and self.step < 20000
            late_phase = self.step % 2000 == 0

            if early_phase or late_phase:
                self.log_time(batch_idx, duration, losses["loss"].cpu().data)

                if "depth_gt" in inputs:
                    self.compute_depth_losses(inputs, outputs, losses)

                self.log("train", inputs, outputs, losses)
                self.val()

            self.step += 1
            if self.opt.freeze_depth_steps > 0 and self.step == self.opt.freeze_depth_steps:
                print("Reached --freeze_depth_steps={}; depth optimizer updates are enabled.".format(
                    self.opt.freeze_depth_steps))
            if (
                self.opt.save_step_frequency > 0
                and self.step % self.opt.save_step_frequency == 0
            ):
                self.save_model("step_{}".format(self.step))
            if self.reached_max_train_steps():
                print("Reached --max_train_steps={}; stopping training.".format(
                    self.opt.max_train_steps))
                break

    def reached_max_train_steps(self):
        return self.opt.max_train_steps > 0 and self.step >= self.opt.max_train_steps

    def depth_updates_frozen(self):
        return self.opt.freeze_depth_steps > 0 and self.step < self.opt.freeze_depth_steps

    def configure_reproducibility(self):
        seed = getattr(self.opt, "seed", None)
        if seed is None:
            return
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    @staticmethod
    def freeze_module(module):
        for parameter in module.parameters():
            parameter.requires_grad = False
        module.eval()

    def temporal_consistency_enabled(self):
        return (
            self.opt.temporal_geo_consistency
            or self.opt.feature_cross_view_consistency
        )

    def teacher_structure_enabled(self):
        return (
            self.opt.teacher_structure_regularization
            or self.opt.teacher_gradient_loss
            or self.opt.teacher_ranking_loss
        )

    def ramped_weight(self, base_weight, warmup_steps):
        if base_weight <= 0.0:
            return 0.0
        if warmup_steps <= 0:
            return base_weight
        progress = min(1.0, float(self.step + 1) / float(warmup_steps))
        return base_weight * progress

    def teacher_scheduled_weight(self, base_weight):
        weight = self.ramped_weight(
            base_weight, self.opt.teacher_structure_warmup_steps)
        if weight <= 0.0:
            return 0.0
        if self.opt.teacher_structure_decay >= 1.0:
            return weight
        warmup_steps = max(0, self.opt.teacher_structure_warmup_steps)
        remaining_steps = max(1, self.num_total_steps - warmup_steps)
        progress = max(0.0, float(self.step + 1 - warmup_steps) / float(remaining_steps))
        progress = min(1.0, progress)
        decay = 1.0 - (1.0 - self.opt.teacher_structure_decay) * progress
        return weight * decay

    def feature_level_from_scale(self, scale):
        return scale - 2

    def select_encoder_feature(self, feature_list, scale):
        feature_level = self.feature_level_from_scale(scale)
        if feature_level < 0 or feature_level >= len(feature_list):
            raise ValueError(
                "Lite-Mono feature scale {} maps to unavailable encoder "
                "feature level {} from {} features".format(
                    scale, feature_level, len(feature_list)))
        return feature_list[feature_level]

    def predict_source_depths_and_features(
            self, inputs, outputs, pose_features, target_features):
        """Predict training-only source depths/features for cross-view losses."""
        requested_scales = set(self.opt.temporal_consistency_scales)
        if self.opt.feature_cross_view_consistency:
            requested_scales.add(self.opt.feature_consistency_scale)
            outputs[("target_feature", self.opt.feature_consistency_scale)] = (
                self.select_encoder_feature(
                    target_features, self.opt.feature_consistency_scale))

        for frame_id in self.opt.frame_ids[1:]:
            if frame_id == "s":
                continue

            if self.opt.pose_model_type == "shared":
                source_features = [feature.detach() for feature in pose_features[frame_id]]
                source_outputs = self.models["depth"](source_features)
            else:
                source_features, source_outputs = self.predict_source_teacher(
                    inputs[("color_aug", frame_id, 0)])

            if self.opt.feature_cross_view_consistency:
                outputs[("source_feature", frame_id, self.opt.feature_consistency_scale)] = (
                    self.select_encoder_feature(
                        source_features, self.opt.feature_consistency_scale).detach())

            for scale in requested_scales:
                if ("disp", scale) not in source_outputs:
                    continue
                outputs[("source_disp", frame_id, scale)] = (
                    source_outputs[("disp", scale)].detach())
                source_depth, _ = self.depth_from_disp_for_projection(
                    source_outputs[("disp", scale)], scale)
                outputs[("source_depth", frame_id, scale)] = source_depth.detach()

    def predict_source_teacher(self, source_image):
        """Run source-frame depth as a stop-gradient teacher for speed/stability."""
        encoder_was_training = self.models["encoder"].training
        depth_was_training = self.models["depth"].training
        self.models["encoder"].eval()
        self.models["depth"].eval()
        with torch.no_grad():
            source_features = self.models["encoder"](source_image)
            source_outputs = self.models["depth"](source_features)
        self.models["encoder"].train(encoder_was_training)
        self.models["depth"].train(depth_was_training)
        if self.opt.freeze_depth_encoder:
            self.models["encoder"].eval()
        return source_features, source_outputs

    def predict_teacher_structure(self, inputs, outputs):
        """Run the frozen RGB teacher on the target frame for pseudo-structure."""
        with torch.no_grad():
            teacher_features = self.teacher_models["encoder"](inputs[("color", 0, 0)])
            teacher_outputs = self.teacher_models["depth"](teacher_features)

        for scale in self.opt.scales:
            if ("disp", scale) in teacher_outputs:
                teacher_disp = teacher_outputs[("disp", scale)].detach()
                outputs[("teacher_disp", scale)] = teacher_disp
                _, teacher_depth = disp_to_depth(
                    teacher_disp, self.opt.min_depth, self.opt.max_depth)
                outputs[("teacher_depth", scale)] = teacher_depth.detach()

    def depth_from_disp_for_projection(self, disp, scale):
        """Match Lite-Mono's projection depth resolution for a disparity scale."""
        if self.opt.v1_multiscale:
            projection_scale = scale
            projection_disp = disp
        else:
            projection_scale = 0
            projection_disp = F.interpolate(
                disp, [self.opt.height, self.opt.width],
                mode="bilinear", align_corners=False)

        _, depth = disp_to_depth(
            projection_disp, self.opt.min_depth, self.opt.max_depth)
        return depth, projection_scale

    def process_batch(self, inputs):
        """Pass a minibatch through the network and generate images and losses
        """
        for key, ipt in inputs.items():
            inputs[key] = ipt.to(self.device)

        if self.opt.pose_model_type == "shared":
            # If we are using a shared encoder for both depth and pose (as advocated
            # in monodepthv1), then all images are fed separately through the depth encoder.
            all_color_aug = torch.cat([inputs[("color_aug", i, 0)] for i in self.opt.frame_ids])
            all_features = self.models["encoder"](all_color_aug)
            all_features = [torch.split(f, self.opt.batch_size) for f in all_features]

            features = {}
            for i, k in enumerate(self.opt.frame_ids):
                features[k] = [f[i] for f in all_features]

            target_features = features[0]
            outputs = self.models["depth"](target_features)
        else:
            # Otherwise, we only feed the image with frame_id 0 through the depth encoder

            features = self.models["encoder"](inputs["color_aug", 0, 0])
            target_features = features

            outputs = self.models["depth"](target_features)

        if self.opt.predictive_mask:
            outputs["predictive_mask"] = self.models["predictive_mask"](target_features)

        if self.use_pose_net:
            outputs.update(self.predict_poses(inputs, features))

        if self.temporal_consistency_enabled():
            self.predict_source_depths_and_features(
                inputs, outputs, features, target_features)

        if self.teacher_structure_enabled():
            self.predict_teacher_structure(inputs, outputs)

        self.generate_images_pred(inputs, outputs)
        losses = self.compute_losses(inputs, outputs)

        return outputs, losses

    def predict_poses(self, inputs, features):
        """Predict poses between input frames for monocular sequences.
        """
        outputs = {}
        if self.num_pose_frames == 2:
            # In this setting, we compute the pose to each source frame via a
            # separate forward pass through the pose network.

            # select what features the pose network takes as input
            if self.opt.pose_model_type == "shared":
                pose_feats = {f_i: features[f_i] for f_i in self.opt.frame_ids}
            else:
                pose_feats = {f_i: inputs["color_aug", f_i, 0] for f_i in self.opt.frame_ids}

            for f_i in self.opt.frame_ids[1:]:
                if f_i != "s":
                    # To maintain ordering we always pass frames in temporal order
                    if f_i < 0:
                        pose_inputs = [pose_feats[f_i], pose_feats[0]]
                    else:
                        pose_inputs = [pose_feats[0], pose_feats[f_i]]

                    if self.opt.pose_model_type == "separate_resnet":
                        pose_inputs = [self.models_pose["pose_encoder"](torch.cat(pose_inputs, 1))]
                    elif self.opt.pose_model_type == "posecnn":
                        pose_inputs = torch.cat(pose_inputs, 1)

                    axisangle, translation = self.models_pose["pose"](pose_inputs)
                    outputs[("axisangle", 0, f_i)] = axisangle
                    outputs[("translation", 0, f_i)] = translation

                    # Invert the matrix if the frame id is negative
                    outputs[("cam_T_cam", 0, f_i)] = transformation_from_parameters(
                        axisangle[:, 0], translation[:, 0], invert=(f_i < 0))

        else:
            # Here we input all frames to the pose net (and predict all poses) together
            if self.opt.pose_model_type in ["separate_resnet", "posecnn"]:
                pose_inputs = torch.cat(
                    [inputs[("color_aug", i, 0)] for i in self.opt.frame_ids if i != "s"], 1)

                if self.opt.pose_model_type == "separate_resnet":
                    pose_inputs = [self.models["pose_encoder"](pose_inputs)]

            elif self.opt.pose_model_type == "shared":
                pose_inputs = [features[i] for i in self.opt.frame_ids if i != "s"]

            axisangle, translation = self.models_pose["pose"](pose_inputs)

            for i, f_i in enumerate(self.opt.frame_ids[1:]):
                if f_i != "s":
                    outputs[("axisangle", 0, f_i)] = axisangle
                    outputs[("translation", 0, f_i)] = translation
                    outputs[("cam_T_cam", 0, f_i)] = transformation_from_parameters(
                        axisangle[:, i], translation[:, i])

        return outputs

    def val(self):
        """Validate the model on a single minibatch
        """
        self.set_eval()
        try:
            inputs = next(self.val_iter)
        except StopIteration:
            self.val_iter = iter(self.val_loader)
            inputs = next(self.val_iter)

        with torch.no_grad():
            outputs, losses = self.process_batch(inputs)

            if "depth_gt" in inputs:
                self.compute_depth_losses(inputs, outputs, losses)

            self.log("val", inputs, outputs, losses)
            del inputs, outputs, losses

        self.set_train()

    def generate_images_pred(self, inputs, outputs):
        """Generate the warped (reprojected) color images for a minibatch.
        Generated images are saved into the `outputs` dictionary.
        """
        for scale in self.opt.scales:
            disp = outputs[("disp", scale)]
            if self.opt.v1_multiscale:
                source_scale = scale
            else:
                disp = F.interpolate(
                    disp, [self.opt.height, self.opt.width], mode="bilinear", align_corners=False)
                source_scale = 0

            _, depth = disp_to_depth(disp, self.opt.min_depth, self.opt.max_depth)

            outputs[("depth", 0, scale)] = depth

            for i, frame_id in enumerate(self.opt.frame_ids[1:]):

                if frame_id == "s":
                    T = inputs["stereo_T"]
                else:
                    T = outputs[("cam_T_cam", 0, frame_id)]

                # from the authors of https://arxiv.org/abs/1712.00175
                if self.opt.pose_model_type == "posecnn":

                    axisangle = outputs[("axisangle", 0, frame_id)]
                    translation = outputs[("translation", 0, frame_id)]

                    inv_depth = 1 / depth
                    mean_inv_depth = inv_depth.mean(3, True).mean(2, True)

                    T = transformation_from_parameters(
                        axisangle[:, 0], translation[:, 0] * mean_inv_depth[:, 0], frame_id < 0)

                cam_points = self.backproject_depth[source_scale](
                    depth, inputs[("inv_K", source_scale)])
                pix_coords = self.project_3d[source_scale](
                    cam_points, inputs[("K", source_scale)], T)

                outputs[("sample", frame_id, scale)] = pix_coords

                outputs[("color", frame_id, scale)] = F.grid_sample(
                    inputs[("color", frame_id, source_scale)],
                    outputs[("sample", frame_id, scale)],
                    padding_mode="border", align_corners=True)

                if not self.opt.disable_automasking:
                    outputs[("color_identity", frame_id, scale)] = \
                        inputs[("color", frame_id, source_scale)]

    def compute_reprojection_loss(self, pred, target):
        """Computes reprojection loss between a batch of predicted and target images
        """
        abs_diff = torch.abs(target - pred)
        l1_loss = abs_diff.mean(1, True)

        if self.opt.no_ssim:
            reprojection_loss = l1_loss
        else:
            ssim_loss = self.ssim(pred, target).mean(1, True)
            reprojection_loss = 0.85 * ssim_loss + 0.15 * l1_loss

        return reprojection_loss

    def compute_losses(self, inputs, outputs):
        """Compute the reprojection and smoothness losses for a minibatch
        """

        losses = {}
        total_loss = 0

        for scale in self.opt.scales:
            loss = 0
            reprojection_losses = []

            if self.opt.v1_multiscale:
                source_scale = scale
            else:
                source_scale = 0

            disp = outputs[("disp", scale)]
            color = inputs[("color", 0, scale)]
            target = inputs[("color", 0, source_scale)]

            for frame_id in self.opt.frame_ids[1:]:
                pred = outputs[("color", frame_id, scale)]
                reprojection_losses.append(self.compute_reprojection_loss(pred, target))

            reprojection_losses = torch.cat(reprojection_losses, 1)

            if not self.opt.disable_automasking:
                identity_reprojection_losses = []
                for frame_id in self.opt.frame_ids[1:]:
                    pred = inputs[("color", frame_id, source_scale)]
                    identity_reprojection_losses.append(
                        self.compute_reprojection_loss(pred, target))

                identity_reprojection_losses = torch.cat(identity_reprojection_losses, 1)

                if self.opt.avg_reprojection:
                    identity_reprojection_loss = identity_reprojection_losses.mean(1, keepdim=True)
                else:
                    # save both images, and do min all at once below
                    identity_reprojection_loss = identity_reprojection_losses

            elif self.opt.predictive_mask:
                # use the predicted mask
                mask = outputs["predictive_mask"]["disp", scale]
                if not self.opt.v1_multiscale:
                    mask = F.interpolate(
                        mask, [self.opt.height, self.opt.width],
                        mode="bilinear", align_corners=False)

                reprojection_losses *= mask

                # add a loss pushing mask to 1 (using nn.BCELoss for stability)
                weighting_loss = 0.2 * nn.BCELoss()(mask, torch.ones(mask.shape).cuda())
                loss += weighting_loss.mean()

            if self.opt.avg_reprojection:
                reprojection_loss = reprojection_losses.mean(1, keepdim=True)
            else:
                reprojection_loss = reprojection_losses

            ambiguity_map = None
            if (
                self.opt.texture_ambiguity_weighting
                or (
                    scale == 0
                    and
                    self.teacher_structure_enabled()
                    and self.opt.teacher_texture_ambiguity_emphasis
                )
            ):
                identity_for_ambiguity = (
                    identity_reprojection_loss if not self.opt.disable_automasking else None)
                ambiguity_map = self.compute_texture_ambiguity_map(
                    target, reprojection_loss, identity_for_ambiguity,
                    outputs, losses, scale)

            if not self.opt.disable_automasking:
                # add random numbers to break ties
                identity_reprojection_loss += torch.randn(
                    identity_reprojection_loss.shape, device=self.device) * 0.00001

                combined = torch.cat((identity_reprojection_loss, reprojection_loss), dim=1)
            else:
                combined = reprojection_loss

            if combined.shape[1] == 1:
                to_optimise = combined
            else:
                to_optimise, idxs = torch.min(combined, dim=1)

            if not self.opt.disable_automasking:
                outputs["identity_selection/{}".format(scale)] = (
                    idxs > identity_reprojection_loss.shape[1] - 1).float()

            photo_error_map = to_optimise
            if photo_error_map.dim() == 3:
                photo_error_map = photo_error_map.unsqueeze(1)
            outputs[("photo_error", scale)] = photo_error_map.detach()

            if self.opt.texture_ambiguity_weighting:
                photo_loss = self.compute_texture_weighted_photo_loss(
                    to_optimise, ambiguity_map, losses, scale)
            else:
                photo_loss = to_optimise.mean()

            loss += photo_loss
            losses["photo_loss/{}".format(scale)] = photo_loss.detach()

            mean_disp = disp.mean(2, True).mean(3, True)
            norm_disp = disp / (mean_disp + 1e-7)
            smooth_loss = get_smooth_loss(norm_disp, color)

            smooth_weighted = self.opt.disparity_smoothness * smooth_loss / (2 ** scale)
            loss += smooth_weighted
            losses["smooth_loss/{}".format(scale)] = smooth_loss.detach()
            losses["smooth_loss_weighted/{}".format(scale)] = smooth_weighted.detach()

            if self.teacher_structure_enabled() and scale == 0:
                teacher_loss = self.compute_teacher_structure_losses(
                    outputs, losses, scale, ambiguity_map, target)
                loss += teacher_loss

            if self.opt.temporal_geo_consistency and scale in self.opt.temporal_consistency_scales:
                geo_loss = self.compute_temporal_geo_consistency_loss(
                    inputs, outputs, losses, scale, ambiguity_map)
                geo_weight = self.ramped_weight(
                    self.opt.temporal_geo_weight,
                    self.opt.temporal_geo_warmup_steps)
                geo_weighted = geo_weight * geo_loss / (2 ** scale)
                loss += geo_weighted
                losses["temporal_geo/weight/{}".format(scale)] = torch.tensor(
                    geo_weight, device=self.device)
                losses["temporal_geo/weighted_loss/{}".format(scale)] = (
                    geo_weighted.detach())

            if (
                self.opt.feature_cross_view_consistency
                and scale == self.opt.feature_consistency_scale
            ):
                feature_loss = self.compute_feature_cross_view_consistency_loss(
                    inputs, outputs, losses, scale, ambiguity_map)
                feature_weight = self.ramped_weight(
                    self.opt.feature_consistency_weight,
                    self.opt.feature_consistency_warmup_steps)
                feature_weighted = feature_weight * feature_loss
                loss += feature_weighted
                losses["feature_consistency/weight/{}".format(scale)] = torch.tensor(
                    feature_weight, device=self.device)
                losses["feature_consistency/weighted_loss/{}".format(scale)] = (
                    feature_weighted.detach())

            total_loss += loss
            losses["loss/{}".format(scale)] = loss

        total_loss /= self.num_scales
        losses["loss"] = total_loss
        return losses

    def charbonnier(self, error, epsilon=1e-3):
        return torch.sqrt(error * error + epsilon * epsilon)

    def normalized_log_inverse_from_disp(self, disp, reference_shape=None):
        """Return per-image normalized log inverse depth from a decoder disparity."""
        if reference_shape is not None and disp.shape[-2:] != reference_shape:
            disp = F.interpolate(
                disp, reference_shape, mode="bilinear", align_corners=False)
        inverse_depth, _ = disp_to_depth(
            disp, self.opt.min_depth, self.opt.max_depth)
        log_inverse = torch.log(inverse_depth.clamp_min(1e-6))
        mean = log_inverse.mean(dim=(2, 3), keepdim=True)
        variance = ((log_inverse - mean) ** 2).mean(dim=(2, 3), keepdim=True)
        std = torch.sqrt(variance + 1e-6)
        return (log_inverse - mean) / std

    def weighted_mean(self, values, weights=None):
        if weights is None:
            return values.mean()
        weights = weights.expand_as(values)
        return (values * weights).sum() / (weights.sum() + 1e-6)

    def gradient_magnitude_map(self, tensor):
        grad_x = torch.abs(tensor[:, :, :, 1:] - tensor[:, :, :, :-1])
        grad_y = torch.abs(tensor[:, :, 1:, :] - tensor[:, :, :-1, :])
        magnitude = torch.zeros_like(tensor)
        count = torch.zeros_like(tensor)
        magnitude[:, :, :, 1:] += grad_x
        magnitude[:, :, :, :-1] += grad_x
        count[:, :, :, 1:] += 1.0
        count[:, :, :, :-1] += 1.0
        magnitude[:, :, 1:, :] += grad_y
        magnitude[:, :, :-1, :] += grad_y
        count[:, :, 1:, :] += 1.0
        count[:, :, :-1, :] += 1.0
        return magnitude / count.clamp_min(1.0)

    def ramped_map(self, values, threshold, ramp):
        return torch.clamp((values - threshold) / ramp, min=0.0, max=1.0)

    def vertical_prior(self, reference, start, end, top_to_bottom=True):
        height = reference.shape[-2]
        y = torch.linspace(
            0.0, 1.0, height, device=reference.device,
            dtype=reference.dtype).view(1, 1, height, 1)
        if top_to_bottom:
            prior = torch.clamp((end - y) / max(end - start, 1e-6), 0.0, 1.0)
        else:
            prior = torch.clamp((y - start) / max(end - start, 1e-6), 0.0, 1.0)
        return prior.expand_as(reference)

    def compute_sky_confidence(self, target):
        r = target[:, 0:1]
        g = target[:, 1:2]
        b = target[:, 2:3]
        brightness = target.mean(1, keepdim=True)
        saturation = target.max(1, keepdim=True)[0] - target.min(1, keepdim=True)[0]
        blue_dominance = b - torch.maximum(r, g)
        temperature = self.opt.sky_confidence_temperature

        blue_score = torch.sigmoid(
            (blue_dominance - self.opt.sky_blue_margin) / temperature)
        brightness_score = torch.sigmoid(
            (brightness - self.opt.sky_min_brightness) / temperature)
        saturation_score = torch.sigmoid(
            (saturation - self.opt.sky_min_saturation) / temperature)
        top_prior = self.vertical_prior(
            brightness, 0.0, self.opt.sky_top_fraction, top_to_bottom=True)
        return (
            blue_score * brightness_score * saturation_score * top_prior
        ).detach()

    def compute_structure_context(
            self, target, teacher_structure, outputs, losses, scale):
        gray = (
            0.299 * target[:, 0:1]
            + 0.587 * target[:, 1:2]
            + 0.114 * target[:, 2:3])
        rgb_gradient = self.gradient_magnitude_map(gray)
        rgb_edge = self.ramped_map(
            rgb_gradient,
            self.opt.structure_rgb_edge_threshold,
            self.opt.structure_rgb_edge_ramp)

        teacher_gradient = self.gradient_magnitude_map(teacher_structure.detach())
        teacher_edge = self.ramped_map(
            teacher_gradient,
            self.opt.structure_teacher_edge_threshold,
            self.opt.structure_teacher_edge_ramp)

        boundary = (rgb_edge * teacher_edge).detach()
        if self.opt.structure_edge_dilation > 1:
            pad = self.opt.structure_edge_dilation // 2
            boundary = F.max_pool2d(
                boundary,
                kernel_size=self.opt.structure_edge_dilation,
                stride=1,
                padding=pad)

        sky = self.compute_sky_confidence(target)
        lower = self.vertical_prior(
            sky, self.opt.sky_lower_reference_start, 1.0,
            top_to_bottom=False)
        lower = (lower * (1.0 - sky)).detach()

        outputs[("structure_rgb_edge", scale)] = rgb_edge.detach()
        outputs[("structure_teacher_edge", scale)] = teacher_edge.detach()
        outputs[("structure_boundary_reliability", scale)] = boundary.detach()
        outputs[("structure_sky_confidence", scale)] = sky.detach()
        outputs[("structure_lower_reference", scale)] = lower.detach()

        losses["structure_rgb_edge/mean/{}".format(scale)] = rgb_edge.mean()
        losses["structure_rgb_edge/ratio/{}".format(scale)] = (
            (rgb_edge > 0.5).float().mean())
        losses["structure_teacher_edge/mean/{}".format(scale)] = teacher_edge.mean()
        losses["structure_boundary/mean/{}".format(scale)] = boundary.mean()
        losses["structure_boundary/ratio/{}".format(scale)] = (
            (boundary > 0.25).float().mean())
        losses["structure_sky/mean/{}".format(scale)] = sky.mean()
        losses["structure_sky/ratio/{}".format(scale)] = (
            (sky > 0.25).float().mean())
        losses["structure_lower_reference/mean/{}".format(scale)] = lower.mean()

        return {
            "boundary": boundary,
            "sky": sky,
            "lower": lower,
        }

    def teacher_weight_map(self, student_structure, teacher_structure,
                           ambiguity_map, structure_context, outputs, losses, scale):
        weights = torch.ones_like(student_structure)

        if self.opt.teacher_confidence:
            agreement_error = torch.abs(
                student_structure.detach() - teacher_structure.detach())
            confidence = torch.exp(
                -agreement_error / self.opt.teacher_confidence_threshold).detach()
            weights = weights * confidence
            outputs[("teacher_confidence", scale)] = confidence
            losses["teacher_confidence/mean/{}".format(scale)] = confidence.mean()
            losses["teacher_confidence/low_ratio/{}".format(scale)] = (
                (confidence < 0.5).float().mean())

        if self.opt.teacher_texture_ambiguity_emphasis:
            boost = self.ambiguity_boost_for(ambiguity_map, weights)
            weights = weights * boost
            losses["teacher_structure/texture_boost_mean/{}".format(scale)] = (
                boost.mean())

        if self.opt.structure_aware_teacher and structure_context is not None:
            boost = 1.0 + (
                self.opt.structure_edge_boost_weight * structure_context["boundary"])
            weights = weights * boost
            losses["structure_boundary/teacher_boost_mean/{}".format(scale)] = (
                boost.mean())
            losses["structure_boundary/teacher_boost_max/{}".format(scale)] = (
                boost.max())

        return weights.detach()

    def gradient_error_map(self, grad_x_error, grad_y_error, reference):
        error_map = torch.zeros_like(reference)
        count_map = torch.zeros_like(reference)
        error_map[:, :, :, 1:] += grad_x_error
        count_map[:, :, :, 1:] += 1.0
        error_map[:, :, :, :-1] += grad_x_error
        count_map[:, :, :, :-1] += 1.0
        error_map[:, :, 1:, :] += grad_y_error
        count_map[:, :, 1:, :] += 1.0
        error_map[:, :, :-1, :] += grad_y_error
        count_map[:, :, :-1, :] += 1.0
        return error_map / count_map.clamp_min(1.0)

    def compute_teacher_gradient_loss(
            self, student_structure, teacher_structure, weights, losses, outputs, scale):
        student_grad_x = student_structure[:, :, :, 1:] - student_structure[:, :, :, :-1]
        teacher_grad_x = teacher_structure[:, :, :, 1:] - teacher_structure[:, :, :, :-1]
        student_grad_y = student_structure[:, :, 1:, :] - student_structure[:, :, :-1, :]
        teacher_grad_y = teacher_structure[:, :, 1:, :] - teacher_structure[:, :, :-1, :]

        grad_x_error = self.charbonnier(student_grad_x - teacher_grad_x)
        grad_y_error = self.charbonnier(student_grad_y - teacher_grad_y)
        loss_x = self.weighted_mean(grad_x_error, weights[:, :, :, 1:])
        loss_y = self.weighted_mean(grad_y_error, weights[:, :, 1:, :])
        gradient_loss = 0.5 * (loss_x + loss_y)

        outputs[("teacher_gradient_error", scale)] = self.gradient_error_map(
            grad_x_error.detach(), grad_y_error.detach(), student_structure)
        losses["teacher_gradient/loss/{}".format(scale)] = gradient_loss.detach()
        losses["teacher_gradient/error_mean/{}".format(scale)] = (
            outputs[("teacher_gradient_error", scale)].mean())
        return gradient_loss

    def compute_teacher_ranking_loss(
            self, student_structure, teacher_structure, weights, losses, scale):
        batch_size, _, height, width = student_structure.shape
        num_pixels = height * width
        sample_count = min(self.opt.teacher_rank_samples, num_pixels)
        student_flat = student_structure.view(batch_size, num_pixels)
        teacher_flat = teacher_structure.detach().view(batch_size, num_pixels)
        weight_flat = weights.view(batch_size, num_pixels)

        idx_a = torch.randint(
            0, num_pixels, (batch_size, sample_count), device=self.device)
        idx_b = torch.randint(
            0, num_pixels, (batch_size, sample_count), device=self.device)

        student_a = torch.gather(student_flat, 1, idx_a)
        student_b = torch.gather(student_flat, 1, idx_b)
        teacher_a = torch.gather(teacher_flat, 1, idx_a)
        teacher_b = torch.gather(teacher_flat, 1, idx_b)
        pair_weight = torch.minimum(
            torch.gather(weight_flat, 1, idx_a),
            torch.gather(weight_flat, 1, idx_b)).detach()

        teacher_diff = teacher_a - teacher_b
        student_diff = student_a - student_b
        valid = torch.abs(teacher_diff) > self.opt.teacher_confidence_threshold
        valid_weight = pair_weight * valid.float()
        valid_sum = valid_weight.sum()

        if valid_sum.item() <= 0:
            zero = student_structure.new_tensor(0.0)
            losses["teacher_ranking/loss/{}".format(scale)] = zero
            losses["teacher_ranking/valid_ratio/{}".format(scale)] = zero
            losses["teacher_ranking/agreement/{}".format(scale)] = zero
            return zero

        teacher_sign = torch.sign(teacher_diff).detach()
        ranking_error = F.softplus(-teacher_sign * student_diff)
        ranking_loss = (ranking_error * valid_weight).sum() / (valid_sum + 1e-6)
        agreement = (
            ((teacher_sign * student_diff.detach()) > 0).float() * valid.float()
        ).sum() / (valid.float().sum() + 1e-6)

        losses["teacher_ranking/loss/{}".format(scale)] = ranking_loss.detach()
        losses["teacher_ranking/valid_ratio/{}".format(scale)] = valid.float().mean()
        losses["teacher_ranking/agreement/{}".format(scale)] = agreement.detach()
        losses["teacher_ranking/weight_mean/{}".format(scale)] = (
            valid_weight.mean().detach())
        return ranking_loss

    def compute_sky_far_structure_loss(
            self, student_structure, structure_context, losses, scale):
        sky = structure_context["sky"]
        lower = structure_context["lower"]
        eps = 1e-6
        sky_sum = sky.sum(dim=(2, 3), keepdim=True)
        lower_sum = lower.sum(dim=(2, 3), keepdim=True)
        sky_ratio = sky.mean(dim=(2, 3), keepdim=True)
        lower_ratio = lower.mean(dim=(2, 3), keepdim=True)
        valid = (
            (sky_ratio >= self.opt.sky_min_ratio)
            & (lower_ratio >= self.opt.sky_min_ratio)
        ).float()

        sky_mean = (student_structure * sky).sum(
            dim=(2, 3), keepdim=True) / (sky_sum + eps)
        lower_mean = (student_structure * lower).sum(
            dim=(2, 3), keepdim=True) / (lower_sum + eps)
        separation = lower_mean - sky_mean
        per_image_loss = F.softplus(self.opt.sky_far_margin - separation)
        valid_count = valid.sum()
        sky_loss = (per_image_loss * valid).sum() / valid_count.clamp_min(1.0)

        losses["sky_far/loss/{}".format(scale)] = sky_loss.detach()
        losses["sky_far/valid_image_ratio/{}".format(scale)] = valid.mean()
        losses["sky_far/sky_ratio_mean/{}".format(scale)] = sky_ratio.mean()
        losses["sky_far/lower_ratio_mean/{}".format(scale)] = lower_ratio.mean()
        losses["sky_far/separation_mean/{}".format(scale)] = (
            (separation.detach() * valid).sum() / valid_count.clamp_min(1.0))
        return sky_loss

    def compute_teacher_structure_losses(
            self, outputs, losses, scale, ambiguity_map, target):
        if ("teacher_disp", scale) not in outputs:
            raise ValueError(
                "Teacher structure regularization is enabled, but teacher output "
                "for scale {} is missing".format(scale))

        student_structure = self.normalized_log_inverse_from_disp(
            outputs[("disp", scale)])
        teacher_structure = self.normalized_log_inverse_from_disp(
            outputs[("teacher_disp", scale)],
            reference_shape=student_structure.shape[-2:]).detach()

        structure_error = self.charbonnier(student_structure - teacher_structure)
        outputs[("teacher_structure_diff", scale)] = structure_error.detach()
        outputs[("teacher_structure_student", scale)] = student_structure.detach()
        outputs[("teacher_structure_teacher", scale)] = teacher_structure.detach()

        structure_context = None
        if self.opt.structure_aware_teacher or self.opt.sky_far_structure_loss:
            structure_context = self.compute_structure_context(
                target, teacher_structure, outputs, losses, scale)

        weights = self.teacher_weight_map(
            student_structure, teacher_structure, ambiguity_map,
            structure_context, outputs, losses, scale)
        total_teacher_loss = student_structure.new_tensor(0.0)

        if self.opt.teacher_structure_regularization:
            structure_loss = self.weighted_mean(structure_error, weights)
            structure_weight = self.teacher_scheduled_weight(
                self.opt.teacher_structure_weight)
            weighted = structure_weight * structure_loss
            total_teacher_loss = total_teacher_loss + weighted
            losses["teacher_structure/loss/{}".format(scale)] = (
                structure_loss.detach())
            losses["teacher_structure/weight/{}".format(scale)] = torch.tensor(
                structure_weight, device=self.device)
            losses["teacher_structure/weighted_loss/{}".format(scale)] = (
                weighted.detach())
            losses["teacher_structure/diff_mean/{}".format(scale)] = (
                structure_error.detach().mean())

        if self.opt.teacher_gradient_loss:
            gradient_loss = self.compute_teacher_gradient_loss(
                student_structure, teacher_structure, weights, losses, outputs, scale)
            gradient_weight = self.teacher_scheduled_weight(
                self.opt.teacher_gradient_weight)
            weighted = gradient_weight * gradient_loss
            total_teacher_loss = total_teacher_loss + weighted
            losses["teacher_gradient/weight/{}".format(scale)] = torch.tensor(
                gradient_weight, device=self.device)
            losses["teacher_gradient/weighted_loss/{}".format(scale)] = (
                weighted.detach())

        if self.opt.teacher_ranking_loss:
            ranking_loss = self.compute_teacher_ranking_loss(
                student_structure, teacher_structure, weights, losses, scale)
            ranking_weight = self.teacher_scheduled_weight(
                self.opt.teacher_ranking_weight)
            weighted = ranking_weight * ranking_loss
            total_teacher_loss = total_teacher_loss + weighted
            losses["teacher_ranking/weight/{}".format(scale)] = torch.tensor(
                ranking_weight, device=self.device)
            losses["teacher_ranking/weighted_loss/{}".format(scale)] = (
                weighted.detach())

        if self.opt.sky_far_structure_loss:
            sky_loss = self.compute_sky_far_structure_loss(
                student_structure, structure_context, losses, scale)
            sky_weight = self.teacher_scheduled_weight(self.opt.sky_far_weight)
            weighted = sky_weight * sky_loss
            total_teacher_loss = total_teacher_loss + weighted
            losses["sky_far/weight/{}".format(scale)] = torch.tensor(
                sky_weight, device=self.device)
            losses["sky_far/weighted_loss/{}".format(scale)] = weighted.detach()

        losses["teacher_structure/total_weighted/{}".format(scale)] = (
            total_teacher_loss.detach())
        return total_teacher_loss

    def shifted_image(self, image, dy, dx):
        """Reflect-shift an image tensor without introducing wraparound seams."""
        height, width = image.shape[-2:]
        pad_left = max(dx, 0)
        pad_right = max(-dx, 0)
        pad_top = max(dy, 0)
        pad_bottom = max(-dy, 0)
        padded = F.pad(
            image, (pad_left, pad_right, pad_top, pad_bottom), mode="reflect")
        y0 = max(-dy, 0)
        x0 = max(-dx, 0)
        return padded[:, :, y0:y0 + height, x0:x0 + width]

    def resize_like(self, tensor, reference):
        if tensor.shape[-2:] == reference.shape[-2:]:
            return tensor
        return F.interpolate(
            tensor, reference.shape[-2:], mode="bilinear", align_corners=False)

    def compute_texture_ambiguity_map(
            self, target, reprojection_loss, identity_reprojection_loss,
            outputs, losses, scale):
        """Estimate RGB-only texture/matching ambiguity without vegetation labels."""
        eps = 1e-7
        shift = self.opt.texture_ambiguity_shift
        diffs = []
        for dy, dx in [(0, shift), (0, -shift), (shift, 0), (-shift, 0)]:
            shifted = self.shifted_image(target, dy, dx)
            diff = torch.abs(target - shifted).mean(1, keepdim=True)
            diffs.append(diff)
        min_shift_diff = torch.min(torch.cat(diffs, dim=1), dim=1, keepdim=True)[0]

        kernel = self.opt.texture_ambiguity_patch_size
        if kernel > 1:
            pad = kernel // 2
            min_shift_diff = F.avg_pool2d(
                F.pad(min_shift_diff, (pad, pad, pad, pad), mode="reflect"),
                kernel_size=kernel,
                stride=1)

        self_similarity = 1.0 - torch.clamp(
            min_shift_diff / (self.opt.texture_ambiguity_color_delta + eps),
            min=0.0,
            max=1.0)

        if reprojection_loss.shape[1] > 1:
            sorted_reprojection = torch.sort(reprojection_loss.detach(), dim=1)[0]
            source_gap = sorted_reprojection[:, 1:2] - sorted_reprojection[:, 0:1]
            source_ambiguity = 1.0 - torch.clamp(
                source_gap / (self.opt.texture_ambiguity_photo_gap + eps),
                min=0.0,
                max=1.0)
        else:
            source_gap = torch.zeros_like(self_similarity)
            source_ambiguity = torch.zeros_like(self_similarity)

        if identity_reprojection_loss is not None:
            reproj_min = reprojection_loss.detach().min(1, keepdim=True)[0]
            identity_min = identity_reprojection_loss.detach().min(1, keepdim=True)[0]
            margin = identity_min - reproj_min
            margin_ambiguity = 1.0 - torch.clamp(
                torch.abs(margin) / (self.opt.texture_ambiguity_photo_gap + eps),
                min=0.0,
                max=1.0)
        else:
            margin = torch.zeros_like(self_similarity)
            margin_ambiguity = torch.zeros_like(self_similarity)

        ambiguity = torch.clamp(
            0.50 * self_similarity
            + 0.25 * source_ambiguity
            + 0.25 * margin_ambiguity,
            min=0.0,
            max=1.0).detach()

        outputs[("texture_ambiguity", scale)] = ambiguity
        losses["texture_ambiguity/mean/{}".format(scale)] = ambiguity.mean()
        losses["texture_ambiguity/ratio/{}".format(scale)] = (
            (ambiguity > 0.5).float().mean())
        losses["texture_ambiguity/self_similarity_mean/{}".format(scale)] = (
            self_similarity.detach().mean())
        losses["texture_ambiguity/source_gap_mean/{}".format(scale)] = (
            source_gap.detach().mean())
        losses["texture_ambiguity/photo_margin_mean/{}".format(scale)] = (
            margin.detach().mean())
        return ambiguity

    def compute_texture_weighted_photo_loss(
            self, photo_loss_map, ambiguity_map, losses, scale):
        """Reduce raw photometric reliance where RGB matching is ambiguous."""
        if photo_loss_map.dim() == 3:
            photo_loss_map = photo_loss_map.unsqueeze(1)
        ambiguity = self.resize_like(ambiguity_map, photo_loss_map)
        max_suppression = 1.0 - self.opt.texture_ambiguity_min_photo_multiplier
        multiplier = 1.0 - (
            max_suppression
            * self.opt.texture_ambiguity_weight
            * ambiguity)
        multiplier = torch.clamp(
            multiplier,
            min=self.opt.texture_ambiguity_min_photo_multiplier,
            max=1.0).detach()

        weighted_photo_loss = (photo_loss_map * multiplier).mean()
        losses["texture_ambiguity/photo_multiplier_mean/{}".format(scale)] = (
            multiplier.mean())
        losses["texture_ambiguity/photo_loss_before/{}".format(scale)] = (
            photo_loss_map.mean().detach())
        losses["texture_ambiguity/photo_loss_after/{}".format(scale)] = (
            weighted_photo_loss.detach())
        return weighted_photo_loss

    def ambiguity_boost_for(self, ambiguity_map, reference):
        if ambiguity_map is None:
            return torch.ones_like(reference)
        ambiguity = self.resize_like(ambiguity_map, reference)
        return (1.0 + self.opt.texture_ambiguity_weight * ambiguity).detach()

    def project_target_depth_to_source(
            self, inputs, outputs, frame_id, target_depth, projection_scale):
        """Project target-camera depth into a source frame using PoseNet pose."""
        T = outputs[("cam_T_cam", 0, frame_id)]
        cam_points = self.backproject_depth[projection_scale](
            target_depth, inputs[("inv_K", projection_scale)])
        source_points = torch.matmul(T, cam_points)
        projected_z = source_points[:, 2:3, :].view_as(target_depth)
        pix_coords = self.project_3d[projection_scale](
            cam_points, inputs[("K", projection_scale)], T)

        x_valid = (pix_coords[..., 0] > -1.0) & (pix_coords[..., 0] < 1.0)
        y_valid = (pix_coords[..., 1] > -1.0) & (pix_coords[..., 1] < 1.0)
        in_bounds = (x_valid & y_valid).unsqueeze(1)
        positive_depth = projected_z > self.opt.min_depth
        projection_valid = in_bounds & positive_depth & torch.isfinite(projected_z)
        return pix_coords, projected_z, projection_valid

    def compute_temporal_geo_consistency_loss(
            self, inputs, outputs, losses, scale, ambiguity_map):
        """Compare target-projected depth with source-frame predicted depth."""
        eps = 1e-6
        projection_scale = scale if self.opt.v1_multiscale else 0
        target_depth = outputs[("depth", 0, scale)]
        total_loss = target_depth.new_tensor(0.0)
        frame_count = 0
        valid_ratios = []
        visibility_ratios = []
        invalid_ratios = []
        error_means = []
        error_maps = []
        visibility_maps = []
        projection_maps = []

        for frame_id in self.opt.frame_ids[1:]:
            if frame_id == "s" or ("source_depth", frame_id, scale) not in outputs:
                continue

            pix_coords, projected_z, projection_valid = (
                self.project_target_depth_to_source(
                    inputs, outputs, frame_id, target_depth, projection_scale))
            source_depth = outputs[("source_depth", frame_id, scale)]
            if source_depth.shape[-2:] != target_depth.shape[-2:]:
                source_depth = F.interpolate(
                    source_depth, target_depth.shape[-2:],
                    mode="bilinear", align_corners=False)
            sampled_source_depth = F.grid_sample(
                source_depth, pix_coords, padding_mode="zeros", align_corners=True)

            finite_source = (
                torch.isfinite(sampled_source_depth)
                & (sampled_source_depth > self.opt.min_depth))
            projection_valid = projection_valid & finite_source
            log_error = torch.abs(
                torch.log(sampled_source_depth.clamp_min(self.opt.min_depth))
                - torch.log(projected_z.clamp_min(self.opt.min_depth)))

            visibility_mask = projection_valid
            if self.opt.visibility_aware_geo:
                visibility_mask = (
                    projection_valid
                    & (log_error.detach() < self.opt.visibility_cycle_threshold))

            weights = visibility_mask.float()
            weights = weights * self.ambiguity_boost_for(ambiguity_map, weights)
            robust_error = torch.sqrt(log_error * log_error + 1e-4)
            frame_loss = (robust_error * weights).sum() / (weights.sum() + eps)
            total_loss = total_loss + frame_loss
            frame_count += 1

            projection_float = projection_valid.float()
            visibility_float = visibility_mask.float()
            valid_ratio = projection_float.mean()
            visibility_ratio = visibility_float.mean()
            valid_denom = projection_float.sum().clamp_min(1.0)
            error_mean = (
                (log_error.detach() * projection_float).sum() / valid_denom)

            valid_ratios.append(valid_ratio)
            visibility_ratios.append(visibility_ratio)
            invalid_ratios.append(1.0 - valid_ratio)
            error_means.append(error_mean)
            error_maps.append((log_error.detach() * projection_float))
            visibility_maps.append(visibility_float.detach())
            projection_maps.append(projection_float.detach())

        if frame_count == 0:
            zero = target_depth.new_tensor(0.0)
            losses["temporal_geo/loss/{}".format(scale)] = zero
            losses["temporal_geo/visibility_mask_ratio/{}".format(scale)] = zero
            losses["temporal_geo/projection_invalid_ratio/{}".format(scale)] = zero
            return zero

        loss = total_loss / frame_count
        losses["temporal_geo/loss/{}".format(scale)] = loss.detach()
        losses["temporal_geo/projection_valid_ratio/{}".format(scale)] = (
            torch.stack(valid_ratios).mean().detach())
        losses["temporal_geo/projection_invalid_ratio/{}".format(scale)] = (
            torch.stack(invalid_ratios).mean().detach())
        losses["temporal_geo/visibility_mask_ratio/{}".format(scale)] = (
            torch.stack(visibility_ratios).mean().detach())
        losses["temporal_geo/log_depth_error_mean/{}".format(scale)] = (
            torch.stack(error_means).mean().detach())

        outputs[("temporal_geo_error", scale)] = torch.stack(error_maps).mean(0)
        outputs[("temporal_geo_visibility", scale)] = torch.stack(visibility_maps).mean(0)
        outputs[("temporal_geo_projection_valid", scale)] = (
            torch.stack(projection_maps).mean(0))
        return loss

    def compute_feature_cross_view_consistency_loss(
            self, inputs, outputs, losses, scale, ambiguity_map):
        """Warp source encoder features to target and compare with cosine distance."""
        eps = 1e-6
        target_feature = outputs[("target_feature", scale)]
        target_disp = outputs[("disp", scale)]
        _, target_depth = disp_to_depth(
            target_disp, self.opt.min_depth, self.opt.max_depth)

        total_loss = target_feature.new_tensor(0.0)
        frame_count = 0
        mask_ratios = []
        error_means = []
        error_maps = []
        mask_maps = []

        target_feature_norm = F.normalize(target_feature, p=2, dim=1, eps=eps)

        for frame_id in self.opt.frame_ids[1:]:
            if frame_id == "s" or ("source_feature", frame_id, scale) not in outputs:
                continue

            pix_coords, projected_z, projection_valid = (
                self.project_target_depth_to_source(
                    inputs, outputs, frame_id, target_depth, scale))
            source_feature = outputs[("source_feature", frame_id, scale)].detach()
            source_feature_norm = F.normalize(source_feature, p=2, dim=1, eps=eps)
            warped_source_feature = F.grid_sample(
                source_feature_norm, pix_coords,
                padding_mode="zeros", align_corners=True)
            feature_error = torch.clamp(
                1.0 - (target_feature_norm * warped_source_feature).sum(
                    1, keepdim=True),
                min=0.0,
                max=2.0)

            finite_mask = torch.isfinite(feature_error)
            visibility_mask = projection_valid & finite_mask
            if self.opt.visibility_aware_geo and ("source_disp", frame_id, scale) in outputs:
                _, native_source_depth = disp_to_depth(
                    outputs[("source_disp", frame_id, scale)],
                    self.opt.min_depth,
                    self.opt.max_depth)
                sampled_source_depth = F.grid_sample(
                    native_source_depth, pix_coords,
                    padding_mode="zeros", align_corners=True)
                depth_error = torch.abs(
                    torch.log(sampled_source_depth.clamp_min(self.opt.min_depth))
                    - torch.log(projected_z.clamp_min(self.opt.min_depth)))
                visibility_mask = (
                    visibility_mask
                    & torch.isfinite(sampled_source_depth)
                    & (sampled_source_depth > self.opt.min_depth)
                    & (depth_error.detach() < self.opt.visibility_cycle_threshold))

            weights = visibility_mask.float()
            weights = weights * self.ambiguity_boost_for(ambiguity_map, weights)
            frame_loss = (feature_error * weights).sum() / (weights.sum() + eps)
            total_loss = total_loss + frame_loss
            frame_count += 1

            mask_ratio = visibility_mask.float().mean()
            mask_ratios.append(mask_ratio)
            error_means.append((feature_error.detach() * weights).sum() / (weights.sum() + eps))
            error_maps.append((feature_error.detach() * visibility_mask.float()))
            mask_maps.append(visibility_mask.float().detach())

        if frame_count == 0:
            zero = target_feature.new_tensor(0.0)
            losses["feature_consistency/loss/{}".format(scale)] = zero
            losses["feature_consistency/mask_ratio/{}".format(scale)] = zero
            return zero

        loss = total_loss / frame_count
        losses["feature_consistency/loss/{}".format(scale)] = loss.detach()
        losses["feature_consistency/mask_ratio/{}".format(scale)] = (
            torch.stack(mask_ratios).mean().detach())
        losses["feature_consistency/error_mean/{}".format(scale)] = (
            torch.stack(error_means).mean().detach())

        outputs[("feature_consistency_error", scale)] = torch.stack(error_maps).mean(0)
        outputs[("feature_consistency_mask", scale)] = torch.stack(mask_maps).mean(0)
        return loss

    def compute_depth_losses(self, inputs, outputs, losses):
        """Compute depth metrics, to allow monitoring during training

        This isn't particularly accurate as it averages over the entire batch,
        so is only used to give an indication of validation performance
        """
        depth_pred = outputs[("depth", 0, 0)]
        depth_gt = inputs["depth_gt"]
        depth_height, depth_width = depth_gt.shape[-2:]
        depth_pred = torch.clamp(F.interpolate(
            depth_pred, [depth_height, depth_width], mode="bilinear", align_corners=False), 1e-3, 80)
        depth_pred = depth_pred.detach()

        mask = self.get_depth_metric_mask(inputs, depth_gt, depth_pred)

        if not torch.any(mask):
            for metric in self.depth_metric_names:
                losses[metric] = np.array(np.nan)
            return

        depth_gt = depth_gt[mask]
        depth_pred = depth_pred[mask]
        depth_pred *= torch.median(depth_gt) / torch.median(depth_pred)

        depth_pred = torch.clamp(depth_pred, min=1e-3, max=80)

        depth_errors = compute_depth_errors(depth_gt, depth_pred)

        for i, metric in enumerate(self.depth_metric_names):
            losses[metric] = np.array(depth_errors[i].cpu())

    def get_depth_metric_mask(self, inputs, depth_gt, depth_pred):
        """Build the valid mask for training-time depth metric logging."""
        mask = torch.isfinite(depth_gt) & torch.isfinite(depth_pred) & (depth_gt > 0)

        if "valid_mask" in inputs:
            valid_mask = inputs["valid_mask"].to(device=depth_gt.device)
            if valid_mask.shape != depth_gt.shape:
                raise ValueError(
                    "valid_mask must match depth_gt for depth metric logging; "
                    "got valid_mask shape {} and depth_gt shape {}".format(
                        tuple(valid_mask.shape), tuple(depth_gt.shape)))
            mask = mask & (valid_mask > 0)

        crop_mode = getattr(self.opt, "depth_metric_crop", "kitti_eigen")
        if crop_mode == "kitti_eigen":
            if depth_gt.shape[-2:] != (375, 1242):
                raise ValueError(
                    "depth_metric_crop='kitti_eigen' expects KITTI depth_gt shape "
                    "375 x 1242, but got {} x {}. For Citrus/non-KITTI labels, "
                    "set --depth_metric_crop none so metric logging uses the "
                    "native label geometry and valid_mask.".format(
                        depth_gt.shape[-2], depth_gt.shape[-1]))
            crop_mask = torch.zeros_like(mask)
            crop_mask[:, :, 153:371, 44:1197] = True
            mask = mask & crop_mask
        elif crop_mode == "none":
            pass
        else:
            raise ValueError("Unsupported depth_metric_crop: {}".format(crop_mode))

        return mask

    def log_time(self, batch_idx, duration, loss):
        """Print a logging statement to the terminal
        """
        samples_per_sec = self.opt.batch_size / duration
        time_sofar = time.time() - self.start_time
        training_time_left = (
            self.num_total_steps / self.step - 1.0) * time_sofar if self.step > 0 else 0
        print_string = "epoch {:>3} | lr {:.6f} |lr_p {:.6f} | batch {:>6} | examples/s: {:5.1f}" + \
            " | loss: {:.5f} | time elapsed: {} | time left: {}"
        print(print_string.format(self.epoch, self.model_optimizer.state_dict()['param_groups'][0]['lr'],
                                  self.model_pose_optimizer.state_dict()['param_groups'][0]['lr'],
                                  batch_idx, samples_per_sec, loss,
                                  sec_to_hm_str(time_sofar), sec_to_hm_str(training_time_left)))

    def log(self, mode, inputs, outputs, losses):
        """Write an event to the tensorboard events file
        """
        writer = self.writers[mode]
        for l, v in losses.items():
            writer.add_scalar("{}".format(l), v, self.step)
        self.write_scalar_diagnostics(mode, losses)

        for j in range(min(4, self.opt.batch_size)):  # write a maxmimum of four images
            for s in self.opt.scales:
                for frame_id in self.opt.frame_ids:
                    writer.add_image(
                        "color_{}_{}/{}".format(frame_id, s, j),
                        inputs[("color", frame_id, s)][j].data, self.step)
                    if s == 0 and frame_id != 0:
                        writer.add_image(
                            "color_pred_{}_{}/{}".format(frame_id, s, j),
                            outputs[("color", frame_id, s)][j].data, self.step)

                writer.add_image(
                    "disp_{}/{}".format(s, j),
                    normalize_image(outputs[("disp", s)][j]), self.step)

                if self.opt.predictive_mask:
                    for f_idx, frame_id in enumerate(self.opt.frame_ids[1:]):
                        writer.add_image(
                            "predictive_mask_{}_{}/{}".format(frame_id, s, j),
                            outputs["predictive_mask"][("disp", s)][j, f_idx][None, ...],
                            self.step)

                elif not self.opt.disable_automasking:
                    writer.add_image(
                        "automask_{}/{}".format(s, j),
                        outputs["identity_selection/{}".format(s)][j][None, ...], self.step)

                debug_maps = [
                    (("photo_error", s), "photo_error"),
                    (("texture_ambiguity", s), "texture_ambiguity"),
                    (("temporal_geo_error", s), "temporal_geo_error"),
                    (("temporal_geo_visibility", s), "temporal_geo_visibility"),
                    (("temporal_geo_projection_valid", s), "temporal_geo_projection_valid"),
                    (("feature_consistency_error", s), "feature_consistency_error"),
                    (("feature_consistency_mask", s), "feature_consistency_mask"),
                    (("teacher_disp", s), "teacher_disp"),
                    (("teacher_depth", s), "teacher_depth"),
                    (("teacher_structure_diff", s), "teacher_structure_diff"),
                    (("teacher_structure_student", s), "teacher_structure_student"),
                    (("teacher_structure_teacher", s), "teacher_structure_teacher"),
                    (("teacher_gradient_error", s), "teacher_gradient_error"),
                    (("teacher_confidence", s), "teacher_confidence"),
                    (("structure_rgb_edge", s), "structure_rgb_edge"),
                    (("structure_teacher_edge", s), "structure_teacher_edge"),
                    (("structure_boundary_reliability", s), "structure_boundary_reliability"),
                    (("structure_sky_confidence", s), "structure_sky_confidence"),
                    (("structure_lower_reference", s), "structure_lower_reference"),
                ]
                for key, name in debug_maps:
                    if key in outputs:
                        writer.add_image(
                            "{}_{}/{}".format(name, s, j),
                            normalize_image(outputs[key][j]), self.step)

    def write_scalar_diagnostics(self, mode, losses):
        """Save latest method diagnostics in plain JSON/CSV for quick review."""
        if mode != "train":
            return
        if not (
            self.temporal_consistency_enabled()
            or self.opt.texture_ambiguity_weighting
            or self.teacher_structure_enabled()
        ):
            return

        diagnostics = {
            "step": int(self.step),
            "epoch": int(self.epoch),
        }
        for name, value in losses.items():
            if isinstance(value, torch.Tensor):
                if value.numel() != 1:
                    continue
                diagnostics[name] = float(value.detach().cpu())
            elif isinstance(value, np.ndarray):
                if value.size != 1:
                    continue
                diagnostics[name] = float(value.reshape(-1)[0])
            elif np.isscalar(value):
                diagnostics[name] = float(value)

        json_path = os.path.join(self.log_path, "diagnostics_last_logged.json")
        csv_path = os.path.join(self.log_path, "diagnostics_last_logged.csv")
        with open(json_path, "w", encoding="utf-8") as fp:
            json.dump(diagnostics, fp, indent=2, sort_keys=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=sorted(diagnostics.keys()))
            writer.writeheader()
            writer.writerow(diagnostics)

    def save_opts(self):
        """Save options to disk so we know what we ran this experiment with
        """
        models_dir = os.path.join(self.log_path, "models")
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        to_save = self.opt.__dict__.copy()

        with open(os.path.join(models_dir, 'opt.json'), 'w') as f:
            json.dump(to_save, f, indent=2)

    def save_model(self, folder_name=None):
        """Save model weights to disk
        """
        if folder_name is None:
            folder_name = "weights_{}".format(self.epoch)
        save_folder = os.path.join(self.log_path, "models", folder_name)
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        for model_name, model in self.models.items():
            save_path = os.path.join(save_folder, "{}.pth".format(model_name))
            to_save = model.state_dict()
            if model_name == 'encoder':
                # save the sizes - these are needed at prediction time
                to_save['height'] = self.opt.height
                to_save['width'] = self.opt.width
                to_save['use_stereo'] = self.opt.use_stereo
            torch.save(to_save, save_path)

        for model_name, model in self.models_pose.items():
            save_path = os.path.join(save_folder, "{}.pth".format(model_name))
            to_save = model.state_dict()
            torch.save(to_save, save_path)

        save_path = os.path.join(save_folder, "{}.pth".format("adam"))
        torch.save(self.model_optimizer.state_dict(), save_path)

        save_path = os.path.join(save_folder, "{}.pth".format("adam_pose"))
        if self.use_pose_net:
            torch.save(self.model_pose_optimizer.state_dict(), save_path)

    def load_pretrain(self):
        self.opt.mypretrain = os.path.expanduser(self.opt.mypretrain)
        path = self.opt.mypretrain
        model_dict = self.models["encoder"].state_dict()
        pretrained_dict = torch.load(path)['model']
        pretrained_dict = {k: v for k, v in pretrained_dict.items() if (k in model_dict and not k.startswith('norm'))}
        model_dict.update(pretrained_dict)
        self.models["encoder"].load_state_dict(model_dict)
        print('mypretrain loaded.')

    def load_teacher_model(self):
        """Load a frozen RGB-only teacher used only for training regularization."""
        teacher_path = os.path.expanduser(self.opt.teacher_path)
        if not os.path.isabs(teacher_path):
            teacher_path = os.path.join(os.path.dirname(__file__), teacher_path)
        if not os.path.isdir(teacher_path):
            raise FileNotFoundError(
                "Cannot find --teacher_path folder {}".format(teacher_path))

        self.teacher_models["encoder"] = networks.LiteMono(
            model=self.opt.model,
            drop_path_rate=self.opt.drop_path,
            width=self.opt.width,
            height=self.opt.height)
        self.teacher_models["depth"] = networks.DepthDecoder(
            self.teacher_models["encoder"].num_ch_enc, self.opt.scales)

        for name, model in self.teacher_models.items():
            weights_path = os.path.join(teacher_path, "{}.pth".format(name))
            if not os.path.isfile(weights_path):
                raise FileNotFoundError(
                    "Cannot find teacher {} weights at {}".format(name, weights_path))
            model_dict = model.state_dict()
            pretrained_dict = torch.load(weights_path, map_location=self.device)
            pretrained_dict = {
                k: v for k, v in pretrained_dict.items()
                if k in model_dict and hasattr(v, "shape")
                and tuple(v.shape) == tuple(model_dict[k].shape)
            }
            model_dict.update(pretrained_dict)
            model.load_state_dict(model_dict)
            model.to(self.device)
            self.freeze_module(model)

        print("Frozen RGB teacher loaded from:\n  {}".format(teacher_path))

    def load_model(self):
        """Load model(s) from disk
        """
        self.opt.load_weights_folder = os.path.expanduser(self.opt.load_weights_folder)

        assert os.path.isdir(self.opt.load_weights_folder), \
            "Cannot find folder {}".format(self.opt.load_weights_folder)
        print("loading model from folder {}".format(self.opt.load_weights_folder))

        for n in self.opt.models_to_load:
            print("Loading {} weights...".format(n))
            path = os.path.join(self.opt.load_weights_folder, "{}.pth".format(n))

            if n in ['pose_encoder', 'pose']:
                model_dict = self.models_pose[n].state_dict()
                pretrained_dict = torch.load(path)
                pretrained_dict = {k: v for k, v in pretrained_dict.items() if k in model_dict}
                model_dict.update(pretrained_dict)
                self.models_pose[n].load_state_dict(model_dict)
            else:
                model_dict = self.models[n].state_dict()
                pretrained_dict = torch.load(path)
                pretrained_dict = {k: v for k, v in pretrained_dict.items() if k in model_dict}
                model_dict.update(pretrained_dict)
                self.models[n].load_state_dict(model_dict)

        # loading adam state

        optimizer_load_path = os.path.join(self.opt.load_weights_folder, "adam.pth")
        optimizer_pose_load_path = os.path.join(self.opt.load_weights_folder, "adam_pose.pth")
        if os.path.isfile(optimizer_load_path):
            print("Loading Adam weights")
            optimizer_dict = torch.load(optimizer_load_path)
            optimizer_pose_dict = torch.load(optimizer_pose_load_path)
            self.model_optimizer.load_state_dict(optimizer_dict)
            self.model_pose_optimizer.load_state_dict(optimizer_pose_dict)
        else:
            print("Cannot find Adam weights so Adam is randomly initialized")
