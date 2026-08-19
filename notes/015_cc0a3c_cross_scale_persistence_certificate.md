# Note 015 — CC0-A3C cross-scale persistence certificate

**Status:** executable GUI/instrument ready. Dense oracle only; no runtime speed claim.

## Why this exists

The first fixed-normalization webcam run (`CC0-A3B`) kept the important qualitative structure after removing A3's hidden framewise global normalization:

```text
raw change rate                 1.000000
spectral packet wake fraction   0.041860
spectral spatial fanout         0.285272
plain tile wake fraction        0.085963
plain tile spatial fanout       0.141399
cross-scale agreement           0.853757
mean bundle count               5.708
largest bundle share            0.605402
```

The spectral field is therefore not simply winning on spatial routing; plain tiles are still spatially sharper. The surviving interesting observation is that spectral wake activity often repeats at the same physical location across several neighboring scales.

The next question is:

> **Does cross-scale agreement predict that a local structure will persist?**

If yes, redundancy over scale may be useful as a local validity/confidence certificate even when it is not the cheapest raw spatial router.

---

## Instrument

Run:

```bat
run_cc0a3c_scale_certificate.bat
```

or:

```bat
python3.13 experiments\cc0a3c_scale_certificate_gui.py
```

A3C inherits the A3B fixed-normalization Gabor/tile census and adds a scale-multiplicity field.

For every physical `6 x 8` spatial cell:

```text
m(x,y) = number of spectral scales with at least one orientation that wakes
```

With six wavelengths, `m` lies in `0..6`.

The new primary visualization keeps physical x/y fixed:

```text
0 scales -> black
1 scale  -> weak/single-scale event
2..6     -> increasingly multi-scale event
```

A second panel shows the simple candidate certificate:

```text
m(x,y) >= 2
```

This replaces the potentially confusing A3/A3B side-by-side scale strip when asking whether several repeated strokes belong to one physical event.

---

## Killable prediction

For source multiplicity `m=1,2,...,6`, A3C measures whether future spectral wake exists at the same spatial cell or one neighboring cell after:

```text
1 frame
2 frames
4 frames
8 frames
```

The one-cell spatial allowance handles ordinary motion. It is fixed for the run and written into the receipt.

The prediction is:

```text
P(future local wake | multiplicity >= 2)
    >
P(future local wake | multiplicity = 1)
```

and, more strongly, persistence should tend to rise with multiplicity.

The GUI reports:

```text
lag   single-scale   multi-scale   delta(multi-single)   plain tiles
```

The plain tile mask gets the same one-cell future-local-wake measurement as an attacker.

Do not claim a win from one positive number. Useful evidence is a positive multi-minus-single delta across several lags with enough support cells, preferably repeated on more than one run/scene.

Kill/demote the certificate idea if:

```text
multi-scale events do not persist more than single-scale events
OR
any advantage vanishes beyond 1 frame
OR
support is too sparse to estimate reliably
OR
plain tile persistence explains the same effect more simply
```

---

## Saved receipt

Default folder:

```text
results/cc0a3c_scale_certificate_runs/
```

A save writes:

```text
cc0a3c_scale_certificate_YYYYMMDD_HHMMSS.txt
cc0a3c_scale_certificate_YYYYMMDD_HHMMSS.json
cc0a3c_scale_certificate_YYYYMMDD_HHMMSS.csv
cc0a3c_scale_certificate_YYYYMMDD_HHMMSS_trace.npz
```

The NPZ contains:

```text
packed full spectral wake tensor
packed tile wake tensor
full per-frame 6x8 multiplicity maps
spectral/tile shapes
wavelengths/orientations
persistence lags
```

The JSON contains the full persistence table including support counts for every multiplicity at every lag.

---

## First protocol

Use defaults and an ordinary webcam scene. Roughly 45–90 seconds is enough for a first look:

```text
quiet
raise/lower one hand
small hand motion
move hand laterally
move toward/away
large body motion
quiet
```

Do not tune the scene to produce high multiplicity.

The important GUI panel is now the fixed-x/y multiplicity map. If a hand edge is represented at several scales, it should appear as one higher-multiplicity spatial region rather than several repeated scale strips.

---

## Boundary

A3C still computes the entire Gabor bank densely every frame. It does not yet route sparsely, skip filters, or prove a speed advantage.

The possible systems use, if the prediction survives, is narrower:

> **Cross-scale agreement may provide a cheap local certificate for which persistent consequences deserve to remain active or trusted longer.**

That certificate would still need to beat simpler spatial/temporal alternatives in a matched task/runtime experiment.
