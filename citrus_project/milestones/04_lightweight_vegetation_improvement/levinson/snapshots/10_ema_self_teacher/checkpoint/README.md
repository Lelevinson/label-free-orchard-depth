# Snapshot 10 inference weights (the WIN)

`weights_29/encoder.pth` + `weights_29/depth.pth` are the selected final checkpoint of the
S10 EMA-self-teacher 30-epoch run. RGB-only, single-image Lite-Mono inference (the EMA teacher,
pose net, and all training-only parts are NOT needed and not included). Test median-scaled:
abs_rel=0.3080, a1=0.6258 — beats original Lite-Mono on both metrics. Load like any Lite-Mono
checkpoint (the full run folder is local/ignored; these copies are the durable record).
