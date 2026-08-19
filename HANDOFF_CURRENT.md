# TheWorld — current handoff

**Date:** 2026-08-19  
**State:** receiver-aware self-adjusting execution / “compile the math out of the hot loop.” Real webcam receipts now support a narrow persistence-certificate result. The dense spectral field is **not** winning as the runtime body. No novelty or speed claim.

## One-line state

> **Use the cheapest geometry to address a change, a richer local test to decide whether it deserves persistence, and wake downstream computation only when the persistent consequence itself becomes invalid.**

## Current files

```text
notes/009_compile_math_out_of_hot_loop.md
notes/010_invalidation_or_catastrophe.md
notes/011_cc0a_first_receipt.md
notes/012_cc0a2_webcam_gui.md
notes/013_cc0a3_local_spectral_field.md
notes/015_cc0a3c_cross_scale_persistence_certificate.md
notes/016_cc0a3d_persistent_certificate_tracker.md
notes/017_a3d_result_router_certificate_separation.md

experiments/cc0a_invalidation_census.py
experiments/cc0a_webcam_gui.py
experiments/cc0a3_local_spectral_field_gui.py
experiments/cc0a3b_local_spectral_field_fixednorm_gui.py
experiments/cc0a3c_scale_certificate_gui.py
experiments/cc0a3d_certificate_tracker_gui.py

results/2026-08-19_cc0a2_webcam_receipt.txt
results/2026-08-19_cc0a3b_fixednorm_webcam_receipt.txt
results/2026-08-19_cc0a3d_certificate_tracker_receipt.txt

HANDOFF_2026-08-19_CC0A3D.md
```

## Receipts

### CC0-A2 — receiver-relative invalidation survives a real webcam

```text
frames                         297
raw change rate                1.000
ANY receiver invalid           0.422
receiver-slot wake fraction    0.158
GLOBAL-OR/local opportunity     2.67x
```

This established the basic phenomenon on a real sensor: raw world change is much denser than receiver-relevant change.

### CC0-A3B — spectral representation does not earn routing

Fixed-normalization webcam receipt:

```text
spectral packet wake fraction   .0419
spectral spatial fanout         .2853
plain tile spatial fanout       .1414
cross-scale agreement           .8538
```

Conclusion:

```text
Gabor/spectral packets as primary router: DEMOTED
cross-scale structure:                    SURVIVES
```

### CC0-A3C — first persistence certificate receipt

Multi-scale (`>=2` scales) local wake was more likely than single-scale wake to remain locally active later:

```text
lag    single    multi    delta
1f      .887      .969    +.082
2f      .859      .953    +.094
4f      .795      .923    +.128
8f      .745      .839    +.094
```

### CC0-A3D — replication + persistent track state

Second webcam run reproduced the same sign:

```text
lag    single    multi    delta
1f      .859      .920    +.061
2f      .801      .867    +.066
4f      .705      .807    +.101
8f      .717      .799    +.082
```

So the narrow positive claim now has two real-webcam receipts:

> **cross-scale agreement contains repeatable information about local temporal persistence.**

Do not strengthen that sentence beyond the data.

## Non-monotonic boundary

The stronger claim `more scales -> more persistence` is false/uneared.

A3D 1-frame persistence:

```text
m=1 .859
m=2 .936
m=3 .952
m=4 .984
m=5 .992
m=6 .619
```

The all-six-scale class behaves differently. Reason unknown. Do not turn multiplicity directly into confidence without attacking this class.

## A3D tracker result

A3D connected `multiplicity >= 2` regions into tiny local states with:

```text
SUPPORTED  current evidence
REUSE      supported consequence unchanged
HOLD       state retained without current support
WAKE       NEW / UPDATE / REACQUIRE / EXPIRE
```

Same tracker was applied to the plain tile attacker.

```text
                               certificate      tile
current evidence fanout          .1373           .0602
belief fanout                    .2099           .1254
held-only fanout                 .0726           .0652
receiver WAKE fraction           .3996           .4378
mean track age                  13.1f           16.6f
created/expired                 38/37           30/29
reacquired                       53              66
```

Event counts:

```text
certificate: NEW38 UPDATE71 REACQUIRE53 REUSE39 HOLD260 EXPIRE37
tile:        NEW30 UPDATE93 REACQUIRE66 REUSE17 HOLD263 EXPIRE29
```

Interpretation:

- certificate gives a modest ~8.7% relative reduction in downstream WAKE fraction;
- certificate gives more REUSE and fewer UPDATE/REACQUIRE events;
- but certificate requires much more spatial state, has shorter mean tracks and more create/expire churn;
- therefore **A3D is a mixed result, not an overall win over tiles.**

## Architectural update

The important decomposition is now:

```text
CHEAP ROUTER
raw delta / plain spatial tiles
    -> candidate address

RICHER LOCAL CERTIFICATE
cross-scale / multiscale agreement
    -> persistence / validity information

PERSISTENT LOCAL STATE
small consequence / track / belief
    -> may HOLD when support disappears

RECEIVER EVENT
WAKE only on material consequence change
```

The spectral field should currently be treated as a **teacher/verifier**, not the hot-loop substrate.

This also gives the earlier phrase “communicate, yet hold belief” a concrete non-mystical implementation:

```text
sensor support != persistent state != downstream communication
```

A3D does not establish a brain mechanism. HOLD=4 is hand-set and the tracker is ordinary.

## Main next hard gate — A3E / first real exploitability test

Stop running the expensive multiscale verifier everywhere.

```text
raw / tile local change
      -> small candidate set (+ fixed neighborhood)
      -> compute multiscale verifier ONLY there
      -> compare with dense multiscale oracle teacher
      -> update persistent local state
      -> emit WAKE only when consequence changes
```

Measure:

```text
candidate-cell fraction
certificate recall / precision vs dense teacher
persistent-event misses
local verifier calls
actual CPU wall time
receiver WAKEs
belief fanout
track churn
```

Mandatory attackers:

```text
tile-only tracker
dense spectral certificate tracker
simple Gaussian/Laplacian/DoG image pyramid
raw-delta local verifier
```

The simple image-pyramid attacker is load-bearing. What survived is **multiscale agreement**, not Gabor specificity.

Kill A3E if local verification needs most cells, patch overhead erases wall-time savings, a cheap pyramid gives the same signal, or tile-only state is equal/better at matched quality.

## Secondary gate

Replace arbitrary `HOLD_FRAMES=4` later with an empirically calibrated survival/hazard rule conditioned on certificate/history. Do not spend effort on this until the certificate itself can be obtained cheaply.

## Broader decomposition remains

```text
TheClutch2 / Fusion1      validity sparsity
DifferentMachine          causal-frontier sparsity
SplatNeuron               receiver sparsity
KYY/TWC/Arbors/ArborVerb  operator lowering
```

The new visual result fits between the first two:

```text
cheap local address -> certificate of persistence -> held consequence -> receiver-local wake
```

## Do not claim

```text
faster AI
runtime speedup
Gabor superiority
spectral field as universal substrate
brain/cortical mechanism
monotonic confidence with number of scales
```

## Carry-forward

> **Receiver-relative invalidation exists on a real sensor stream. Cross-scale agreement repeatedly predicted local persistence. The next thing to earn is whether a cheap router can invoke that richer certificate only where needed and thereby save actual wall-clock work.**
