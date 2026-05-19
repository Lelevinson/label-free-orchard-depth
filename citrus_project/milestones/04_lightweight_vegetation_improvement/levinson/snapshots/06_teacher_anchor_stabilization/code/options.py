from __future__ import absolute_import, division, print_function

import os
import argparse

file_dir = os.path.dirname(__file__)  # the directory that options.py resides in


class LiteMonoOptions:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Lite-Mono options")

        # PATHS
        self.parser.add_argument("--data_path",
                                 type=str,
                                 help="path to the training data",
                                 default=os.path.join(file_dir, "kitti_data"))
        self.parser.add_argument("--log_dir",
                                 type=str,
                                 help="log directory",
                                 default="./tmp")

        # TRAINING options
        self.parser.add_argument("--model_name",
                                 type=str,
                                 help="the name of the folder to save the model in",
                                 default="lite-mono")
        self.parser.add_argument("--split",
                                 type=str,
                                 help="which training split to use",
                                 choices=["eigen_zhou", "eigen_full", "odom", "benchmark",
                                          "citrus_prepared"],
                                 default="eigen_zhou")
        self.parser.add_argument("--model",
                                 type=str,
                                 help="which model to load",
                                 choices=["lite-mono", "lite-mono-small", "lite-mono-tiny", "lite-mono-8m"],
                                 default="lite-mono")
        self.parser.add_argument("--weight_decay",
                                 type=float,
                                 help="weight decay in AdamW",
                                 default=1e-2)
        self.parser.add_argument("--drop_path",
                                 type=float,
                                 help="drop path rate",
                                 default=0.2)
        self.parser.add_argument("--num_layers",
                                 type=int,
                                 help="number of resnet layers",
                                 default=18,
                                 choices=[18, 34, 50, 101, 152])
        self.parser.add_argument("--dataset",
                                 type=str,
                                 help="dataset to train on",
                                 default="kitti",
                                 choices=["kitti", "kitti_odom", "kitti_depth", "kitti_test",
                                          "citrus"])
        self.parser.add_argument("--citrus_prepared_name",
                                 type=str,
                                 help="prepared Citrus dataset folder name inside data_path",
                                 default="prepared_training_dataset")
        self.parser.add_argument("--citrus_max_neighbor_delta_ms",
                                 type=float,
                                 help="maximum timestamp gap for Citrus temporal neighbors",
                                 default=200.0)
        self.parser.add_argument("--citrus_color_aug_probability",
                                 type=float,
                                 help="probability of applying train-only Citrus color jitter",
                                 default=0.5)
        self.parser.add_argument("--png",
                                 help="if set, trains from raw KITTI png files (instead of jpgs)",
                                 action="store_true")
        self.parser.add_argument("--height",
                                 type=int,
                                 help="input image height",
                                 default=192)
        self.parser.add_argument("--width",
                                 type=int,
                                 help="input image width",
                                 default=640)
        self.parser.add_argument("--disparity_smoothness",
                                 type=float,
                                 help="disparity smoothness weight",
                                 default=1e-3)
        self.parser.add_argument("--scales",
                                 nargs="+",
                                 type=int,
                                 help="scales used in the loss",
                                 default=[0, 1, 2])
        self.parser.add_argument("--min_depth",
                                 type=float,
                                 help="minimum depth",
                                 default=0.1)
        self.parser.add_argument("--max_depth",
                                 type=float,
                                 help="maximum depth",
                                 default=100.0)
        self.parser.add_argument("--use_stereo",
                                 help="if set, uses stereo pair for training",
                                 action="store_true")
        self.parser.add_argument("--frame_ids",
                                 nargs="+",
                                 type=int,
                                 help="frames to load",
                                 default=[0, -1, 1])

        self.parser.add_argument("--profile",
                                 type=bool,
                                 help="profile once at the beginning of the training",
                                 default=True)

        # OPTIMIZATION options
        self.parser.add_argument("--batch_size",
                                 type=int,
                                 help="batch size",
                                 default=16)
        self.parser.add_argument("--lr",
                                 nargs="+",
                                 type=float,
                                 help="learning rates of DepthNet and PoseNet. "
                                      "Initial learning rate, "
                                      "minimum learning rate, "
                                      "First cycle step size.",
                                 default=[0.0001, 5e-6, 31, 0.0001, 1e-5, 31])
        self.parser.add_argument("--num_epochs",
                                 type=int,
                                 help="number of epochs",
                                 default=50)
        self.parser.add_argument("--seed",
                                 type=int,
                                 help="optional random seed for reproducible short runs; "
                                      "unset preserves the original behavior",
                                 default=None)
        self.parser.add_argument("--max_train_steps",
                                 type=int,
                                 help="optional safety limit for optimizer steps; "
                                      "0 means run the full requested epochs",
                                 default=0)
        self.parser.add_argument("--freeze_depth_steps",
                                 type=int,
                                 help="optional pose warmup; skip depth optimizer updates "
                                      "for the first N training steps while pose still updates. "
                                      "0 disables this behavior",
                                 default=0)
        self.parser.add_argument("--freeze_depth_encoder",
                                 help="if set, keep the depth encoder weights and BatchNorm "
                                      "running statistics frozen during training; only the "
                                      "depth decoder remains in the depth optimizer",
                                 action="store_true")
        self.parser.add_argument("--save_step_frequency",
                                 type=int,
                                 help="optional step checkpoint interval; "
                                      "0 keeps the original epoch-only checkpoint behavior",
                                 default=0)
        self.parser.add_argument("--scheduler_step_size",
                                 type=int,
                                 help="step size of the scheduler",
                                 default=15)

        # ABLATION options
        self.parser.add_argument("--v1_multiscale",
                                 help="if set, uses monodepth v1 multiscale",
                                 action="store_true")
        self.parser.add_argument("--avg_reprojection",
                                 help="if set, uses average reprojection loss",
                                 action="store_true")
        self.parser.add_argument("--disable_automasking",
                                 help="if set, doesn't do auto-masking",
                                 action="store_true")
        self.parser.add_argument("--predictive_mask",
                                 help="if set, uses a predictive masking scheme as in Zhou et al",
                                 action="store_true")
        self.parser.add_argument("--temporal_geo_consistency",
                                 help="if set, adds a training-only temporal depth consistency "
                                      "loss between target and source-frame predictions",
                                 action="store_true")
        self.parser.add_argument("--temporal_geo_weight",
                                 type=float,
                                 help="weight for temporal geometric consistency",
                                 default=0.03)
        self.parser.add_argument("--temporal_geo_warmup_steps",
                                 type=int,
                                 help="linearly ramps temporal geometry weight over this many "
                                      "optimizer steps; 0 disables warmup",
                                 default=100)
        self.parser.add_argument("--temporal_consistency_scales",
                                 nargs="+",
                                 type=int,
                                 help="disparity scales where temporal geometry is applied",
                                 default=[0])
        self.parser.add_argument("--visibility_aware_geo",
                                 help="if set, masks temporal geometry pixels with large "
                                      "cross-view depth disagreement as likely occlusions or "
                                      "non-rigid/out-of-view cases",
                                 action="store_true")
        self.parser.add_argument("--visibility_cycle_threshold",
                                 type=float,
                                 help="maximum detached log-depth disagreement kept by the "
                                      "visibility-aware temporal geometry mask",
                                 default=0.35)
        self.parser.add_argument("--texture_ambiguity_weighting",
                                 help="if set, detects RGB-only repeated/ambiguous texture "
                                      "regions and downweights raw photometric loss while "
                                      "boosting temporal consistency losses there",
                                 action="store_true")
        self.parser.add_argument("--texture_ambiguity_weight",
                                 type=float,
                                 help="strength of texture ambiguity weighting and temporal "
                                      "consistency boost",
                                 default=0.5)
        self.parser.add_argument("--texture_ambiguity_patch_size",
                                 type=int,
                                 help="odd local smoothing window used for RGB self-similarity "
                                      "ambiguity estimates",
                                 default=5)
        self.parser.add_argument("--texture_ambiguity_shift",
                                 type=int,
                                 help="pixel offset used when comparing nearby RGB patches for "
                                      "self-similarity",
                                 default=5)
        self.parser.add_argument("--texture_ambiguity_color_delta",
                                 type=float,
                                 help="RGB patch-difference scale where self-similarity stops "
                                      "being treated as ambiguous",
                                 default=0.08)
        self.parser.add_argument("--texture_ambiguity_photo_gap",
                                 type=float,
                                 help="photometric loss gap/margin scale used to identify "
                                      "ambiguous source-frame matches",
                                 default=0.02)
        self.parser.add_argument("--texture_ambiguity_min_photo_multiplier",
                                 type=float,
                                 help="lowest multiplier applied to raw photometric loss in "
                                      "high-ambiguity pixels",
                                 default=0.5)
        self.parser.add_argument("--feature_cross_view_consistency",
                                 help="if set, adds low-resolution encoder-feature consistency "
                                      "across temporal views using predicted depth and PoseNet",
                                 action="store_true")
        self.parser.add_argument("--feature_consistency_weight",
                                 type=float,
                                 help="weight for feature-level cross-view consistency",
                                 default=0.01)
        self.parser.add_argument("--feature_consistency_warmup_steps",
                                 type=int,
                                 help="linearly ramps feature consistency weight over this many "
                                      "optimizer steps; 0 disables warmup",
                                 default=100)
        self.parser.add_argument("--feature_consistency_scale",
                                 type=int,
                                 help="image-pyramid scale used for encoder feature warping; "
                                      "Lite-Mono's first encoder feature is scale 2",
                                 default=2)
        self.parser.add_argument("--teacher_structure_regularization",
                                 help="if set, adds training-only RGB-teacher anchored "
                                      "scale-invariant relative depth structure loss",
                                 action="store_true")
        self.parser.add_argument("--teacher_structure_weight",
                                 type=float,
                                 help="weight for normalized inverse-depth/log-depth teacher "
                                      "relative-structure agreement",
                                 default=0.03)
        self.parser.add_argument("--teacher_structure_warmup_steps",
                                 type=int,
                                 help="linearly ramps teacher structure weights over this many "
                                      "optimizer steps; 0 disables warmup",
                                 default=500)
        self.parser.add_argument("--teacher_structure_decay",
                                 type=float,
                                 help="final multiplier for teacher structure weights after "
                                      "warmup; 1 keeps the weight constant and 0 decays to zero",
                                 default=0.5)
        self.parser.add_argument("--teacher_gradient_loss",
                                 help="if set, compares student and teacher normalized "
                                      "disparity/log-inverse-depth gradients",
                                 action="store_true")
        self.parser.add_argument("--teacher_gradient_weight",
                                 type=float,
                                 help="weight for teacher anchored local gradient structure loss",
                                 default=0.01)
        self.parser.add_argument("--teacher_ranking_loss",
                                 help="if set, adds sparse pairwise ordinal consistency from "
                                      "the frozen RGB teacher",
                                 action="store_true")
        self.parser.add_argument("--teacher_ranking_weight",
                                 type=float,
                                 help="weight for sparse pairwise teacher ordinal/ranking loss",
                                 default=0.02)
        self.parser.add_argument("--teacher_rank_samples",
                                 type=int,
                                 help="number of random pixel pairs per image for teacher "
                                      "ordinal/ranking consistency",
                                 default=512)
        self.parser.add_argument("--teacher_confidence",
                                 help="if set, weights teacher losses by label-free "
                                      "teacher/student structure agreement",
                                 action="store_true")
        self.parser.add_argument("--teacher_confidence_threshold",
                                 type=float,
                                 help="normalized structure-difference scale used for teacher "
                                      "confidence and ranking-pair filtering",
                                 default=0.25)
        self.parser.add_argument("--teacher_texture_ambiguity_emphasis",
                                 help="if set, uses the Snapshot 04 RGB-only texture ambiguity "
                                      "map as a weak emphasis prior for teacher losses",
                                 action="store_true")
        self.parser.add_argument("--teacher_path",
                                 type=str,
                                 help="folder containing frozen RGB teacher encoder.pth and "
                                      "depth.pth weights",
                                 default="weights/lite-mono")
        self.parser.add_argument("--no_ssim",
                                 help="if set, disables ssim in the loss",
                                 action="store_true")
        self.parser.add_argument("--mypretrain",
                                 type=str,
                                 help="if set, use my pretrained encoder")
        self.parser.add_argument("--weights_init",
                                 type=str,
                                 help="pretrained or scratch",
                                 default="pretrained",
                                 choices=["pretrained", "scratch"])
        self.parser.add_argument("--pose_model_input",
                                 type=str,
                                 help="how many images the pose network gets",
                                 default="pairs",
                                 choices=["pairs", "all"])
        self.parser.add_argument("--pose_model_type",
                                 type=str,
                                 help="normal or shared",
                                 default="separate_resnet",
                                 choices=["posecnn", "separate_resnet", "shared"])

        # SYSTEM options
        self.parser.add_argument("--no_cuda",
                                 help="if set disables CUDA",
                                 action="store_true")
        self.parser.add_argument("--num_workers",
                                 type=int,
                                 help="number of dataloader workers",
                                 default=12)

        # LOADING options
        self.parser.add_argument("--load_weights_folder",
                                 type=str,
                                 help="name of model to load")
        self.parser.add_argument("--models_to_load",
                                 nargs="+",
                                 type=str,
                                 help="models to load",
                                 default=["encoder", "depth", "pose_encoder", "pose"])

        # LOGGING options
        self.parser.add_argument("--log_frequency",
                                 type=int,
                                 help="number of batches between each tensorboard log",
                                 default=250)
        self.parser.add_argument("--save_frequency",
                                 type=int,
                                 help="number of epochs between each save",
                                 default=1)

        # TRAINING-TIME DEPTH METRIC OPTIONS
        self.parser.add_argument("--depth_metric_crop",
                                 type=str,
                                 default="auto",
                                 choices=["auto", "kitti_eigen", "none"],
                                 help="crop used for training-time depth metric logging; "
                                      "'auto' uses KITTI Eigen crop for KITTI and no crop for Citrus")

        # EVALUATION options
        self.parser.add_argument("--disable_median_scaling",
                                 help="if set disables median scaling in evaluation",
                                 action="store_true")
        self.parser.add_argument("--pred_depth_scale_factor",
                                 help="if set multiplies predictions by this number",
                                 type=float,
                                 default=1)
        self.parser.add_argument("--ext_disp_to_eval",
                                 type=str,
                                 help="optional path to a .npy disparities file to evaluate")
        self.parser.add_argument("--eval_split",
                                 type=str,
                                 default="eigen",
                                 choices=[
                                    "eigen"],
                                 help="which split to run eval on")
        self.parser.add_argument("--save_pred_disps",
                                 help="if set saves predicted disparities",
                                 action="store_true")
        self.parser.add_argument("--no_eval",
                                 help="if set disables evaluation",
                                 action="store_true")
        self.parser.add_argument("--eval_out_dir",
                                 help="if set will output the disparities to this folder",
                                 type=str)
        self.parser.add_argument("--post_process",
                                 help="if set will perform the flipping post processing "
                                      "from the original monodepth paper",
                                 action="store_true")

    def parse(self):
        self.options = self.parser.parse_args()
        return self.options
