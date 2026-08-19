# TheWorld — current handoff

**Date:** 2026-08-19  
**State:** observer geometry + anchored-world bookkeeping + minimal material runtime have collided with older repo results. The main line is now **receiver-aware self-adjusting execution / compile the math out of the hot loop**. No novelty claim.

For the full current synthesis see:

- `notes/009_compile_math_out_of_hot_loop.md`
- `HANDOFF_2026-08-19_COMPILE_HOT_LOOP.md`

The previous FLOW/JUMP + minimal-realization state is preserved in `HANDOFF_2026-08-19_FLOW_JUMP_RECEIVER_REALIZATION.md`.

---

## One-line state

> **Keep a rich learned machine persistent; reuse consequences while they remain valid; touch only locally discoverable causal frontiers; wake only receivers whose distinguishable world changed; and execute the smallest cheap realization those receivers actually need.**

---

## What the repo archaeology changed

The latest “minimal neuron” ideas were not one new mechanism. They decomposed into four older measured lines:

```text
TheClutch2 / Fusion1
    validity sparsity
    -> don't recompute while a cached consequence remains usable

DifferentMachine
    causal-frontier sparsity
    -> don't execute quiet/unreached state

SplatNeuron / observer geometry
    receiver sparsity
    -> don't preserve or communicate distinctions this receiver cannot use

KYY / TWC / FunctionalArbors / ArborVerb / Note 008
    operator lowering
    -> don't execute a general model when a cheaper realization suffices
```

The next experiment must combine these and pay for the control plane rather than re-proving one piece in isolation.

---

## Receiver-relative invalidation

For receiver

\[
y_i=h_i(x),
\]

and local state change `delta x`,

\[
\delta y_i \approx J_i\delta x,
\qquad J_i=Dh_i(x).
\]

The runtime implication is:

> **A changed dependency does not necessarily invalidate a receiver consequence.**

Large motion near `ker(J_i)` can leave receiver `i` effectively unchanged. Small motion along a sensitive direction can invalidate it immediately.

Approximate receiver equivalence:

\[
x_1\sim_{i,\epsilon}x_2
\iff
\|h_i(x_1)-h_i(x_2)\|\le\epsilon_i.
\]

A cached output may sleep while the world remains inside that tolerance region.

This is the bridge between the observer-atlas mathematics and incremental computation.

---

## The guard has to be cheaper than waking

Candidate runtime:

```text
cheap certificate says safe     -> REUSE
certificate uncertain           -> PROBE
receiver consequence changed    -> local WAKE
local model no longer trusted   -> full REFRESH / teacher
```

Possible guards include local ids, spatial hashes, coarse bounding volumes, low-rank sensitivity sketches, small learned classifiers or domain-specific probes.

Do **not** assume Jacobians are cheap. They are an analysis/teacher instrument unless they actually win the runtime bill.

---

## Whole-system cost

Any speed claim must pay for:

```text
change detection
candidate discovery
routing / queues
metadata / indices
local state updates
receiver computation
teacher refreshes
memory traffic
synchronization
recovery after drift
```

A useful shorthand is

\[
C_t=C_{detect}+C_{route}+C_{metadata}+C_{frontier}
+\sum_i I_i C_i+I_{refresh}C_{teacher}.
\]

If this is not below a strong ordinary implementation at matched quality, the architecture loses.

---

## Prior-art boundary

Do not claim invention of:

```text
memoization / incremental computation
self-adjusting computation
change propagation
delta / temporal-sparse inference
conditional computation
model reduction / balanced truncation
knowledge distillation
event-driven SSM/RNN execution
```

The unearned engineering question is the **joint compiler/runtime**:

```text
rich teacher
 -> receiver maps
 -> cheap receiver-validity guards
 -> locally discoverable causal frontier
 -> reduced/cheap realizations
 -> sparse execution
 -> occasional full refresh
```

with honest end-to-end resource accounting.

---

# Main next gate — CC0

`MP3 primitive auction` is demoted to a component test.

## CC0 — Compiled Consequence Gate 0

Question:

> **Can receiver-relative invalidation plus persistent local state avoid real work at matched task quality after paying for detection, routing, metadata and refresh?**

### First substrate

Prefer `NeuromorphicDVSplusEMDfield` as the immediate real-stream instrument because image/event coordinates provide world-supplied locality.

### Second substrate

After the current WorldSplat ray-fix finishes, use the learned scene/world state as a rich teacher. Do not modify the running training gate.

### First receivers

Use narrow consequences rather than full RGB:

```text
near-field collision
left/right motion
object continuity
route-relevant obstacle state
```

### Mandatory attackers

```text
FULL every step
make/dependency invalidation
raw-delta threshold
global Clutch gate
tiny always-on GRU / SSM / MLP
serious delta/incremental baseline where architecture permits
receiver-aware compiled runtime
```

### Measure

```text
task error / critical misses
teacher wake fraction
local update fraction
messages/events processed
persistent state bytes
index/metadata bytes
CPU wall time
GPU wall time when relevant
latency distribution
forced-drift recovery cost
```

### Kill lines

- FLOPs improve but wall time loses after routing/memory -> **LOSE**.
- Tiny always-on model is faster at same quality -> **LOSE**.
- Conventional incremental/delta baseline matches it more simply -> keep baseline; architecture claim **LOSES**.
- Receiver-aware wake rate is not materially below raw world/input change rate -> receiver quotient provides no useful runtime sparsity here.

---

## WorldModel epistemic side remains separate

The anchored-world code currently has source categories for sensor, independent model, teacher prior and self-prediction.

Note 006 identified the missing active-agent distinction:

```text
exogenous measurement
active-sensing measurement
intervention-mediated measurement
recursive prediction
```

That is worth implementing later, but it is not the speed mechanism.

Keep the two ledgers separate:

```text
How much work did I avoid?
How independently was this belief earned?
```

---

## What “skip the maths” now means

Not “no mathematics.”

It means:

```text
pay expensive learning/identification occasionally
compile useful consequences into persistent state/structure
leave them resident while valid
route only receiver-relevant innovations
execute only the cheap realization needed locally
wake the expensive teacher when the certificate fails
```

The mathematics still describes and trains the machine. The hot loop may execute far less of it.

---

## Carry-forward sentence

> **Compile the expensive relationship once; keep its useful consequence resident; wake only the receivers whose distinguishable world actually changed; and make the proof that they can sleep cheaper than waking them.**
