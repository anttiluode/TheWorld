# Note 007 — FLOW / JUMP: the causal material ISA

**Status:** synthesis + two executed mechanism gates; not a novelty claim.  
**Date:** 2026-08-19

## 0. The Mass–Pulse model was still too specific

The previous note proposed a minimal artificial neuron body built from local relaxing `mass`, delayed pulse routing, and threshold/reset.

The next ablation immediately removes part of that proposal:

> **On a spatiotemporal coincidence task, exponential mass was unnecessary. A finite event window plus geometry/delay was slightly better.**

So `mass` should not be a universal primitive.

The deeper primitive is not a particular differential equation. It is a split between what happens **between events** and what happens **at events**.

For local state `q`, write

\[
q(t+\Delta)=\Phi_{\Delta}(q(t))
\]

between events, and

\[
q^+ = J_e(q^-, e)
\]

when event `e` arrives.

The minimal runtime language is therefore:

```text
FLOW(dt)      advance local state across silent time
JUMP(event)   change local state at an event
ROUTE(delay)  schedule a consequence at another location
EMIT(test)    generate a new event when a local condition is met
ADAPT         optionally change slow material/edge state
```

`Mass–Pulse` is one member of this family:

```text
FLOW: exponential relaxation
JUMP: add incoming amplitude
ROUTE: edge delay/gain
EMIT: threshold/reset
```

But a cheaper task may use:

```text
FLOW: nothing
JUMP: increment integer occupancy
ROUTE: delay + expiry event
EMIT: count >= threshold
```

The implementation should buy only the local physics a task earns.

---

## 1. Exact event-driven execution is a semigroup trick

If silent evolution has the composition property

\[
\Phi_{a+b}=\Phi_a\circ\Phi_b,
\]

then a clocked simulator need not execute all intermediate states if no event or readout needs them.

Examples:

### Exponential relaxation

\[
\Phi_{\Delta}(m)=e^{-\Delta/\tau}m.
\]

### Linear countdown with floor

\[
\Phi_{\Delta}(m)=\max(0,m-k\Delta).
\]

### Pure timeout / eligibility window

Store an expiry time. Nothing changes until the expiry event occurs.

### Damped rotation

For two-state `q=[x,y]^T`,

\[
\dot q=(-\alpha I+\omega J)q,
\qquad
J=\begin{bmatrix}0&-1\\1&0\end{bmatrix},
\]

so

\[
\Phi_{\Delta}(q)
=e^{-\alpha\Delta}R(\omega\Delta)q.
\]

The computer can jump directly across an arbitrarily long silent interval.

This is standard event-driven / hybrid-systems territory. Brette (2006, 2007) explicitly develops exact event-driven integrate-and-fire simulation when state evolution between spikes and the spike condition can be solved analytically. The point here is architectural: **treat analytically composable local flow as an ISA property, not as a global simulation loop.**

---

## 2. There is a compiler hiding here

Suppose the external input is an event stream

\[
u(t)=\sum_n a_n\delta(t-t_n).
\]

A scalar relaxing state obeying

\[
\dot m_s=-s m_s+u(t)
\]

has solution

\[
m_s(t)=\sum_{t_n<t} a_n e^{-s(t-t_n)}.
\]

This is exactly a Laplace-transform coordinate of recent input history.

Shankar & Howard (2012) already make this mathematical observation explicitly: a bank of leaky integrators computes a real Laplace transform of temporal history, from which a compressed timeline can be approximately recovered.

This gives a precise version of the phrase

> **the past survives as unrelaxed matter.**

The physical/artificial element does not symbolically calculate a Laplace transform. A leaking state *is the dynamical operation whose external mathematical description is a Laplace coordinate*.

With several time constants,

\[
y(t)=\sum_k c_k m_{s_k}(t)
\]

implements a causal kernel

\[
k(t)=\sum_k c_k e^{-s_k t}.
\]

Adding edge delays gives

\[
k(t)=\sum_k c_k e^{-s_k(t-d_k)}H(t-d_k).
\]

So a desired causal temporal operator can be **compiled into delays + local flows + a sparse readout** rather than evaluated from scratch at every time step.

This is mathematically neighboring ordinary continuous-time state-space models. S4 and later selective SSMs use the general form

\[
\dot x=Ax+Bu,\qquad y=Cx+Du.
\]

Our restriction is deliberate: choose local block structure in `A` so the state can be advanced lazily and sparsely between asynchronous events.

Recent event-by-event SSM work is therefore a mandatory attacker; the architecture cannot claim `event-driven state space` as new.

---

## 3. Gate MP1 — remove the exponential

Task:

- 12 spatial sensors;
- positives are noisy left-to-right travelling event sheets near a target velocity;
- negatives are reverse trajectories, spatially permuted timing, or wrong-speed trajectories;
- event dropout and distractor events are included;
- geometry supplies structured delays that make the target trajectory arrive approximately coincident at one receiver.

