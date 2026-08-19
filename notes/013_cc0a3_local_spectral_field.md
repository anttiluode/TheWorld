# Note 013 — CC0-A3 local spectral field demo

**Status:** executable instrument ready. This is a dense oracle/locality demo, not a sparse-runtime speed result and not a claim that spectral packets beat ordinary spatial processing.

## Question

The Sigh-image slider showed a visually continuous reorganization of one image as a narrow radial frequency band moved from near-Nyquist checker structure through curved/moiré-like interference toward low-frequency gist.

The useful systems question is narrower:

> **Can a real visual stream be represented in coordinates where change is locally addressable in space × scale × time, so most of the persistent state does not need touching?**

This is a direct attack on the `DifferentMachine` requirement that relevance be locally discoverable and the `CC0` requirement that receiver consequences may remain valid while raw input changes.

## Instrument

`experiments/cc0a3_local_spectral_field_gui.py`

Pipeline:

```text
webcam / video
    ↓
grayscale reduced image
    ↓
localized quadrature Gabor bank
    6 wavelengths × 4 orientations
    ↓
6 × 8 spatial pooling lattice
    ↓
1152 localized spectral packets
    ↓
independent cached consequence per packet
    ↓
packet invalidation + space/scale bundle census
```

Each packet is an oracle measurement with an address approximately

```text
(scale, orientation, spatial-cell-y, spatial-cell-x)
```

The current implementation computes the whole bank densely every frame. A packet is marked WAKE only when its current normalized energy has moved outside a tolerance region around its last accepted cached value.

That tells us which packet computations **could** have slept if a cheap router/guard existed. It does not yet provide the cheap router.

## Mandatory attacker in the same window

A deliberately boring baseline is evaluated on the same stream:

```text
plain spatial grid
    channel 0 = cell mean intensity
    channel 1 = cell Sobel edge energy
```

The GUI reports its cache invalidation fraction beside the spectral field.

Do not celebrate a visually beautiful spectral field if the ordinary tile representation is at least as selective for less state/cost.

## Live measurements

The GUI shows:

```text
raw input change rate
spectral packet wake fraction
spectral spatial routing fanout
plain tile wake fraction
adjacent-scale spatial agreement
active space×scale bundle count
largest active bundle share
```

Definitions:

- **spectral packet wake fraction** — fraction of all `(scale, orientation, y, x)` packets crossing their cache tolerance.
- **spatial routing fanout** — fraction of image-grid cells that contain at least one invalid spectral packet. This is closer to the candidate-discovery bill than packet sparsity alone.
- **cross-scale agreement** — mean spatial correlation between adjacent scale-energy maps after collapsing orientation. It is a crude first test of whether neighboring scales form related structure.
- **bundle** — connected component after collapsing orientation, with adjacency through spatial 4-neighbors and neighboring scales. This tests whether invalidations form a few coherent local objects/sheets rather than salt-and-pepper global activity.

## GUI

Run on Windows:

```bat
run_cc0a3_spectral_field.bat
```

or:

```bat
python3.13 experiments\cc0a3_local_spectral_field_gui.py
```

The window can use either a webcam or a video file.

Controls:

```text
Camera
Spectral tolerance
Tile tolerance
Analysis width
View scale
Start webcam
Load video
Stop
Reset
Save receipt
```

`View scale` only changes the visualization. It does not change the measurement.

Default bank:

```text
wavelengths ≈ 4, 6.5, 10, 15.5, 24, 36 analysis pixels
orientations = 0°, 45°, 90°, 135°
grid = 6 × 8
analysis width = 128
```

## Saved receipt

Default folder:

```text
results/cc0a3_spectral_field_runs/
```

Each save writes:

```text
cc0a3_spectral_field_YYYYMMDD_HHMMSS.txt
cc0a3_spectral_field_YYYYMMDD_HHMMSS.json
cc0a3_spectral_field_YYYYMMDD_HHMMSS.csv
cc0a3_spectral_field_YYYYMMDD_HHMMSS_wake_trace.npz
```

The compressed NPZ stores the packed full spectral and tile wake matrices plus the tensor shapes, wavelengths and orientations. This is the important file if we later want to inspect cluster geometry instead of trusting GUI averages.

## First protocol

Use the same ordinary room/webcam situation as CC0-A2. Do not stage the scene to help the spectral representation.

Suggested sequence, about 45–90 seconds:

```text
quiet / ordinary camera noise
left-side hand motion
right-side hand motion
move toward and away from camera
small fine object motion
large body motion
brief lighting change if convenient
quiet again
```

First use the defaults. Save the receipt.

Then attack spectral tolerance rather than tuning for a pretty number. Useful repeats:

```text
0.20
0.35
0.60
```

The tile tolerance is not mathematically commensurate with the spectral tolerance, so **raw wake fractions alone are not a fair winner test yet**. The first purpose is to inspect locality, clustering and scale continuity. A later matched-quality/matched-false-miss calibration is required before claiming one representation is more efficient.

## Pass / kill interpretation

Interesting pattern:

```text
raw input changes often
AND
spectral packet wake fraction is low
AND
spatial routing fanout is materially lower than 1
AND
activity forms a few coherent space×scale bundles
AND
adjacent scales show reproducible relationship
```

Stronger result:

```text
spectral representation gives better task/receiver selectivity per touched state
than plain spatial tiles after thresholds are fairly calibrated
```

Kill / demote the spectral story if:

```text
spectral spatial fanout stays near 1 on ordinary motion
OR
active packets are globally salt-and-pepper
OR
cross-scale structure is weak/unstable
OR
plain tiles provide the same routing selectivity more cheaply
```

Even a kill can leave the larger CC0 idea intact; it would only say that localized spectral coordinates are not the useful routing geometry for this substrate.

## Self-test

```bat
python3.13 experiments\cc0a3_local_spectral_field_gui.py --self-test
```

The self-test checks shapes/cache plumbing on a synthetic moving-bar stream. It is not evidence for the hypothesis.

## Carry-forward sentence

> **The Sigh slider does not need to reveal a hidden brain code. It only needs to suggest a coordinate geometry in which visual consequences remain local enough that change can be routed instead of recomputed globally.**
