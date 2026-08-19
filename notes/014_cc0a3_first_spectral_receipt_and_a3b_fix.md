# Note 014 — CC0-A3 first webcam receipt, attacker, and A3B correction

**Date:** 2026-08-19  
**Status:** first real localized spectral-field receipt is interesting but normalization-confounded. A corrected `A3B` instrument is now the hard rerun.

## First receipt

User ran the default CC0-A3 webcam GUI for 335 frames / 334 steady steps.

```text
raw change rate             1.000000
spectral packet wake frac   0.058144
spectral spatial fanout     0.301148
plain tile wake frac        0.062157
ANY spectral wake rate      0.850299
cross-scale agreement       0.879239
mean bundle count           4.707
largest bundle share        0.548387
```

The raw stream changed every measured step, but an individual spectral packet crossed its cache tolerance on only ~5.8% of opportunities.

This immediately recreates the `invalidation OR catastrophe` pattern at a larger receiver count: with 1152 packets, *some* spectral packet is invalid on ~85% of frames even though individual packet invalidation is sparse. A useful runtime therefore cannot use one global spectral alarm; it needs local candidate discovery.

## Wake-trace archaeology

The packed wake trace was unpacked as:

```text
spectral tensor  : 6 scales x 4 orientations x 6 x 8 spatial cells = 1152 packets
tile tensor      : 2 channels x 6 x 8 spatial cells = 96 states
```

Steady-state means:

```text
spectral packets touched/frame       66.98 / 1152
spectral spatial cells addressed     14.46 / 48   = 30.11%
plain tile states touched/frame       5.97 / 96
plain tile spatial cells addressed    4.67 / 48   =  9.73%
```

So the first attacker result is uncomfortable:

> **At the chosen thresholds, spectral packet sparsity does not buy spatial routing sparsity. Plain tiles address about one third as many spatial cells.**

Do not call tiles the task winner yet. The spectral and tile thresholds are not calibrated to matched task error / miss rate, and spectral states carry scale/orientation information that the two-channel tile baseline does not. But for the narrow routing bill, the burden is now on the spectral representation.

## Cross-scale result survived

Per-scale packet wake fractions were fairly flat:

```text
wavelength 4.0      0.0492
wavelength 6.5      0.0530
wavelength 10.0     0.0558
wavelength 15.5     0.0640
wavelength 24.0     0.0671
wavelength 36.0     0.0599
```

After collapsing orientation, adjacent-scale wake-map Jaccards were about:

```text
0.482, 0.455, 0.467, 0.487, 0.460
```

Conditional overlap was roughly `0.60 -> 0.68`: when a spatial location was active at one scale, the same location was often also active at a neighboring scale.

Combined with mean observation-level cross-scale agreement `0.879`, this says the scale axis is not behaving like six unrelated channels. There is real redundant/coherent structure to compress or route as bundles.

The activity was also bursty:

```text
mean active spectral packets/frame    66.98
median                                 10
90th percentile                       251.7
```

So most frames are much quieter than the mean, with occasional broad bursts.

## Instrument flaw discovered

A3 used:

```python
q = quantile(channel_map, 0.95)
normalized_map = channel_map / q
```

**on every frame**.

That is wrong for a locality census.

A local visual event can change the channel's global `q95`, which then rescales values in spatial cells that did not receive the local event. The measurement itself introduces a global dependency and can inflate apparent spatial fanout.

The plain tile edge channel used the same framewise normalization, but spectral used it for all 24 scale/orientation maps, so the confound can hurt spectral locality much more strongly.

## A3B correction

New instrument:

```text
experiments/cc0a3b_local_spectral_field_fixednorm_gui.py
run_cc0a3b_spectral_field.bat
```

A3B keeps the same Gabor bank, cache logic, spatial lattice, bundles and tile attacker, but:

```text
first frame:
    estimate one q95 scale for each (scale, orientation) channel
    freeze it

all later frames:
    use the same frozen channel scale
```

The tile edge scale is frozen the same way.

Therefore a later local event cannot globally renormalize unrelated cells.

A3B also exposes **tile spatial routing fanout** directly beside spectral spatial fanout, because state wake fraction alone hid the most important attacker result.

Reset starts a fresh first-frame calibration.

## Next run

Use defaults first, same ordinary webcam protocol:

```text
spectral tolerance 0.35
tile tolerance     0.08
analysis width     128
```

Run 45–90 seconds and save the receipt.

Main comparison:

```text
A3 spectral spatial fanout     0.301  (confounded)
A3 tile spatial fanout         0.097  (derived from wake trace)
A3B spectral spatial fanout    ???
A3B tile spatial fanout        ???
```

If corrected spectral fanout stays around `0.30` while tiles stay around `0.10`, naive localized spectral packet routing is demoted/killed for this substrate.

If spectral fanout collapses materially after removing global normalization while cross-scale bundle structure survives, then the earlier poor locality was partly an instrument artifact and the bundle-compression route remains live.

## Carry-forward

> **A3 found two things at once: scale-space structure is coherent, but naive overcomplete spectral packets are expensive to address. A3B asks whether that cost is real or partly caused by our own globally coupled normalization.**