Three receiver bodies were trained only by selecting one internal time parameter and one threshold on a training split:

```text
EXPONENTIAL MASS
    m <- exp(-dt/tau) m + event

LINEAR MASS
    m <- max(0, m - leak*dt) + event

FINITE WINDOW
    count how many delayed events coexist inside width W
```

Held-out result:

```text
exponential + structured delay : 0.99713
linear      + structured delay : 0.99862
window      + structured delay : 0.99925

window + NO delay              : 0.50887
window + shuffled delays       : mean 0.63446, sd 0.10593
                                 best of 32 = 0.87813
```

The result is not that the window detector is a new algorithm. Delay-and-coincidence computation is classic neuroscience and signal processing.

The result for this program is a **kill**:

> **The exponential `mass` state is not required for the first geometry×time task. Geometry + timeout occupancy is enough and is cheaper.**

So the runtime hierarchy should start below leaky integration.

### Biological neighbor

The barn-owl auditory brainstem is an unusually literal example of the design principle. Carr & Konishi measured systematic axonal conduction delays, and later intracellular work supports the circuit interpretation of axonal delay lines feeding coincidence detector neurons for interaural-time differences.

The useful engineering sentence is therefore not `brains use our algorithm` but:

> **A relation that looks like temporal arithmetic to the observer can be converted into local coincidence by arranging propagation delays in the substrate.**

Izhikevich's polychronization and the Tempotron are other mandatory temporal-spike neighbors.

---

## 4. The next compression: sometimes even local analog state is unnecessary

For some computations, digital hardware can represent the material trace more cheaply than an analog-style state.

If an event simply opens an eligibility interval of duration `W`, do not repeatedly decay anything.

Store

```text
expiry_time
```

or schedule a future `REMOVE` event.

Then local runtime is only

```text
on arrival:  count += 1
             schedule count -= 1 at t+W
             if count >= threshold: emit
```

This uses integer changes and event timestamps.

Likewise, if a local state always resets to a fixed amplitude and only its age matters, the entire analog trace can be represented by

```text
last_event_time
```

and reconstructed only if a receiver asks for it.

Thus there are two different optimization targets:

1. **material plausibility** — use a physical-style relaxing state;
2. **digital minimality** — compile that state into timestamps / expiry events when algebra permits.

Do not confuse the two.

---

## 5. Gate MP2 — when does phase / rotation actually earn its cost?

Now price the optional rotating state.

A scalar relaxer has a real stable pole

\[
\lambda=-\alpha.
\]

It represents

\[
e^{-\alpha t}
\]

with one state exactly.

A two-state damped rotational block has

\[
M=-\alpha I+\omega J,
\qquad J^T=-J,
\]

with complex-conjugate poles

\[
-\alpha\pm i\omega.
\]

Starting from `q(0)=[1,0]`, the first coordinate is

\[
x(t)=e^{-\alpha t}\cos(\omega t).
\]

So **two real states represent a damped oscillatory mode exactly**.

### Executed approximation test

Target:

\[
e^{-0.12t}\cos(2\pi\,0.35t),\qquad 0\le t\le20.
\]

The target contains 14 sign changes in the measured interval.

Fit banks of ordinary real decays

\[
\sum_{k=1}^{K} c_k e^{-s_k t}
\]

with signed coefficients and ridge-stabilized least squares.

```text
K= 1   RMSE 0.322197
K= 2   RMSE 0.299493
K= 4   RMSE 0.296727
K= 8   RMSE 0.260116   max |c| ~ 2.5e1
K=16   RMSE 0.211091   max |c| ~ 9.2e3
K=32   RMSE 0.207509
K=64   RMSE 0.203992

one 2-state rotate/decay block: RMSE 0 exactly (analytic construction)
```

The huge coefficients at larger `K` are a warning about ill-conditioned cancellation, not merely parameter count.

There is also a structural reason. Distinct real exponentials form a Chebyshev system: a nontrivial linear combination of `K` such exponentials has a bounded number of zeros (at most `K-1` on an interval under the standard conditions). An oscillatory target accumulates zero crossings with time, so a real-decay bank must grow with the number of oscillations merely to reproduce the sign structure. A conjugate pole pair carries the rotation directly.

This gives the old Geometric-Neuron `phase has to pay its bill` idea a much cleaner implementation meaning:

> **Do not pay for a rotating / phase state to store generic fading memory. Pay for it when the local temporal operator genuinely contains rotation, oscillation, or signed cyclic direction that would be expensive to synthesize from scalar relaxers.**

---

## 6. The decomposition is exactly the old symmetric/skew story, but local and cheaper

For the 2-state resonant block,

\[
M=
\underbrace{-\alpha I}_{\text{symmetric dissipation}}
+
\underbrace{\omega J}_{\text{skew rotation}}.
\]

The symmetric part changes magnitude.
The skew part rotates state and changes orientation without being the dissipative term.

This is much cleaner than saying `all neural phase is special`.

