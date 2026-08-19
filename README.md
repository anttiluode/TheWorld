# TheWorld

A thinking ledger for the mathematics between the SplatWorld / TinyAvatar / WorldModel line and the SplatNeuron / dendrite / Geometric-Neuron observer line.

> **Do not begin by claiming a brain architecture. Begin by asking what a partial receiver can actually know, preserve, and cheaply realize about a larger world.**

The repo began from:

> **Each unit has a small nonlinear observation map into a vastly richer surrounding state.**

The dynamic refinement became:

> **Each receiver may require only a low-order realization of the surrounding world's dynamics. Compile that receiver into the cheapest local causal primitives that preserve the consequences it actually needs.**

The newest systems refinement is:

> **Do not recompute a consequence merely because its inputs changed. Recompute only when the change can cross that receiver's distinguishability boundary, and make the certificate and routing cheaper than the work they suppress.**

The word *subspace* is deliberately not used globally. A nonlinear observation map has fibers / indistinguishable sets; only its local differential has a literal linear row-space and nullspace.

---

## Current spine

### 1. Observer geometry

- `notes/001_observer_atlas.md` — nonlinear observation maps, local Jacobians/nullspaces, multi-view observability, Wide Present connection.
- `notes/002_confidence_is_not_observability.md` — separate belief precision from external support; generalized anchor-gap directions.
- `notes/003_observer_metrics_quotients_and_face_space.md` — receiver-specific information metrics, quotient/equivalence geometry, face-space interpretation.

### 2. World dimensionality and causal evidence

- `notes/004_intrinsic_dimension_and_navigation.md` — physical dimension vs behavioral manifold vs task/observer dimension.
- `notes/005_below_vectors_local_causal_grammar.md` — the substrate does not symbolically evaluate the mathematics used to describe it.
- `notes/006_endogenous_evidence_and_self_confirming_loops.md` — source lineage plus intervention lineage; external evidence can still be causally endogenous.

### 3. Minimal material runtime

- `notes/004_mass_pulse_minimal_neuron.md` — first Mass–Pulse abstraction: local state + delayed routing + sparse pulse output.
- `notes/007_flow_jump_material_isa.md` — Mass–Pulse ablation; FLOW/JUMP/ROUTE/EMIT material ISA; finite-window gate kills exponential mass as a universal primitive; precise state-price for rotation/phase.
- `experiments/minimal_material_neuron.py` — lazy event parity, delay coincidence and activity-silent local-history toys.
- `experiments/mass_pulse_gate1_primitive_ladder.py` — exponential vs linear vs finite-window receiver with structured/shuffled delay controls.
- `experiments/mass_pulse_gate2_phase_bill.py` — real-decay bank versus one 2-state damped rotational mode.

### 4. Receiver-specific dynamical worlds

- `notes/008_receiver_specific_minimal_realization.md` — dynamic SplatNeuron refinement via transfer functions, Hankel spectra and minimal realization degree.
- `experiments/receiver_specific_hankel_gate.py` — one 6-state world, receiver Hankel ranks 1 / 2 / 1 / 6.
- `results/2026-08-19_receiver_specific_realization.txt` — frozen output and interpretation.

### 5. Receiver-aware incremental runtime

- `notes/009_compile_math_out_of_hot_loop.md` — cross-repo synthesis: validity sparsity + causal-frontier sparsity + receiver sparsity + operator lowering; receiver-relative invalidation; full runtime cost bill; CC0.
- `notes/010_invalidation_or_catastrophe.md` — why one global change gate collapses as a large world grows; receiver-local validity scaling; CC0-A invalidation sparsity census.
- `HANDOFF_2026-08-19_COMPILE_HOT_LOOP.md` — current detailed handoff and prior-art collision.
- `HANDOFF_CURRENT.md` — rolling current state.

---

## Current architecture hypothesis

Do not give every unit the same dynamics, and do not wake every unit merely because some upstream state changed.

Candidate path:

```text
rich persistent world / teacher
        ↓
receiver-specific observation geometry
        ↓
receiver-specific validity / distinguishability boundary
        ↓
cheap guard + locally discoverable causal frontier
        ↓
receiver-specific temporal consequence map
        ↓
effective Hankel spectrum / minimal realization degree
        ↓
compile to cheapest local primitives
        ↓
sparse event execution
        ↓
full refresh only when local validity fails
```

Candidate primitive library remains:

```text
DELAY(d)
WINDOW(w)
RELAX(alpha)
RESOURCE(alpha, jump)
ROTATE(alpha, omega)
THRESHOLD(theta)
RESET / REFRACT
ADAPT
```

