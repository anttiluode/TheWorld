# TheWorld — CC0-A2 webcam GUI handoff

**Date:** 2026-08-19

## State

CC0-A1 found a receiver-local invalidation opportunity on simple encoded visual streams. That was not enough to justify CC0-B.

The repo now has a live webcam instrument for CC0-A2:

```text
experiments/cc0a_webcam_gui.py
run_cc0a_webcam.bat
notes/012_cc0a2_webcam_gui.md
```

The GUI reuses the exact CC0-A1 receiver definitions and cache/tolerance logic rather than inventing a separate demo.

## What is ready

Live display:

```text
camera preview
raw frame change rate
ANY receiver invalid rate
receiver-slot invalid fraction
GLOBAL-OR / oracle-local opportunity ratio
current per-receiver WAKE/valid state
per-receiver wake rate
per-receiver distance/tolerance ratio
```

Receipt export:

```text
JSON summary
text summary
per-frame invalidation + receiver-distance CSV
optional raw MJPG webcam AVI
```

Default output:

```text
results/cc0a_webcam_runs/
```

Settings are locked while collecting so one receipt cannot silently mix tolerance scales.

## Validation already done

`python cc0a_webcam_gui.py --self-test` was run against the existing census receiver functions in the working environment.

Receipt:

```text
CC0-A webcam GUI self-test PASS
frames=80 raw=1.0000 any=0.8987 local=0.1715
```

This validates plumbing/cache/statistics execution only. It is not CC0-A2 evidence.

## Next human action

Run:

```bat
run_cc0a_webcam.bat
```

Recommended first session:

```text
tolerance scale = 0.35
~1 minute ordinary webcam scene
left-hand movement
right-hand movement
forward/back movement
partly leave/return to frame
lighting change if convenient
some intentional quiet time
```

Then press `Save receipt`.

Repeat at tolerance scale `0.15` and `0.75` if the first run is technically clean.

## Gate

A useful CC0-A2 result requires the real stream to show the qualitative separation:

```text
input changes often
BUT
most individual receiver consequences remain valid
AND
wake events address a small receiver subset
```

If the webcam invalidation matrix becomes dense, do not build CC0-B for this receiver set.

If the sparsity gap survives, then CC0-B can finally attack the hard question: whether cheap guards and local routing can exploit the oracle opportunity after paying the full wall-clock/memory/control-plane bill.

> **A1 says the opportunity is measurable. The webcam GUI makes A2 runnable. Only the saved real-stream receipt can say whether A2 passes.**