It also reconciles two facts from the older repos:

- amplitude-only / real dynamics can be extremely rich;
- a skew component is the economical object for a local arrow / circulation.

Important boundary: **feed-forward causal delay geometry can distinguish temporal order without a local rotating state.** That does not contradict the old reciprocity result, because a directed delay line is already a causal asymmetric structure, not a passive reciprocal static medium.

So the pricing rule becomes:

```text
need a fixed temporal alignment?       buy DELAY
need a finite coincidence condition?   buy WINDOW / TIMEOUT
need fading scalar history?            buy one RELAX state
need many time scales?                 buy a small RELAX bank
need oscillation / local phase?        buy a 2-D ROTATE block
need nonlinear context dependence?     buy JUMP/threshold/resource state
need long-term adaptation?             buy slow ADAPT only where earned
```

---

## 7. Proposed minimal artificial-neuron ISA v2

### Mandatory core

```text
EVENT(time, type, amplitude?)
ROUTE(target, delay, gain/type)
FLOW(dt)        # only for locations whose state requires it
JUMP(event)
EMIT(condition)
```

### Cheap state blocks

```text
TIMEOUT(W)            one deadline / expiry event
COUNT(W)              integer occupancy in a temporal window
RELAX(tau)            one scalar real pole
RESOURCE(tau, jump)   one slow local history variable
ROTATE(alpha, omega)  two real states / one complex-conjugate pole pair
```

### Slow material layer

```text
ADAPT(edge/local parameter) on selected events
REWIRE rarely
```

No block is universal. The compiler / learner has to earn it.

---

## 8. What this says about `there is no maths`

The phrase should not mean mathematics is irrelevant.

It means the runtime and the analysis live at different descriptive levels.

The runtime may execute only:

```text
wait
receive event
move a local state
schedule another event
compare to threshold
```

An external scientist can still discover that the resulting system implements:

```text
Laplace coordinates
state-space poles
convolutions
observability metrics
skew operators
eigenmodes
```

The mathematical object is often the **compressed external description of repeated causal behavior**, not a symbolic expression stored inside the material.

The strongest concrete example in this note is the Laplace relation:

> a leaky element does not `calculate a Laplace transform`; its physical relaxation makes its instantaneous state equal to a Laplace-weighted integral of past input.

And the second is delay coincidence:

> the receiver does not subtract event timestamps to infer a delay; appropriately routed events simply arrive together.

---

## 9. Where this sits against existing work

Nothing in the individual ingredients is new.

Mandatory neighbors / attackers include:

- exact event-driven integrate-and-fire simulation (Brette 2006/2007);
- axonal delay-line / coincidence circuits in barn owl ITD computation (Carr & Konishi and successors);
- polychronous groups from delays + STDP (Izhikevich 2006);
- Tempotron temporal pattern recognition (Gütig & Sompolinsky 2006);
- leaky-integrator Laplace representations of temporal history (Shankar & Howard 2012 and descendants);
- liquid / continuous-time networks;
- structured state-space sequence models such as S4 and selective SSMs such as Mamba;
- modern event-by-event state-space models for neuromorphic streams.

Therefore the claim to pursue is **not** `we invented event-driven neurons`.

The potentially useful engineering program is narrower:

> **Can a learned compiler select the cheapest local causal blocks (delay, timeout, scalar relax, rotational pair, resource) needed by a task, and thereby match a strong recurrent/state-space baseline while executing work proportional to sparse causal events rather than dense clock ticks?**

That is testable.

---

## 10. Next gates

### MP3 — primitive auction

Give the same task to progressively richer blocks:

```text
DELAY+WINDOW
+ RELAX
+ RESOURCE
+ ROTATE
```

Penalize both error and runtime resource bill.

If a more expensive block does not improve the Pareto frontier, remove it.

### MP4 — learned geometry, not hand-coded geometry

The travelling-sheet gate uses a correct built-in velocity prior. That is intentionally favorable.

Next require the system to infer useful delays from training data and compare with:

```text
small GRU
small TCN
small diagonal SSM
Tempotron-like readout
ordinary event-by-event recurrent model
```

Matched state count and matched communication/event budget are mandatory.

### MP5 — multiple receiver bodies over one WorldSplat state

WorldSplat should not immediately emit full images to every consumer.

Create sparse event streams from changes in scene primitives and test whether task receivers can operate from cheap local bodies:

```text
collision receiver
motion receiver
object-continuity receiver
navigation receiver
```

Each receiver buys only the temporal state it needs.

---

## Carry-forward sentence

> **The minimal artificial neuron may be better understood as a small hybrid material program: silent local FLOW, event-triggered JUMP, geometry encoded as ROUTE/delay, and sparse EMIT. Scalar decay is one optional instruction; a two-state rotation is another. Buy neither unless the task proves it needs them.**

And the deeper design rule remains:

> **Do not calculate a relationship repeatedly if local state and propagation can make the relationship arrive as a coincidence.**
