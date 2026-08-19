# HANDOFF — 2026-08-19 — CC0-A3D

## State in one sentence

> **Cross-scale agreement survived as a local persistence signal, but the dense spectral field did not earn itself as the runtime body; the architecture should now separate cheap routing from richer persistence certification.**

## What was built today

The CC0 line progressed through:

```text
CC0-A1  encoded-video invalidation opportunity census
CC0-A2  real webcam receiver invalidation census
CC0-A3  localized 6-scale x 4-orientation spectral field + tile attacker
CC0-A3B fixed-normalization repair
CC0-A3C cross-scale multiplicity -> future persistence test
CC0-A3D persistent certificate tracker: SUPPORTED / REUSE / HOLD / WAKE
```

Main files:

```text
experiments/cc0a_invalidation_census.py
experiments/cc0a_webcam_gui.py
experiments/cc0a3_local_spectral_field_gui.py
experiments/cc0a3b_local_spectral_field_fixednorm_gui.py
experiments/cc0a3c_scale_certificate_gui.py
experiments/cc0a3d_certificate_tracker_gui.py

notes/009_compile_math_out_of_hot_loop.md
notes/010_invalidation_or_catastrophe.md
notes/011_cc0a_first_receipt.md
notes/012_cc0a2_webcam_gui.md
notes/013_cc0a3_local_spectral_field.md
notes/015_cc0a3c_cross_scale_persistence_certificate.md
notes/016_cc0a3d_persistent_certificate_tracker.md
notes/017_a3d_result_router_certificate_separation.md

results/2026-08-19_cc0a2_webcam_receipt.txt
results/2026-08-19_cc0a3b_fixednorm_webcam_receipt.txt
results/2026-08-19_cc0a3d_certificate_tracker_receipt.txt
```

## Receipts that matter

### A2 — real sensor invalidation survives

First webcam receiver census:

```text
raw change rate                 1.000
ANY receiver invalid            0.422
receiver-slot invalid fraction  0.158
GLOBAL-OR / local opportunity    2.67x
```

This established that raw physical change and receiver-relevant change are measurably different on a real stream.

### A3B — spectral packets sparse internally, tiles route better

First fixed-normalization spectral run:

```text
spectral packet wake fraction   0.0419
spectral spatial fanout         0.2853
plain tile spatial fanout       0.1414
cross-scale agreement           0.8538
```

Conclusion:

```text
naive Gabor packet field as spatial router: DEMOTED
cross-scale structure: SURVIVES
```

### A3C — cross-scale multiplicity predicts persistence

First explicit persistence run:

```text
lag      single      multi(>=2)      delta
1f       .887        .969            +.082
2f       .859        .953            +.094
4f       .795        .923            +.128
8f       .745        .839            +.094
```

### A3D — replication + persistent-state test

Second webcam run reproduced the sign at every lag:

```text
lag      single      multi(>=2)      delta
1f       .859        .920            +.061
2f       .801        .867            +.066
4f       .705        .807            +.101
8f       .717        .799            +.082
```

So the current narrow positive result is replicated twice:

> **multi-scale local wake predicts future local wake better than single-scale wake in these ordinary webcam sessions.**

Do not inflate that sentence.

## Important failure / boundary

The multiplicity relationship is not monotone all the way to six scales.

In A3D at 1 frame:

```text
m1 .859
m2 .936
m3 .952
m4 .984
m5 .992
m6 .619
```

The all-six-scale events are a different class or a measurement artifact; reason unknown. Do not implement `confidence = multiplicity` blindly.

## A3D tracker result is mixed

Same simple connected-component / centroid tracker on certificate and tile masks:

```text
                               certificate      tile
current evidence fanout          .1373           .0602
belief fanout                    .2099           .1254
held-only fanout                 .0726           .0652
receiver WAKE fraction           .3996           .4378
mean track age                  13.1f           16.6f
created / expired               38 / 37         30 / 29
reacquired                       53              66
```

Event counts:

