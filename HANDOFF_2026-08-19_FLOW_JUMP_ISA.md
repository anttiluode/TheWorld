# TheWorld handoff — FLOW/JUMP material ISA

**Date:** 2026-08-19  
**Status:** two new executed mechanism gates; architecture narrowed, not validated.

## One-line state

> **Replace the universal `mass` primitive with a cheaper hybrid-program view: silent FLOW, event-triggered JUMP, geometry as ROUTE/delay, and sparse EMIT. Buy scalar relaxation, local resource state, or a two-state rotational mode only when a task earns the extra state/operations.**

---

## 1. What changed

The previous Mass–Pulse note proposed:

```text
local mass + relaxation + delayed pulses + threshold/reset
```

The first ablation killed the universal `mass` part.

A 12-sensor travelling-event detector was tested with the same structured delay geometry and progressively cheaper receiver dynamics:

```text
exponential mass  -> 0.99713 held-out accuracy
linear mass       -> 0.99862
finite window     -> 0.99925
```

For the cheapest finite-window arm:

```text
no delay geometry            -> 0.50887
32 shuffled delay geometries -> mean 0.63446, sd 0.10593, best 0.87813
```

So the first task needs geometry + coincidence, not analog exponential relaxation.

This is a built-in velocity prior and a mechanism gate only. It is not a learned-architecture result.

Code:

```text
experiments/mass_pulse_gate1_primitive_ladder.py
```

Frozen output:

```text
results/2026-08-19_mass_pulse_chase.txt
```

---

## 2. New core language

For local state `q`, split dynamics into:

\[
q(t+\Delta)=\Phi_\Delta(q(t))
\]

between events, and

\[
q^+=J_e(q^-,e)
\]

at an event.

Candidate ISA:

```text
FLOW(dt)
JUMP(event)
ROUTE(target, delay, gain/type)
EMIT(condition)
ADAPT              # slow/optional
```

This is a hybrid/event-driven systems description, not a new mathematical class.

Important implementation idea:

If `FLOW` is analytically composable / has a semigroup property, a digital runtime can jump directly across silence instead of executing clock ticks.

This generalizes the previous lazy exponential trick to:

```text
finite timeout
a linear countdown
exponential decay
a resource/recovery state
a damped 2-D rotation
```

---

## 3. Cheapest state ladder

Do not begin at LIF if a cheaper primitive is sufficient.

```text
LEVEL A — DELAY
    schedule event at t+d

LEVEL B — TIMEOUT / WINDOW
    expiry timestamp or integer occupancy

LEVEL C — RELAX
    one scalar fading state

LEVEL D — RESOURCE
    one additional slow local state whose value changes future transmission

LEVEL E — ROTATE
    two real states carrying a damped rotational/phase mode

LEVEL F — richer nonlinear branch dynamics
    only after lower levels fail
```

Slow learning/plasticity remains separate:

```text
ADAPT / REWIRE only on selected events or slow schedules
```

---

## 4. The Laplace bridge

For event input

\[
u(t)=\sum_n a_n\delta(t-t_n)
\]

one leaky state

\[
\dot m_s=-s m_s+u(t)
\]

contains

\[
m_s(t)=\sum_n a_n e^{-s(t-t_n)}.
\]

This is a real Laplace-transform coordinate of recent event history.

This is established work: Shankar & Howard 2012 explicitly propose banks of leaky integrators as a Laplace representation of temporal history.

Interpretation for this program:

> `the past survives as unrelaxed matter` has a precise standard mathematical neighbor. The element does not symbolically calculate the transform; its relaxation is the operation described by that transform.

A bank of scalar relaxers is a diagonal continuous-time state-space model.

This places the architecture next to S4 / Mamba / continuous-time and event-by-event SSM work. Any claim must attack those baselines.

---

## 5. New phase bill

A scalar relaxer is one real stable pole:

\[
\lambda=-\alpha.
\]

A two-state rotational block is

\[
M=-\alpha I+\omega J,
\qquad
J=\begin{bmatrix}0&-1\\1&0\end{bmatrix},
\qquad J^T=-J.
\]

Its poles are

\[
-\alpha\pm i\omega
\]

and

\[
e^{Mt}=e^{-\alpha t}R(\omega t).
\]

Gate MP2 targeted

\[
e^{-0.12t}\cos(2\pi\,0.35t)
\]

over `[0,20]`.

The target has 14 sign changes.

Real scalar-decay banks:

```text
K= 1  RMSE .322197
K= 2  RMSE .299493
K= 4  RMSE .296727
K= 8  RMSE .260116
K=16  RMSE .211091   max coefficient ~9.2e3
K=32  RMSE .207509
K=64  RMSE .203992
```

