# TheWorld — handoff: compile the math out of the hot loop

**Date:** 2026-08-19  
**State:** the minimal-material-neuron line has collided with older repo results and is now reframed as a receiver-aware incremental runtime/compiler problem.

## One-line state

> **The next target is not a new neuron equation. It is a runtime that keeps a rich learned machine persistent, reuses consequences while they remain valid, follows only locally discoverable causal frontiers, preserves only receiver-relevant distinctions, and lowers surviving dynamics into the cheapest realizations that earn their cost.**

See `notes/009_compile_math_out_of_hot_loop.md`.

---

## What survived the repo archaeology

The apparent new idea split into four older measured threads:

```text
TheClutch2 / Fusion1
    don't recompute while a cached consequence is still valid

DifferentMachine
    don't execute quiet/unreached state; follow an addressed causal frontier

SplatNeuron / observer geometry
    don't preserve or communicate distinctions a receiver cannot use

KYY / TransientWaveCompiler / FunctionalArbors / ArborVerb
    lower learned/identified dynamics into cheaper structured realizations
```

The mistake would be to build a fifth toy that re-proves one of those separately.

The useful synthesis is to make them one runtime and then attack the total systems cost.

---

## The new operational bridge

For receiver

\[
y_i=h_i(x),
\]

a state change gives locally

\[
\delta y_i\approx J_i\delta x.
\]

A large `delta x` can be almost irrelevant if it lies near `ker(J_i)`.

A small `delta x` can be critical if it points along a strongly observable receiver direction.

So the central runtime question is not:

```text
did an input change?
```

It is:

```text
could this change move receiver i outside its allowed consequence tolerance?
```

This turns the observer-equivalence idea into a cache invalidation rule.

---

## Four ways not to compute

### 1. REUSE

The consequence is still valid.

Avoid recomputation across time.

### 2. DON'T TOUCH

The event never reaches this state / module.

Avoid state updates across the represented machine.

### 3. DON'T TELL THIS RECEIVER

The world changed, but not in a distinction this receiver cares about.

Avoid communication and downstream work.

### 4. EXECUTE A CHEAPER BODY

The receiver needs a consequence, but its dynamics admit a smaller realization than the rich teacher.

Avoid general dense operator work.

These are separate resource axes and should be measured separately before combining them.

---

## Guard / certificate

Skipping requires evidence that the cached consequence is still usable.

Candidate policy:

```text
cheap bound says safe       -> REUSE
bound uncertain             -> PROBE
bound says consequence moved -> local WAKE
local model loses validity  -> full REFRESH / teacher
```

A Jacobian-based guard is one starting instrument, not the intended endpoint. The compiler should prefer the cheapest guard that works: local ids, spatial hash, coarse bounding box, low-rank sensitivity sketch, threshold table, tiny classifier, or domain-specific probe.

The guard, routing and metadata must all be charged.

---

## Prior-art collision / claim boundary

Do not claim:

```text
incremental computation
memoization
change propagation
model reduction
balanced truncation
delta CNN inference
event-driven state-space models
conditional computation
knowledge distillation
```

Those territories are established.

The candidate engineering contribution to earn is the **joint compiler/runtime**:

```text
rich teacher
 -> receiver definitions
 -> receiver-specific validity guards
 -> locally discoverable causal frontier
 -> low-order/cheap realization
 -> event-sparse execution
 -> full refresh only when needed
```

with complete cost accounting and strong attackers.

---

## Existing repo constraints that must be obeyed

### DifferentMachine

The win dies if finding relevance needs global work.

So every receiver-aware wake mechanism must report **candidate discovery / routing cost**.

### FunctionalArbors

Delay/geometry can carry useful timing.

Absolute phase has repeatedly failed to earn a generic role.

Credit transport was easier than causal eligibility; local changes must be tagged by consequences closer to what they actually changed.

### KYY

Strong generic algebra can beat pretty geometry.

Every structured runtime needs matched GRU/SSM/generic-structured attackers.

### SplatNeuron

Observer compression is conditional on alignment and task complexity.

Dense rotations destroy many compact local-vocabulary advantages.

### Fusion1

Ordinary dependency invalidation / `make` is a mandatory attacker where exact dependency information is available.

A control plane should tie a perfect dependency oracle, not pretend to beat it.

---

## Next gate changes

`MP3 primitive auction` is demoted to a component/unit test.

The main next gate is:

# CC0 — Compiled Consequence Gate 0

Question:

> **Can receiver-relative invalidation plus persistent local state avoid real work at matched task quality after paying for detection, routing, metadata and refresh?**

### Immediate substrate

Use `NeuromorphicDVSplusEMDfield` first if practical.

Reason: locality comes from real image/event coordinates rather than a synthetic graph designed to make locality useful.

### Second substrate

After the current WorldSplat ray-fix finishes, use its learned world as a rich teacher/substrate.

Do not modify the running training gate.

### First receivers

Prefer narrow consequences:

```text
near-field collision
left/right motion
object continuity
route-relevant obstacle state
```

Do not start with full RGB reproduction.

### Attackers

```text
FULL every step
make/dependency invalidation
raw-delta threshold
one global Clutch gate
tiny always-on GRU/SSM/MLP
serious delta/incremental baseline where possible
receiver-aware compiled runtime
```

### Required measurements

```text
task error / safety misses
teacher wake fraction
local update fraction
message/event count
persistent state bytes
index/metadata bytes
CPU wall time
GPU wall time if applicable
latency distribution
recovery after forced change
```

### Kill line

If the receiver-aware system wins only in nominal FLOPs but loses after routing/memory/scheduling, it loses.

If a tiny always-on model is faster at the same quality, it loses.

If a conventional delta/incremental baseline is equally good and simpler, keep the baseline and stop the architecture claim.

---

## WorldModel epistemic side note

Current anchored-world code tracks source kinds roughly as:

```text
SENSOR
INDEPENDENT_MODEL
TEACHER_PRIOR
SELF_PREDICTION
```

The new Note 006 distinction has not yet been lowered into that enum:

```text
active sensing
intervention-mediated measurement
```

That is a real implementation gap, but it is **orthogonal to the speed gate**.

Do not mix better evidence lineage with faster execution into one headline.

---

## The deeper interpretation of “skip the maths”

The useful version is not mystical.

A rich model may spend huge computation learning a relationship.

After learning, some consequences can be embodied in:

```text
persistent state
cached result
local topology
delay
small recurrence
coarse guard
address/index
```

Then the hot loop need not re-solve the original relationship every clock tick.

This is ordinary amortization/compilation pushed aggressively into learned dynamical systems.

The hypothesis is that **receiver-relative change** may let us push it farther than raw input-delta or global surprise alone.

---

## Carry-forward sentence

> **Compile the expensive relationship once; keep its useful consequence resident; wake only the receivers whose distinguishable world actually changed; and make the proof that they can sleep cheaper than waking them.**
