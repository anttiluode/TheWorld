# Note 008 — Receiver-specific minimal realization

**Status:** control-theoretic synthesis + toy gate; not a novelty claim.  
**Date:** 2026-08-19

## 0. The dynamic version of the observer-atlas sentence

Earlier notes used a receiver-specific observation map

\[
y_i=h_i(x)
\]

and local metric

\[
G_i=J_i^TR_i^{-1}J_i,
\qquad J_i=Dh_i(x),
\]

to ask which instantaneous world directions receiver `i` can distinguish.

Once the world has dynamics, there is a stronger question:

> **How much dynamical state does receiver `i` actually need in order to reproduce every consequence of the world that can reach that receiver?**

For a local linearization,

\[
\dot x=Ax+Bu,
\]

\[
y_i=C_i x+D_i u.
\]

The receiver transfer function is

\[
H_i(s)=C_i(sI-A)^{-1}B+D_i.
\]

The full world may have state dimension `n`, but the minimal realization degree of `H_i` can be much smaller.

This is standard realization/control theory. The connection to this project is unusually direct:

> **`a receiver only needs the sender/world's observable consequences` becomes `a receiver only needs a minimal realization of the input→output dynamics relevant to that receiver`.**

This is a candidate mathematical core for the SplatNeuron / observer-atlas / minimal-material-neuron synthesis.

---

## 1. Static observer rank versus dynamical degree

The instantaneous Jacobian tells us what can be distinguished at one state/time.

A finite temporal window can expose modes that are not visible in one instantaneous sample.

For linear discrete-time dynamics

\[
x_{t+1}=Ax_t+Bu_t,
\qquad y_t=Cx_t,
\]

the impulse response is

\[
h_k=CA^kB.
\]

Build a Hankel matrix from this sequence:

\[
\mathcal H=
\begin{bmatrix}
h_0&h_1&h_2&\cdots\\
h_1&h_2&h_3&\cdots\\
\vdots&\vdots&\vdots
\end{bmatrix}.
\]

For an exact finite-dimensional minimal LTI realization, the Hankel rank equals the minimal system order under the usual controllability/observability conditions.

So the **dynamic receiver degree** is not merely `rank(C)` or `rank(J_i)`.

It asks how many distinct internal modes survive the full input→world→receiver path through time.

---

## 2. One world can have radically different minimal receivers

Executed toy:

One shared stable six-state world contains:

```text
mode 1      slow scalar relaxation
mode 2      fast scalar relaxation
modes 3-4   damped rotational pair
modes 5-6   second damped rotational pair
```

One impulse excites all six modes.

Four receiver matrices read different consequences.

Measured Hankel singular spectra:

```text
slow-only receiver:
    rank 1
    [14.200, 0, 0, 0, 0, 0]

oscillation-only receiver:
    rank 2
    [4.670, 4.582, 0, 0, 0, 0]

fast-only receiver:
    rank 1
    [1.333, 0, 0, 0, 0, 0]

mixed receiver:
    rank 6
    [8.417, 2.634, 2.404, 0.508, 0.300, 0.054]
```

Same six-state world.
Different receiver.
Different dynamical degree.

The result is mathematically expected. Its value is conceptual:

```text
WORLD state dimension            = 6
slow receiver's needed degree    = 1
oscillatory receiver's degree    = 2
mixed receiver's needed degree   = 6
```

So there is no reason every downstream unit should carry one universal world bottleneck of the same width.

---

## 3. This is a stronger SplatNeuron interpretation

The useful surviving SplatNeuron statement was approximately:

> a receiver only needs enough of the sender's observable consequences to preserve distinctions relevant to that receiver.

In a dynamical setting, replace generic `enough` with a measurable object:

\[
\text{receiver degree} \approx \text{effective Hankel rank / minimal realization order}.
\]

Then interface cost can be asked honestly:

```text
full persistent world        n states
receiver A                   r_A states
receiver B                   r_B states
...
```

with

\[
r_i\ll n
\]

only when the world→receiver dynamics actually permit that compression.

This also supplies an attacker against hand-wavy `each unit owns a little world` language:

> If the empirical Hankel spectrum for a receiver is full-rank and flat, then the receiver does not have a cheap low-order dynamical view. The desired compression is not there.

---

## 4. FLOW/JUMP becomes a realization target

Now combine Note 007 with realization theory.

A stable real linear system can be decomposed into real modal/Schur blocks.

The primitive library maps naturally onto those blocks:

```text
real stable 1-D mode
    -> RELAX(alpha)

complex-conjugate pole pair
    -> ROTATE(alpha, omega)

explicit propagation time
    -> ROUTE(delay)

instantaneous feedthrough
    -> JUMP / direct gain
```

For a diagonalizable transfer, schematically:

\[
H_i(s)
\approx
D_i
+\sum_r \frac{a_r}{s+\alpha_r}
+\sum_c
\frac{b_c s+c_c}{(s+\alpha_c)^2+\omega_c^2}
\]

