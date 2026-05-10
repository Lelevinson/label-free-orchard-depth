# Plain Lite-Mono Citrus Baseline Inference Weights

These are the inference-only weights from the final epoch of the plain Lite-Mono Citrus baseline.

Source checkpoint:

```text
citrus_project/milestones/04_lightweight_vegetation_improvement/runs/plain_litemono_citrus_imagenet_pretrain_b12_30ep_lr1e-4/models/weights_29/
```

Included:

- `encoder.pth`
- `depth.pth`

Not included:

- pose-network weights
- optimizer states
- earlier epoch checkpoints

Recipe summary:

- Lite-Mono trained on the prepared Citrus dataset
- initialized from the Lite-Mono ImageNet encoder pretrain
- batch size 12
- 30 epochs
- input size 640x192
- monocular temporal self-supervised training frames `[0, -1, 1]`

The full training run folder is intentionally ignored by git because it contains many large checkpoints and optimizer files.
