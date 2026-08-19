# TheWorld handoff — CC0-A3D persistent certificate tracker

**Date:** 2026-08-19

## Current state

A3C produced the first positive cross-scale persistence receipt on a real webcam stream. Multi-scale (`>=2` scales) wake predicted future local wake better than one-scale wake at 1/2/4/8 frames, while the plain tile baseline remained spatially sharper.

Therefore the spectral-packet-as-router story remains demoted. The active question is now:

> **Can a multi-scale certificate be collapsed into a small persistent local state whose downstream receiver mostly REUSEs/HOLDs and only WAKEs on meaningful changes?**

## A3D

Files:

```text
experiments/cc0a3d_certificate_tracker_gui.py
run_cc0a3d_certificate_tracker.bat
notes/016_cc0a3d_persistent_certificate_tracker.md
results/2026-08-19_cc0a3c_scale_certificate_receipt.txt
```

A3D takes the fixed A3C certificate:

```text
multiplicity(x,y) >= 2
```

forms connected blobs on the 6x8 lattice and gives them tiny persistent track state.

State machine:

```text
SUPPORTED  current certificate evidence
REUSE      supported and consequence stable
HOLD       evidence absent, state retained <=4 frames
WAKE       NEW / UPDATE / REACQUIRE / EXPIRE
```

`HOLD` is explicitly not counted as evidence. Held-only spatial fanout is measured separately.

A plain tile mask gets the same tracker as an attacker.

## What to inspect in the first run

```text
certificate current fanout
certificate belief fanout
certificate held-only fanout
certificate receiver WAKE fraction
track create/expire/reacquire churn
mean/max track age

tile current fanout
tile belief fanout
tile receiver WAKE fraction
```

A useful result requires more than low WAKE fraction. The certificate tracker must not achieve persistence merely by retaining large unsupported regions, and it should show some advantage over the tile tracker.

## Kill lines

```text
tile tracker equal/better at lower fanout -> spectral certificate runtime story loses
held-only fanout large -> HOLD is just hallucinated occupancy
track churn high -> local state not stable
WAKE near every decision -> no event sparsity
benefit disappears with hold_frames=0/1 -> persistence mostly hand-coded latch
```

If the default run looks positive, attack `--hold-frames 0`, `1`, `4`, `8` before making a claim.

## Boundary

A3D still computes both visual front ends densely every frame. It is an oracle control-plane experiment, not CC0-B sparse execution and not a speed result.

## Carry-forward

> **Evidence can disappear while state remains resident, but the ledger must mark the difference. The next thing to earn is that this held local state reduces downstream updates without becoming a larger, sloppier world than the simple tile attacker.**
