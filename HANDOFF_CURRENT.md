# TheWorld — current handoff

**Date:** 2026-08-19  
**State:** receiver-aware self-adjusting execution / “compile the math out of the hot loop.” Real webcam opportunity receipts now exist. The current branch is testing whether **cross-scale agreement can act as a local persistence certificate**, not whether Gabor packets themselves are a speed win. No novelty claim.

Current files:

- `notes/009_compile_math_out_of_hot_loop.md`
- `notes/010_invalidation_or_catastrophe.md`
- `notes/011_cc0a_first_receipt.md`
- `notes/012_cc0a2_webcam_gui.md`
- `notes/013_cc0a3_local_spectral_field.md`
- `notes/015_cc0a3c_cross_scale_persistence_certificate.md`
- `experiments/cc0a_invalidation_census.py`
- `experiments/cc0a_webcam_gui.py`
- `experiments/cc0a3_local_spectral_field_gui.py`
- `experiments/cc0a3b_local_spectral_field_fixednorm_gui.py`
- `experiments/cc0a3c_scale_certificate_gui.py`
- `results/2026-08-19_cc0a2_webcam_receipt.txt`
- `results/2026-08-19_cc0a3b_fixednorm_webcam_receipt.txt`

---

## One-line state

> **The world changing is not the computational event. A receiver consequence becoming invalid is the event; cross-scale agreement is now being tested as one possible local certificate for whether a visual consequence deserves to persist.**

The broader decomposition remains:

```text
TheClutch2 / Fusion1      validity sparsity
DifferentMachine          causal-frontier sparsity
SplatNeuron               receiver sparsity
KYY/TWC/Arbors/ArborVerb  operator lowering
```

The unearned part is still end-to-end combination with honest control-plane cost.

---

# Receipts so far

## CC0-A1 — encoded video opportunity

On a 901-frame rotating-globe clip at tolerance scale `0.35`:

```text
raw frame changed              100.00%
ANY receiver invalid            12.44%
receiver slots invalid/frame     1.202%
GLOBAL-OR / oracle-local work    10.35x
```

This was an oracle skip-opportunity result only.

## CC0-A2 — first real webcam receiver census

```text
frames                         297
raw change rate                1.000000
ANY receiver invalid           0.422297
receiver-slot wake fraction    0.158170
GLOBAL-OR/local opportunity     2.670x
```

So receiver-relative invalidation remained sparser than raw camera change on a real sensor stream.

## CC0-A3/A3B — localized spectral field + tile attacker

A3 introduced a 6-scale × 4-orientation localized Gabor bank pooled to a 6×8 spatial grid. A3's framewise q95 normalization accidentally created a hidden global dependency, so A3B fixed one normalization scale per spectral channel from the first frame.

First A3B webcam receipt:

```text
raw change rate                 1.000000
spectral packet wake fraction   0.041860
spectral spatial fanout         0.285272
plain tile wake fraction        0.085963
plain tile spatial fanout       0.141399
cross-scale agreement           0.853757
mean bundle count               5.708
largest bundle share            0.605
```

Interpretation:

- individual spectral packets are sparse inside the large 1152-state representation;
- however plain spatial tiles are currently much sharper spatial routers (~14% vs ~29% fanout);
- therefore **naive Gabor packet routing is not presently winning**;
- the strong surviving observation is repeated activity at the same physical location across several scales.

The spectral story is therefore demoted from “packets may be a better router” to:

> **Cross-scale redundancy may be a local persistence/validity signal.**

---

# Main next gate — CC0-A3C

`experiments/cc0a3c_scale_certificate_gui.py`

Run:

```bat
run_cc0a3c_scale_certificate.bat
```

A3C keeps physical x/y fixed and computes

```text
m(x,y) = number of spectral scales that wake at this cell
```

with `m in 0..6`.

The GUI now shows:

```text
cross-scale multiplicity map at fixed x,y
>=2-scale certificate map
plain tile wake map
selected spectral scale
live persistence table
```

### Killable prediction

For source events of multiplicity 1,2,...,6, measure whether future spectral wake exists at the same spatial cell or one neighboring cell after:

```text
1, 2, 4, 8 frames
```

The primary comparison is:

```text
P(future local wake | multiplicity >= 2)
vs
P(future local wake | multiplicity = 1)
```

A useful certificate should produce a positive multi-minus-single persistence delta across several lags with enough support. Stronger evidence would show persistence increasing with multiplicity.

Plain tiles receive the same future-local-wake measurement as an attacker.

### Kill lines

Demote/kill the cross-scale certificate if:

```text
multi-scale wake does not persist more than single-scale wake
OR
advantage exists only at 1 frame and disappears immediately
OR
support counts are too small
OR
plain tile temporal persistence explains the same effect more simply
```

Even a kill here does not kill CC0; it only kills this proposed visual certificate.

---

## Important boundary

A3/A3B/A3C are still **dense oracle instruments**. The entire Gabor bank and tile baseline run every frame.

No claim yet of:

```text
runtime speedup
GPU win
energy win
learned sparse routing
brain mechanism
```

The systems gate after any successful certificate result remains:

```text
cheap guard / candidate discovery
 -> local routing
 -> persistent receiver state
 -> real skipped work
 -> actual CPU/GPU wall-clock comparison
```

against FULL, make/dependency invalidation, raw delta, global Clutch, plain tiles, tiny always-on GRU/SSM/MLP, and serious incremental/delta baselines.

---

## Carry-forward sentence

> **The packet may not be the useful unit. The candidate unit is now a persistent cross-scale bundle: several spectral manifestations at one place whose agreement may predict that the underlying consequence deserves to stay alive.**
