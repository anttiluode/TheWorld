# Note 011 — CC0-A1 first receipt: receiver invalidation is sparse on simple encoded video

**Status:** positive opportunity/instrument receipt on pre-existing encoded visual streams; **not** a runtime speedup, not a natural-world result, not a novelty claim.  
**Date:** 2026-08-19

## 0. Question

`notes/010_invalidation_or_catastrophe.md` proposed a cheap pre-gate before building a receiver-aware runtime:

> **When the observed world changes, do most individual receiver consequences actually remain valid?**

If the answer is no, there is no reason to build receiver-local sleeping. If the answer is yes, the next question is whether a cheap guard/router can exploit the oracle sparsity.

This experiment measures only the first question.

---

## 1. Instrument

`experiments/cc0a_invalidation_census.py` takes an ordinary encoded video and deliberately runs an **oracle dense census**.

Every frame is processed. Eleven small receivers are evaluated densely:

```text
appearance: global_gist, center_gist, left_gist, right_gist, periphery_gist
structure:  global_edge, bottom_edge
geometry:   light_centroid
motion:     left_motion, right_motion, bottom_motion
```

Each receiver keeps its last accepted output. On frame `t`, the dense oracle computes the new output `y_i(t)` and compares it with that receiver's cached value `c_i`:

```text
if distance(y_i(t), c_i) > epsilon_i:
    receiver i is INVALID
    c_i <- y_i(t)
else:
    receiver i remains VALID
```

The comparison is against the **cached consequence**, not merely the previous frame. Small changes can therefore accumulate until they cross a receiver's tolerance boundary.

The experiment records raw frame MAE, the OR of all receiver invalidations, the fraction of receiver slots invalidated per frame, the full binary invalidation matrix and pairwise invalidation correlations.

The oracle is intentionally wasteful. It computes every receiver in order to label which computations a hypothetical correct runtime could have skipped. **The census itself saves no compute.**

---

## 2. Source streams

The execution container already contained three encoded MP4 assets in the installed Gradio package. They were used because they were byte-accessible without inventing a synthetic stream or touching `WorldModel` while its training experiment was running.

```text
world.mp4  901 frames  480x270  30 fps
SHA256 71944d7430c461f0cd6e7fd10cee7eb72786352a3678fc7bc0ae3d410f72aece

b.mp4      150 frames  480x270  30 fps
SHA256 fc7e05ed802c94d74e9005e3bc53d5abfd36ab4b63be1602f6cfe697b789c418

a.mp4      209 frames  1920x1080 30 fps
SHA256 a6f96e13dfd69423d1c6cc883d6d0886fd8ae5c69f5a87661c5698ce8bf991b5
```

Visual inspection: `world.mp4` and `b.mp4` are rotating rendered-globe clips on a dark background; `a.mp4` is a sparse title/outro animation.

These are **simple rendered media**, not a natural driving stream, DVS recording, or WorldSplat state sequence. That limitation is load-bearing.

---

## 3. Main receipt — `world.mp4`

At tolerance scale `0.35`, excluding the mandatory first-frame acquisition:

```text
raw frame changed                 1.0000
ANY receiver invalid             0.1244
mean receivers invalid/frame     0.1322 / 11
receiver-slot invalid fraction   0.01202
```

Per-receiver invalidation rates:

```text
periphery_gist       0.0000
left_motion          0.0000
right_motion         0.0000
bottom_motion        0.0000
global_edge          0.0022
bottom_edge          0.0022
light_centroid       0.0144
global_gist          0.0178
left_gist            0.0200
right_gist           0.0233
center_gist          0.0522
```

Under a deliberately simple **equal receiver-cost** thought experiment:

```text
GLOBAL OR:
  if ANY receiver invalid -> execute all 11 receivers

ORACLE LOCAL:
  execute only receivers whose cached consequence crossed tolerance
```

receiver execution fractions are:

```text
global OR     0.12444
oracle local  0.01202
```

so

```text
global-OR receiver work / oracle-local receiver work = 10.35x
```

This is an **opportunity ratio**, not measured speedup. Guard, routing, metadata, queueing and refresh costs are all zero in this oracle calculation.

---

## 4. Tolerance sweep — do not cherry-pick epsilon