```text
certificate: NEW38 UPDATE71 REACQUIRE53 REUSE39 HOLD260 EXPIRE37
tile:        NEW30 UPDATE93 REACQUIRE66 REUSE17 HOLD263 EXPIRE29
```

Interpretation:

- certificate gets modestly fewer downstream WAKEs (~8.7% relative reduction);
- it gets more REUSE and fewer UPDATE/REACQUIRE events;
- but it occupies much more spatial state, has shorter average tracks and more create/expire churn;
- therefore A3D is **not an overall win** over tiles.

## Architectural update

Do not ask one representation to do every job.

Current best decomposition:

```text
CHEAP ROUTER
raw delta / plain spatial tiles
    -> where should we even look?

RICHER CERTIFICATE
cross-scale / multiscale local agreement
    -> does this event deserve persistence / trust?

PERSISTENT LOCAL STATE
small consequence / track / belief
    -> can remain resident without current support

RECEIVER EVENT
WAKE only when persistent consequence materially changes
```

This is the important conceptual state of the project.

The spectral field may be a **teacher/verifier**, not the runtime substrate.

## Why this relates back to the conceptual arc

The original image was of physical units that:

> communicate, yet hold their belief.

A3D gives a tiny non-mystical software instance:

```text
SUPPORTED  = current sensory evidence
HOLD       = persistent state without current evidence
REACQUIRE  = evidence returns
WAKE       = consequence changes enough to tell someone else
```

That is useful because it separates support, belief and communication.

Do not call this a brain model. HOLD=4 is hand-coded and the tracker is ordinary.

## Main next hard gate — A3E / first exploitability gate

The original goal was faster computation, so the next move should finally stop evaluating the expensive spectral verifier globally.

Candidate pipeline:

```text
raw / tile local delta
      -> candidate cells (+ fixed neighborhood)
      -> evaluate multiscale verifier ONLY for candidates
      -> approximate dense certificate teacher
      -> update persistent local state
      -> emit receiver WAKE only on consequence change
```

Dense Gabor/multiscale processing remains available in parallel only as an oracle teacher during the experiment.

### Measure

```text
candidate fanout
certificate recall vs dense teacher
certificate precision / false misses
persistent-event recall
local verifier calls
front-end wall time
receiver WAKEs
belief fanout
track churn
```

### Mandatory attackers

```text
tile-only tracker
dense spectral certificate tracker
simple Gaussian/Laplacian/DoG image pyramid
raw-delta local verifier
```

The simple image-pyramid attacker is especially important because A3C/A3D support **multiscale agreement**, not frequency/Gabor specificity.

### Kill

Kill the routed spectral verifier if:

```text
certificate recall requires touching most cells
OR
local patch overhead erases wall-time savings
OR
simple image pyramid gives the same persistence signal more cheaply
OR
tile-only state is equal/better at matched quality
```

## Secondary next gate — remove arbitrary HOLD=4

A3C/A3D already estimate survival probabilities conditioned on certificate class.

Later, replace fixed `HOLD_FRAMES=4` with a calibrated survival/hazard rule, but only after the certificate can be obtained cheaply.

## Epistemic boundary

Keep these separate:

```text
sensor support        what is externally constrained now
persistent belief     what local state currently retains/predicts
runtime validity      whether receiver consequence can be reused
communication         whether downstream needs a WAKE
```

This parallels WorldModel support/provenance, but the CC0 runtime ledger is not the same as evidence lineage.

## Carry-forward sentence

> **Use the cheapest geometry to address a change, a richer local test to decide whether it deserves persistence, and wake downstream computation only when the persistent consequence itself becomes invalid.**

## Do not claim

```text
faster AI
runtime speedup
Gabor superiority
brain mechanism
spectral field as universal substrate
monotonic confidence with number of scales
```

What is earned so far is much narrower and more useful:

> **receiver-relative invalidation exists on a real sensor stream, and cross-scale agreement carried repeatable information about local temporal persistence.**
