# Note 009 — Compile the math out of the hot loop

**Status:** cross-repo synthesis / prior-art collision / architecture gate. No novelty claim.  
**Date:** 2026-08-19

## 0. The question after the rediscoveries

The useful question is no longer:

> Can a neuron-like primitive avoid mathematics?

It is:

> **Can an expensive learned machine be compiled into a runtime that executes only the receiver-relevant consequences that can actually change, while leaving the rest as persistent state/structure?**

There is still mathematics. The proposed saving is that the mathematics is paid during learning, identification, compilation, acquisition, or occasional refresh rather than recomputed densely in every hot-loop step.

A useful slogan is:

> **Compile the math out of the hot loop.**

This note exists mainly to stop `TheWorld` from re-deriving pieces already present elsewhere in the repo family and in established incremental/model-reduction literature.

---

## 1. Four distinct ways not to compute

Several older repos were attacking different axes of the same cost problem.

### A. Validity sparsity — do not recompute a consequence that is still valid

`TheClutch2` and `Fusion1`:

```text
cached expensive consequence
        |
        +-- still valid -> REUSE
        +-- uncertain   -> cheap PROBE
        `-- invalid     -> WAKE expensive computation
```

This is temporal/recompute sparsity.

### B. Causal-frontier sparsity — do not update quiet/unreached state

`DifferentMachine`:

```text
large persistent machine
        |
addressed event
        v
small locally discoverable causal frontier
```

Its most important constraint is already known internally: bounded work survives only while **relevance is locally discoverable**. If finding relevance requires a global scan, the saving disappears.

### C. Receiver sparsity — do not preserve distinctions a receiver cannot use

`SplatNeuron` + Notes 001–003:

```text
rich world x
   |
receiver h_i
   v
small consequence y_i
```

Different receivers partition the same world differently. A world change may be large yet irrelevant to one receiver.

### D. Operator sparsity / lowering — do not execute a general operator when a cheaper realization suffices

`KYY`, `TransientWaveCompiler`, `FunctionalArbors`, `ArborVerb`, Note 008:

```text
learn / identify rich dynamics
        |
reduce / factor / compile
        v
small structured recurrence / local primitive body
```

This is where `RELAX`, `ROTATE`, `DELAY`, scattering sections, poles/residues, reduced models, etc. belong.

These four axes are not interchangeable. A system can exploit one and fail on the others.

---

## 2. The missing unifying runtime object: receiver-relative invalidation

Let the persistent world/internal state be

\[
x_t\in\mathcal M
\]

and receiver `i` care only about

\[
y_i=h_i(x_t).
\]

Suppose the world changes by

\[
\delta x=x_{t+1}-x_t.
\]

Locally,

\[
\delta y_i \approx J_i(x_t)\,\delta x,
\qquad J_i=Dh_i(x_t).
\]

Now the important systems fact is immediate:

\[
\delta x\in\ker J_i
\quad\Rightarrow\quad
\delta y_i\approx 0.
\]

So:

> **Input/state change is not the same thing as receiver consequence change.**

A conventional dependency engine often invalidates a node because an input changed.

A receiver-aware engine should ask the narrower question:

> **Could this change move the receiver's answer outside its allowed tolerance?**

That is the bridge between observer geometry and incremental computation.

---

## 3. Equivalence classes become cache-validity regions

Earlier notes defined

\[
x_1\sim_i x_2
\iff
h_i(x_1)=h_i(x_2).
\]

For a practical approximate receiver, define a tolerance relation

\[
x_1\sim_{i,\epsilon}x_2
\iff
\|h_i(x_1)-h_i(x_2)\|\le\epsilon_i.
\]

Now a cached receiver result remains valid while the changing world stays inside the same approximate equivalence region.

This gives a more operational interpretation of an observer fiber:

> **A receiver fiber is also a region through which the world can move without forcing that receiver to recompute.**

That is a useful systems consequence of the observer mathematics. It is not a new theorem.

---

## 4. Cheap certificates, not blind faith

Skipping an expensive computation is useful only if deciding to skip it is cheaper than doing it.

The runtime therefore needs a **validity certificate / guard**.

Ideal form:

\[
B_i(x,\delta x)
\ge
\|h_i(x+\delta x)-h_i(x)\|.
\]

Then:

```text
B_i <= epsilon_i   -> guaranteed REUSE
B_i uncertain      -> PROBE
B_i > epsilon_i    -> WAKE / update receiver
```

A local smooth approximation might begin from

\[
B_i
\approx
\|J_i\delta x\|
+
\frac12 L_i\|\delta x\|^2,
\]

where `L_i` bounds local curvature/error.

But a Jacobian is not automatically cheap. The compiler may instead learn or derive a cheaper guard:

```text
small projection
local spatial hash
changed-object ids
bounding volume
coarse depth range
low-rank sensitivity sketch
quantized threshold table
small decision tree
cheap probe callback
```

The guard itself belongs on the resource frontier.

---

## 5. The actual cost equation

Any claimed speedup has to pay for the whole control plane.

For one step, roughly:

\[
C_t =
C_{detect}
+ C_{route}
+ C_{metadata}
+ C_{local\ frontier}
+ \sum_i I_i C_{receiver,i}
+ I_{refresh} C_{teacher}.
\]

A sparse architecture wins only if this is below the ordinary dense/always-on alternative at matched task quality.

That means counting:

```text
arithmetic
memory reads/writes
index / queue work
synchronization
branching/scatter overhead
bytes of persistent metadata
probe cost
reacquisition after drift
teacher refreshes
wall-clock latency
```

The enemy is not only FLOPs. It is often memory traffic and scheduling.

---

## 6. Why this is not a novelty claim

The neighboring territories are already large:

```text
memoization / incremental computation
self-adjusting computation
dependency graphs / build systems
differential dataflow
delta / temporal-sparse CNN inference
conditional computation / routing / MoE
event-driven recurrent models / neuromorphic execution
model reduction / balanced truncation
knowledge distillation
state-space models
learned caches / speculative execution
```

Kellems-style reduced neuron models already show that a huge biophysical state can collapse dramatically when only a few receiver voltages matter.

Learnable short-term synaptic dynamics already occupies the idea that local persistent state can learn timing transformations.

`KYY` already showed that generic strong algebraic recurrent baselines can erase a geometric headline.

Therefore the unearned remainder is narrow:

> **Can one toolchain jointly learn receiver-specific validity, locally discoverable causal frontiers, and cheap reduced realizations, then obtain a real accuracy–latency–memory/energy frontier win over strong incremental and always-on baselines?**

That is an engineering result to earn, not a neuron discovery.

---

## 7. Candidate compiler

The first useful compiler pipeline is:

```text
RICH TEACHER / WORLD MODEL
        |
        | collect trajectories + interventions
        v