The same fixed receiver definitions were swept over a ~6.7x tolerance range.

### `world.mp4`

```text
scale   raw change   ANY invalid   local slot frac   global-OR/local
0.15      1.0000       0.3156          0.03242            9.73x
0.25      1.0000       0.1811          0.01818            9.96x
0.35      1.0000       0.1244          0.01202           10.35x
0.50      1.0000       0.0744          0.00727           10.24x
0.75      1.0000       0.0422          0.00384           11.00x
1.00      1.0000       0.0156          0.00141           11.00x
```

The absolute wake rate is tolerance-dependent, as it must be. The more useful observation is that the **global-OR/local work gap remains about 9.7–11x across the sweep**.

### `b.mp4`

```text
scale   raw change   ANY invalid   local slot frac   global-OR/local
0.15      1.0000       0.3020          0.03051            9.90x
0.25      1.0000       0.1611          0.01586           10.15x
0.35      1.0000       0.1074          0.00976           11.00x
0.50      1.0000       0.0470          0.00427           11.00x
0.75      1.0000       0.0268          0.00244           11.00x
1.00      1.0000       0.0067          0.00061           11.00x
```

### `a.mp4`

The sparse title animation is qualitatively different and gives a smaller but still nontrivial gap:

```text
scale   raw change   ANY invalid   local slot frac   global-OR/local
0.15      0.2548       0.2933          0.10927            2.68x
0.25      0.2548       0.2452          0.05988            4.09x
0.35      0.2548       0.1731          0.04458            3.88x
0.50      0.2548       0.1298          0.03278            3.96x
0.75      0.2548       0.1490          0.02622            5.68x
1.00      0.2548       0.0721          0.01792            4.02x
```

So the instrument is not hard-coded to manufacture an 11x ratio on every stream.

---

## 5. What passed

The weak CC0-A opportunity condition is visible on the globe stream:

```text
raw visual state changes essentially every frame
BUT
most individual receiver consequences remain inside their cached tolerance
AND
invalidations are usually receiver-specific rather than wake-everybody events
```

So:

> **CC0-A1 instrument/opportunity gate: PASS on these simple encoded streams.**

This pass only earns a more realistic experiment.

---

## 6. What did not pass / what is not claimed

Do **not** report:

```text
83x faster AI
10x runtime speedup
real-world visual result
learned receiver geometry
natural event sparsity
GPU efficiency
energy efficiency
```

Why not:

1. The oracle computes all receiver outputs densely to label invalidations.
2. No cheap guard exists yet.
3. No local routing/index cost is paid.
4. Receiver costs are not actually equal.
5. Receiver definitions and tolerances are hand specified.
6. The globe/title streams are simple rendered media.
7. Several motion receivers are nearly/fully inactive on the globe clip, which helps sparsity but may not reflect a useful deployed task.
8. No compact always-on GRU/SSM/delta baseline has been timed yet.

The tempting `always-on/local = 83.2x` number at scale `0.35` is therefore kept only as bookkeeping inside the machine-readable output. It is **not a headline**.

---

## 7. Next gate — CC0-A2, not CC0-B yet

Before spending effort on a compiled guard/runtime, repeat the same census on a stream where locality and task consequences come from a real external process.

Preferred order:

```text
1. NeuromorphicDVSplusEMDfield / webcam or recorded real motion
   receivers: left/right motion, tracked-object continuity, occupancy/risk

2. driving / outdoor video
   receivers: near-field occupancy, route obstruction, motion clusters

3. WorldSplat after the current ray-fix run finishes
   receivers: collision/near-depth, motion, object continuity, RGB/appearance control
```

Keep the receiver oracle dense in CC0-A2. First establish that the **opportunity** survives a real stream.

Only then build CC0-B:

```text
oracle invalidation matrix
       ↓
cheap learned/derived guards
       ↓
locally discoverable candidate receivers
       ↓
actual sparse runtime
       ↓
wall-clock + memory-traffic attack
```

---

## Carry-forward sentence

> **On simple continuously changing visual streams, receiver consequences can be far sparser than raw change: the first census found a robust ~10x gap between “wake everybody if anything changed” and oracle receiver-local invalidation. The next job is to see whether that gap survives a real visual stream before claiming any compute win.**