with optional explicit delay factors

\[
e^{-sd}.
\]

The correspondence is direct:

```text
1/(s+alpha)                         RELAX
quadratic damped-oscillator term    ROTATE pair
e^{-sd}                             ROUTE delay
D                                   immediate JUMP/read
```

This suggests a literal **receiver compiler**:

1. identify/learn the input→receiver impulse/step behavior;
2. estimate the smallest useful dynamic degree;
3. factor it into cheap real modes, rotational pairs, and delays;
4. instantiate only those local blocks;
5. add nonlinear thresholds/resources only if linear blocks fail.

This is system identification / model reduction territory, not a new theorem.

The potential engineering contribution would be sparse heterogeneous compilation into an event runtime.

---

## 5. Hankel singular values are a dynamic observer budget

Raw rank is brittle under noise.

The useful empirical object is the singular spectrum

\[
\sigma_1\ge\sigma_2\ge\cdots.
\]

A receiver with rapidly decaying singular values may admit a low-order approximation even when exact algebraic rank is high.

Define an approximate degree at tolerance `epsilon`, for example

\[
r_i(\epsilon)
=
\min\left\{r:
\frac{\sum_{k>r}\sigma_k^2}
     {\sum_k\sigma_k^2}
\le\epsilon
\right\}.
\]

Now the receiver's resource width becomes a measured accuracy/resource tradeoff.

This is more useful for real neural/world-model data than exact rank.

It also aligns naturally with SplatNeuron's resource accounting:

```text
observer description bits
+
receiver state count
+
per-event operations
+
interface event rate
+
approximation error
```

---

## 6. Wide Present gets another clean interpretation

The finite Hankel matrix maps past input history to future receiver consequences.

Its effective rank and singular spectrum depend on the horizon used to build it.

So a receiver's `wide present` can be characterized by two quantities:

```text
H_i       useful temporal horizon
r_i(H)    number of dynamical modes needed over that horizon
```

A receiver may have:

```text
short horizon, low degree
long horizon, low degree
short horizon, high degree
long horizon, high degree
```

There is no need for one global memory width.

This sharpens the earlier finite-observability idea:

> **the present is not only how far history matters; it is how many dynamical distinctions survive across that history for this receiver.**

---

## 7. This tells us how to join WorldSplat without shipping the whole world

Suppose one persistent world state is `W`.

Different receivers care about different consequences:

```text
collision
navigation
visual synthesis
object persistence
semantic identity
```

Do not begin by giving every receiver the same `z`.

Instead estimate receiver-specific dynamic maps:

\[
W,u \rightarrow y_i.
\]

Then ask whether each map has a low-order realization.

Example:

```text
WORLD               512 splats / rich latent

collision receiver
    may only require a few near-field distance/velocity modes

navigation receiver
    may require slow free-space/topology modes

appearance renderer
    may require many texture/illumination modes
```

This is a concrete, falsifiable version of the observer atlas.

If all receivers empirically require nearly full world degree, the architecture loses.

---

## 8. Connection to external support / anchored world

Minimal realization describes what a receiver needs to **predict its consequence**.

It does not tell us whether those receiver states are externally anchored.

Keep the earlier split:

```text
receiver belief state
receiver dynamic degree
external support geometry
source/intervention lineage
```

A one-state receiver can still be confidently wrong.

So compression and epistemic anchoring are orthogonal problems.

This matters for WorldModel:

> **A tiny receiver model is allowed to inherit a huge prior. The support ledger must still say which of its decisive modes are currently constrained by real observations.**

---

## 9. Next experiment: empirical receiver compiler

Do not use another toy linear system after this note.

Use an already learned nonlinear model.

### Candidate A — TinyAvatar/SplatWorld

Perturb latent trajectories and measure outputs for receivers:

```text
pose
identity
expression
illumination
```

Build empirical input/output Hankel matrices around trajectories.

Question:

> do different receivers have sharply different effective dynamic degrees?

### Candidate B — WorldSplat after the current ray-fix run

Use changes across adjacent VKITTI frames / controlled latent perturbations.

Candidate receivers:

```text
RGB reconstruction
metric-depth summary
near-field collision proxy
image-plane motion
```

Measure empirical Hankel spectra.

If the collision receiver has degree 3 while RGB synthesis has degree 60+, that is the first quantitative receipt for `different receivers own differently sized worlds`.

---

## 10. Carry-forward

The earlier sentence was:

> Each unit has a small nonlinear observation map of a richer surrounding state.

The dynamic refinement is:

> **Each receiver may require only a low-order realization of the surrounding world's dynamics. The size of that local world is not a metaphor: in the linearized case it is measured by the input→output Hankel spectrum/minimal realization degree.**

And the material-runtime refinement is:

> **Compile that low-order realization into the cheapest local FLOW/JUMP blocks its pole structure requires, then execute only when causal events touch it.**

That is currently the cleanest bridge between SplatNeuron, WidePresent, GeometricNeuronV23, and WorldModel.