Nothing here is universal. Every block, guard, index and routing mechanism has to earn its resource cost.

---

## Four ways not to compute

The repo family already contains separate ancestors for four different savings:

```text
TheClutch2 / Fusion1
    REUSE a still-valid expensive consequence

DifferentMachine
    DON'T TOUCH quiet/unreached persistent state

SplatNeuron / observer geometry
    DON'T TELL a receiver about distinctions it cannot use

KYY / TWC / FunctionalArbors / ArborVerb
    EXECUTE A CHEAPER BODY after learning/identification
```

The current job is not to re-prove these independently. It is to combine them and measure the whole systems bill.

---

## Why one global gate is not enough

Suppose `R` receivers each become invalid with probability `p` on a step.

A single global gate that wakes everything whenever **any** receiver changes has wake probability

```text
1 - (1-p)^R
```

under the simple independent toy assumption.

As `R` grows, that approaches `1` even when each individual receiver changes rarely.

Example:

```text
R = 100
p = .01

ANY receiver invalid     ≈ 63.4% of steps
one receiver on average  = 1% of steps
```

So a large world can be almost never globally quiet while most receiver consequences remain locally valid.

This makes the `DifferentMachine` constraint load-bearing: receiver invalidations must be routed to a small candidate set without scanning all receivers.

See `notes/010_invalidation_or_catastrophe.md`.

---

## House rules

Keep these distinctions separate:

1. **belief/content** — what the system currently predicts;
2. **observability/support** — which directions were actually constrained by external measurements;
3. **source/intervention lineage** — where evidence came from and whether the model's own actions partly generated it;
4. **receiver compression** — how small a local realization can preserve the consequences relevant to one consumer;
5. **runtime validity** — whether a cached receiver consequence can still be reused after the world changes;
6. **internal queries / imagination** — operations on belief that are not new evidence.

A compelling internal world is allowed to be wrong. A tiny receiver is allowed to inherit a huge prior. A cached result is allowed to remain valid while upstream state changes. The bookkeeping must still say why.

---

## Main next hard gate

`CC0 — Compiled Consequence Gate 0`

Before implementing the full runtime, run:

### `CC0-A — invalidation sparsity census`

On a real changing stream:

```text
run the rich teacher offline on every step
choose several narrow receivers
record their true consequences
set task-meaningful tolerances
mark which receivers actually become invalid each step
measure global-any vs per-receiver vs cluster invalidation
```

Only proceed if:

```text
global world/input changes often
BUT
most receiver consequences remain valid most of the time
AND
an event invalidates only a small receiver cluster
```

If that opportunity exists, then `CC0-B` learns/derives cheap guards and routing that approximate the oracle invalidation matrix without running the teacher.

Immediate candidate substrate: `NeuromorphicDVSplusEMDfield`, where locality comes from real image/event coordinates.

Second substrate: the learned WorldSplat state after the current ray-fix A/B finishes. Do not retrofit the running trainer.

First narrow receivers should be things like near-field collision, left/right motion, object continuity or route-relevant obstacle state rather than full RGB reproduction.

Mandatory attackers include:

```text
FULL every step
make/dependency invalidation
raw-delta threshold
global Clutch gate
tiny always-on GRU/SSM/MLP
serious delta/incremental baseline where possible
```

The receiver-aware runtime must pay for:

```text
change detection
candidate discovery
routing / queueing
metadata / indices
local state updates
receiver work
teacher refreshes
memory traffic
synchronization
recovery after drift
actual CPU/GPU wall time
```

If it wins only in nominal operation count, it loses.

`MP3 — primitive auction` remains a component test for deciding when DELAY/WINDOW/RELAX/RESOURCE/ROTATE are worth buying; it is no longer the main architecture gate.

---

## Prior-art boundary

Do not claim invention of memoization, self-adjusting/incremental computation, change propagation, delta inference, conditional computation, model reduction, balanced truncation, knowledge distillation, event-driven state-space execution or structured recurrence.

The candidate contribution to earn is narrower: a joint compiler/runtime that discovers receiver-specific validity, locally discoverable causal frontiers and cheap realizations, then demonstrates a real accuracy–latency–memory/energy frontier advantage over strong ordinary baselines.

---

> **A large world is almost never globally unchanged. The scalable question is whether most individual receivers remain valid, and whether the few invalidated receivers can be found without scanning the rest.**

> **Compile the expensive relationship once; keep its useful consequence resident; wake only the receivers whose distinguishable world actually changed; and make the proof that they can sleep cheaper than waking them.**

Do not hype. Do not lie. Keep attacking.