RECEIVER DEFINITIONS h_i
        |
        +--> measure sensitivity / empirical consequence changes
        +--> identify low-order temporal realization
        +--> discover cheap validity guard
        +--> discover locality / candidate index
        v
LOWER
        |
        +--> direct/JUMP
        +--> DELAY / WINDOW
        +--> RELAX
        +--> ROTATE only if earned
        +--> RESOURCE only if earned
        +--> tiny learned nonlinear block if required
        v
PERSISTENT EVENT RUNTIME
        |
        +--> REUSE
        +--> PROBE
        +--> local WAKE
        `--> full REFRESH / reacquire
```

The teacher can remain available during training and as a fallback. It does not need to run on every event.

---

## 8. Gate CC0 — receiver-aware self-adjusting runtime

`MP3` remains a useful primitive unit test, but it should no longer be the main next gate.

The more consequential next gate is **CC0** (`Compiled Consequence Gate 0`).

### Input

Use a real changing stream where locality comes from the world rather than being hand-designed.

Best immediate candidate already identified by `DifferentMachine`:

```text
NeuromorphicDVSplusEMDfield
```

because image/event coordinates provide natural locality and the stream contains long periods in which much of the represented capacity is irrelevant to a particular receiver.

Second candidate, after the current WorldSplat ray-fix finishes:

```text
WorldModel / WorldSplat
```

### Receiver

Do not begin with full RGB reconstruction.

Use a narrow receiver such as:

```text
near-field collision risk
left/right motion consequence
tracked-object continuity
route-relevant obstacle state
```

### Policies to compare

```text
1. FULL
   run the expensive teacher/receiver every step

2. DEPENDENCY
   invalidate on any declared input dependency change
   make-style attacker

3. RAW-DELTA
   wake on ordinary input/state-change magnitude

4. GLOBAL-CLUTCH
   one cheap global surprise gate

5. TINY-ALWAYS-ON
   matched compact GRU / SSM / MLP receiver

6. RECEIVER-AWARE
   persistent state + cheap receiver-specific guard
   + locally addressed update
   + teacher refresh on guard violation
```

Where architecture permits, add a serious delta/incremental-inference baseline rather than inventing a weak one.

### Measure

```text
task error / missed critical events
teacher wake fraction
receiver update fraction
events/messages processed
state bytes
metadata/index bytes
bytes moved if measurable
CPU wall time
GPU wall time where relevant
latency distribution
recovery cost after forced distribution shift
```

### Kill condition

The story loses if, at matched task quality:

```text
receiver-aware guard + routing + refresh
```

does not beat at least one strong ordinary implementation in **actual runtime/resource cost**.

A FLOP-count-only win is not enough.

---

## 9. WorldSplat connection

The current `WorldModel` trainer should remain untouched while the ray/depth A/B is running.

Afterward, treat its learned scene state as the rich teacher/substrate.

The first question is not whether the whole 512-splat/latent scene can be made event-driven.

Ask:

> **For a particular downstream receiver, how often does a world-state change actually cross that receiver's tolerance boundary?**

Example:

```text
large sky/texture change
    -> RGB receiver invalid
    -> collision receiver may remain valid

small near-depth change
    -> RGB difference may be tiny
    -> collision receiver invalid immediately
```

That is exactly why raw global delta is the wrong wake criterion.

If the receiver-aware wake rate is much smaller than the world's raw change rate, there is exploitable structure.

If not, stop.

---

## 10. Epistemic bookkeeping is parallel, not the speed mechanism

`WorldModel` currently distinguishes source kinds such as sensor, independent model, teacher prior and self-prediction.

Note 006 identified a missing orthogonal axis:

```text
exogenous measurement
active-sensing measurement
intervention-mediated measurement
recursive prediction
```

That should eventually be implemented because it affects what evidence is allowed to support belief.

But do not mix it into the compute-speed claim.

A system can be computationally sparse and epistemically wrong.

A system can be perfectly anchored and computationally wasteful.

These are separate ledgers.

---

## 11. What "skip the maths" means after all the attacks

It does **not** mean:

```text
no mathematics
no multiplication
biology magically computes for free
```

It means:

```text
learn expensive relationship once
compile useful consequence into persistent structure/state
leave it alone while it remains valid
route only actual innovations to affected receivers
execute only the smallest dynamics those receivers require
wake the expensive teacher only when the cheap certificate fails
```

This is the candidate systems architecture.

---

## Carry-forward sentence

> **Do not recompute a consequence merely because its inputs changed. Recompute only when the change can cross that receiver's distinguishability boundary, and make the certificate and routing cheaper than the work they suppress.**