One two-state rotate/decay block reproduces the target analytically with zero RMSE.

Code:

```text
experiments/mass_pulse_gate2_phase_bill.py
```

Interpretation:

> **Scalar relaxation is the cheap primitive for fading memory. A 2-D rotational state is the compact primitive for a genuine oscillatory/cyclic mode.**

This gives the old `phase must pay its bill` thread a precise systems meaning.

It also mirrors the old GeometricNeuron symmetric/skew split locally:

```text
-alpha I     symmetric dissipative part
omega J      skew rotational part
```

Do not overstate: directed feed-forward delays can detect temporal order without local rotational state. The old passive-reciprocity result is not contradicted because the delay graph is already causal/directed.

---

## 6. Literature boundary checked today

Primary neighbors:

- Brette 2006, *Exact simulation of integrate-and-fire models with synaptic conductances* — exact event-driven simulation when inter-event dynamics are analytically tractable.
- Brette 2007, *Exact simulation of integrate-and-fire models with exponential currents* — extends event-driven exactness to multiple exponential time constants/adaptation.
- Carr & Konishi 1988/1990 — barn-owl axonal conduction delays as physical delay lines feeding coincidence detection for ITD.
- Izhikevich 2006, *Polychronization: computation with spikes* — conduction delays + STDP generate reproducible non-synchronous temporal groups.
- Gütig & Sompolinsky 2006, *The tempotron* — single spiking readout learns spatiotemporal spike decisions.
- Shankar & Howard 2012, *A scale-invariant internal representation of time* — leaky integrators implement a Laplace transform of history.
- S4 (Gu, Goel, Ré 2021) — structured continuous-time state-space sequence model.
- Mamba (Gu & Dao 2023) — selective input-dependent SSM.
- Schöne et al. 2024 — event-by-event deep state-space processing of very long neuromorphic event streams.

Therefore no novelty claim may be phrased as:

```text
event-driven neurons
state-space memory
axonal delays compute time
leaky traces remember history
```

Those are established.

The thing to test is the **resource-selection/compiler** program.

---

## 7. Candidate new research question

> **Can a learner/compiler choose the cheapest local causal block needed at each site—delay, timeout, scalar relaxation, resource state, or rotational pair—and match a strong recurrent/SSM baseline while doing work proportional to sparse causal events rather than dense clock ticks?**

This is an engineering claim, not a brain claim.

The strongest version requires all of:

```text
matched task error
matched or lower state count
measured event/communication count
actual wall-clock runtime
strong recurrent/TCN/SSM baselines
geometry shuffle
block ablations
no built-in target geometry in the final benchmark
```

---

## 8. Next experiments

### MP3 — primitive auction

One dataset, same train/test split. Allow candidate blocks:

```text
DELAY
WINDOW
RELAX
RESOURCE
ROTATE
```

Objective should include task loss + explicit block/runtime bill.

Question:

> does a sparse heterogeneous body occupy a better accuracy/resource Pareto frontier than using the richest state everywhere?

### MP4 — learn the delays

Gate MP1 hand-coded the correct travel geometry. That is the next cheat to remove.

Learn or search the delay assignment from examples, then compare against:

```text
linear slope/time-feature baseline
Tempotron-like temporal readout
small GRU
small TCN
small diagonal SSM
modern event-by-event SSM if practical
```

### MP5 — complex-pole necessity

Construct task families whose optimal temporal operator ranges from monotone memory to damped periodic structure.

Prediction:

```text
monotone tasks -> scalar relaxer wins resource bill
periodic tasks -> rotate pair enters Pareto frontier
```

If the learned auction buys ROTATE on non-oscillatory tasks, the regularizer/compiler is wrong.

### MP6 — WorldSplat receiver experiment

Do not feed every receiver a rendered frame.

Generate sparse primitive-change events from one persistent scene state and compare receiver bodies for:

```text
motion
collision
object persistence
navigation
```

Measure how much each receiver can discard while preserving its task distinctions.

This rejoins the observer-atlas/SplatNeuron line.

---

## 9. Carry forward

The strongest conceptual compression now is:

```text
MATERIAL BODY
    local state blocks
    + event routing / delay
    + sparse jumps
    + threshold emission

ANALYST
    later describes the resulting machine using
    Laplace transforms, poles, spectra, Jacobians, observability, etc.
```

The machine need not execute the analyst's mathematics operation by operation.

And the new phase sentence is:

> **Phase is not the default memory primitive. A two-state rotational mode is a priced instruction for temporal structure with genuine rotation/oscillation; scalar relaxation and delays should get first refusal.**

Do not hype. Keep removing operations until a task breaks.
