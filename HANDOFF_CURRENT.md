# TheWorld — current handoff

**Date:** 2026-08-19  
**State:** receiver-aware self-adjusting execution / “compile the math out of the hot loop.” `CC0-A1` has now been executed. It is a positive opportunity receipt on simple encoded video, **not** a runtime-speed result. No novelty claim.

Current detailed files:

- `notes/009_compile_math_out_of_hot_loop.md`
- `notes/010_invalidation_or_catastrophe.md`
- `notes/011_cc0a_first_receipt.md`
- `experiments/cc0a_invalidation_census.py`
- `results/2026-08-19_cc0a_encoded_video.txt`
- `HANDOFF_2026-08-19_CC0A1.md`

---

## One-line state

> **Keep a rich learned machine persistent; reuse consequences while they remain valid; touch only locally discoverable causal frontiers; wake only receivers whose distinguishable world changed; and execute the smallest cheap realization those receivers actually need.**

The four older repo lines remain the decomposition:

```text
TheClutch2 / Fusion1      validity sparsity
DifferentMachine          causal-frontier sparsity
SplatNeuron               receiver sparsity
KYY/TWC/Arbors/ArborVerb  operator lowering
```

The unearned part is their end-to-end combination with honest control-plane cost.

---

## Receiver-relative invalidation

For `y_i = h_i(x)` and local state change `delta x`:

\[
\delta y_i \approx J_i\delta x.
\]

A changed dependency does not necessarily invalidate receiver `i`. A cached receiver output may sleep while the world moves inside an approximate equivalence/tolerance region for that receiver.

That yields the runtime question:

> **Could this world change move this receiver's answer outside its tolerated equivalence class?**

The guard must be cheaper than waking.

---

# CC0-A1 — executed

`experiments/cc0a_invalidation_census.py` densely evaluates 11 receiver consequences on every frame but gives every receiver an independent cached value. A receiver is marked invalid only when its current output has moved beyond its tolerance from that cache.

This is an **oracle census**. It labels skip opportunities; it does not skip the oracle computation itself.

### Main stream

Pre-existing encoded `world.mp4` asset:

```text
frames                         901
raw frame changed              1.0000
ANY receiver invalid           0.1244
mean receivers invalid/frame   0.1322 / 11
receiver-slot invalid fraction 0.01202
```

Equal receiver-cost opportunity comparison:

```text
GLOBAL OR:
  any invalid -> execute all receivers

ORACLE LOCAL:
  execute only invalid receivers

GLOBAL-OR / oracle-local receiver work = 10.35x
```

### Tolerance attack

Tolerance scales `0.15, 0.25, 0.35, 0.50, 0.75, 1.00` gave GLOBAL-OR/local ratios:

```text
9.73x, 9.96x, 10.35x, 10.24x, 11.00x, 11.00x
```

So the relative OR/local gap is not a single-epsilon cherry-pick on this stream.

A different sparse title-animation asset produced a smaller roughly `2.68x -> 5.68x` range depending on tolerance, which is a useful reminder that the ratio is stream/receiver dependent.

### Decision

```text
CC0-A1 instrument/opportunity   PASS
CC0-A2 real external stream     NEXT
CC0-B cheap sparse runtime      BLOCKED until A2
```

---

## What CC0-A1 does NOT establish

Do not say:

```text
10x faster AI
83x faster AI
GPU speedup
energy speedup
natural visual sparsity
learned receiver geometry
```

The dense oracle computed all receivers. No guard, routing, candidate discovery, metadata, memory traffic, teacher refresh, compact baseline or wall-clock saving was measured. The source videos are simple rendered media, not a natural driving/DVS/WorldSplat stream. Several motion receivers are nearly inactive on the globe clip.

The tempting always-on/oracle-local ratio is therefore bookkeeping only, not a headline.

---

# Main next gate — CC0-A2

Repeat the same dense census where locality and receiver semantics come from a real external process.

Preferred substrate order:

```text
1. NeuromorphicDVSplusEMDfield + webcam/recorded real motion
2. real outdoor/driving video
3. WorldModel / WorldSplat after the current ray-fix run finishes
```

Do not modify the running WorldModel training gate.

Use task consequences:

```text
near-field occupancy / collision
left-right motion
tracked-object continuity
route obstruction
```

A useful real-stream gate should show:

```text
world/input changes often
BUT
most individual receiver consequences remain valid
AND
an event addresses only a small receiver cluster
```

If that pattern is absent, stop the receiver-aware speed story for that substrate.

If it survives, then build CC0-B:

```text
oracle invalidation matrix
 -> cheap guard
 -> locally discoverable candidate set
 -> receiver-local wake
 -> compact/reduced receiver implementation
 -> teacher refresh on certificate failure
```

and attack actual wall time, memory traffic and drift recovery against FULL, dependency/make, raw delta, global Clutch, tiny always-on GRU/SSM/MLP, and serious incremental/delta inference.

---

## Parallel epistemic ledger remains separate

`WorldModel` support/provenance asks **why a belief is allowed to count as externally earned**.

CC0 asks **why a computation is allowed to sleep**.

Do not merge those ledgers.

---

## Carry-forward sentence

> **CC0-A1 says the opportunity is measurable; CC0-A2 must show it is real; CC0-B must show it is exploitable.**
