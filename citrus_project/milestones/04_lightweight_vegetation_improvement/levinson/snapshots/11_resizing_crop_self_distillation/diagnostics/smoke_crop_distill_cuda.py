"""S11 CUDA smoke (3 training steps, NOT a training run).

Loads the S10 full run's saved opt.json (exact same recipe/flags), enables
--crop_self_distillation, forces the EMA+crop branches active, and runs 3 full
optimizer steps at batch 12 on CUDA. Reports: all loss components (finite?),
crop_distill diagnostics, and peak VRAM (the go/no-go number for batch 12).

Usage: python smoke_crop_distill_cuda.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402

OPT_JSON = (REPO_ROOT / "citrus_project" / "milestones"
            / "04_lightweight_vegetation_improvement" / "levinson" / "runs"
            / "s10_ema_self_teacher_b12_30ep_seed0" / "models" / "opt.json")


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--subbatch", type=int, default=0,
                     help="crop_distill_subbatch to test (0 = full batch)")
    cli.add_argument("--downsample", type=int, default=1,
                     help="crop_view_downsample to test (1 or 2)")
    cli_args = cli.parse_args()

    with OPT_JSON.open(encoding="utf-8") as fp:
        opt_dict = json.load(fp)

    opt_dict.update(
        model_name="s11_smoke_tmp",
        num_epochs=1,
        num_workers=2,
        # S11 under test:
        crop_self_distillation=True,
        crop_distill_subbatch=cli_args.subbatch,
        crop_view_downsample=cli_args.downsample,
        # force EMA (and therefore the crop branch) active from the first step:
        ema_start_step=1,
    )
    opts = argparse.Namespace(**opt_dict)

    from trainer import Trainer  # noqa: E402  (after sys.path insert)

    trainer = Trainer(opts)
    trainer.set_train()
    trainer.step = 10  # > ema_start_step, inside warmup ramp

    loader = iter(trainer.train_loader)
    for step_i in range(3):
        if step_i == 1:
            torch.cuda.reset_peak_memory_stats()
        inputs = next(loader)
        outputs, losses = trainer.process_batch(inputs)
        trainer.model_optimizer.zero_grad()
        if trainer.use_pose_net:
            trainer.model_pose_optimizer.zero_grad()
        losses["loss"].backward()
        trainer.model_optimizer.step()
        if trainer.use_pose_net:
            trainer.model_pose_optimizer.step()
        trainer.update_ema()
        trainer.step += 1

        print(f"\n--- step {step_i} ---")
        for key in sorted(str(k) for k in losses):
            pass
        for key, value in losses.items():
            name = key if isinstance(key, str) else "/".join(str(p) for p in key)
            if isinstance(name, str) and ("crop_distill" in name or "ema_distill" in name
                                          or name == "loss"):
                v = float(value)
                flag = "" if torch.isfinite(torch.tensor(v)) else "  <-- NOT FINITE"
                print(f"  {name}: {v:.6f}{flag}")

    alloc = torch.cuda.max_memory_allocated() / (1024 ** 2)
    reserved = torch.cuda.max_memory_reserved() / (1024 ** 2)
    print(f"\npeak VRAM (steps 2-3): allocated {alloc:.0f} MiB, reserved {reserved:.0f} MiB")
    print("batch size:", opts.batch_size)
    print("VERDICT:", "batch 12 HOLDS" if reserved < 7900 else
          "TIGHT/SPILL — consider --crop_distill_subbatch 6 or batch 10")


if __name__ == "__main__":
    main()
