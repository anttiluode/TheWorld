# TheWorld

A thinking ledger for the mathematics between the SplatWorld / TinyAvatar / WorldModel line and the SplatNeuron / dendrite / Geometric-Neuron observer line.

> **Do not begin by claiming a brain architecture. Begin by asking what a partial receiver can actually know, preserve, and cheaply realize about a larger world.**

The repo began from:

> **Each unit has a small nonlinear observation map into a vastly richer surrounding state.**

The current dynamic refinement is:

> **Each receiver may require only a low-order realization of the surrounding world's dynamics. Compile that receiver into the cheapest local causal primitives that preserve the consequences it actually needs.**

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

### 5. Current handoff

- `HANDOFF_2026-08-19_FLOW_JUMP_RECEIVER_REALIZATION.md` — current synthesis, primitive price list, receiver compiler, WorldSplat bridge and MP3 primitive-auction plan.
- `HANDOFF_CURRENT.md` — rolling current state.

---

## Current architecture hypothesis

Do not give every unit the same internal dynamics.

A candidate path is:

```text
rich persistent world
        ↓
receiver-specific observation map
        ↓
receiver-specific information geometry
        ↓
receiver-specific temporal consequence map
        ↓
effective Hankel spectrum / minimal realization degree
        ↓
compile to cheapest local primitives
        ↓
sparse event execution
```

Candidate primitive library:

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

Nothing here is universal. Every block has to earn its resource cost.

---

## House rules

Keep these distinctions separate:

1. **belief/content** — what the system currently predicts;
2. **observability/support** — which directions were actually constrained by external measurements;
3. **source/intervention lineage** — where evidence came from and whether the model's own actions partly generated it;
4. **receiver compression** — how small a local realization can preserve the consequences relevant to one consumer;
5. **internal queries / imagination** — operations on belief that are not new evidence.

A compelling internal world is allowed to be wrong. A tiny receiver is allowed to inherit a huge prior. The bookkeeping must still say where the system is weakly externally anchored.

---

## Next hard gate

`MP3 — primitive auction`

Optimize task quality jointly with explicit costs for state count, event operations and communication. Test whether different task families actually select different cheap primitives:

```text
coincidence      -> DELAY / WINDOW
recency          -> RELAX
history context  -> RESOURCE
oscillation      -> ROTATE
```

Attack with matched compact GRU/LSTM/TCN/state-space/spiking baselines and actual runtime measurements.

If a conventional compact recurrent/state-space model wins the resource frontier, the material-ISA story loses.

---

> **The mathematics may be the external compressed description of a causal material program, not the symbolic algorithm executed by that material. The useful artificial question is whether we can identify the smallest receiver-specific dynamics and compile them into cheaper local causal operations.**

Do not hype. Do not lie. Keep attacking.
