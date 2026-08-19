# TheWorld — FLOW/JUMP + receiver-specific realization handoff

**Date:** 2026-08-19  
**Status:** current working handoff after the Mass–Pulse ablations and receiver-specific Hankel gate.

## One-line state

> **Do not define the artificial neuron by a preferred equation. Learn/identify the smallest receiver-specific dynamical realization, compile it into the cheapest local causal primitives that preserve its behavior, and execute only when causal events require work.**

This is an engineering synthesis of established ingredients, not a novelty claim.

---

## 1. What was killed today

The first Mass–Pulse sketch assumed local exponential `mass` as a default state.

Gate MP1 killed that as a universal primitive.

On a noisy 12-sensor travelling-event task:

```text
exp + structured delay       0.99713
linear + structured delay    0.99862
window + structured delay    0.99925

window + no delay            0.50887
window + shuffled delay      0.63446 mean
```

So the first geometry×time task does not earn analog exponential state at all.

The correct abstraction is lower:

```text
FLOW(dt)
JUMP(event)
ROUTE(delay)
EMIT(test)
ADAPT(optional/slow)
```

Some units may implement `FLOW = nothing` plus expiry/window bookkeeping.

---

## 2. Current primitive price list

```text
DELAY(d)               schedule consequence later
WINDOW(w)              finite coexistence / coincidence
RELAX(alpha)           one real fading state
RESOURCE(alpha,jump)   one extra history-dependent state
ROTATE(alpha,omega)    two-state damped rotation
THRESHOLD(theta)       sparse event emission
RESET / REFRACT        post-emission local change
ADAPT                  slow material change
```

Do not make every unit carry all of these.

The central question is which local dynamics a receiver actually earns.

---

## 3. Clean bill for phase / rotation

One scalar relaxer exactly carries one real decaying mode:

\[
\dot x=-\alpha x.
\]

Two coupled real states carry one damped rotational mode:

\[
\dot q=(-\alpha I+\omega J)q,
\qquad
J=\begin{bmatrix}0&-1\\1&0\end{bmatrix}.
\]

Executed approximation test for a damped cosine with 14 sign changes:

```text
1 scalar decay      RMSE .322197
2                   .299493
4                   .296727
8                   .260116
16                  .211091
32                  .207509
64                  .203992

one 2-state rotation/decay block
                    RMSE 0
```

Interpretation:

> **One scalar state buys relaxation. Two coupled states buy genuine rotation.**

This is the most economical surviving implementation reading of the old Geometric-Neuron `phase must pay its bill` idea.

Do not use `ROTATE` for generic memory. Use it where the receiver's temporal operator actually contains oscillatory/cyclic structure.

---

## 4. New core mathematical object: receiver-specific minimal realization

Earlier observer-atlas work asked which instantaneous world directions a receiver can distinguish.

For local linear dynamics

\[
x_{t+1}=Ax_t+Bu_t,
\qquad y_i=C_i x_t,
\]

the impulse response is

\[
h_k=C_iA^kB.
\]

Build a Hankel matrix from the impulse-response sequence.

For an exact minimal finite-dimensional LTI system, Hankel rank gives the minimal dynamical order under the usual controllability/observability conditions.

This gives a stronger version of the SplatNeuron sentence:

> **A receiver only needs a minimal dynamical realization of the world's consequences that can actually reach that receiver.**

Same world need not imply same local state dimension.

---

## 5. Executed six-state receiver gate

One shared stable six-state world contained:

```text
1 slow scalar mode
1 fast scalar mode
1 two-state damped rotational mode
1 second two-state damped rotational mode
```

One impulse excites all six.

Different receiver readouts give:

```text
slow-only receiver          Hankel rank 1
oscillation-only receiver   Hankel rank 2
fast-only receiver          Hankel rank 1
mixed receiver              Hankel rank 6
```

Leading singular values:

```text
slow       [14.200, 0, 0, 0, 0, 0]
osc        [4.670, 4.582, 0, 0, 0, 0]
fast       [1.333, 0, 0, 0, 0, 0]
mixed      [8.417, 2.634, 2.404, .508, .300, .054]
```

This is expected systems theory. The point is the bridge:

```text
rich shared world
      ↓
receiver-specific consequence map
      ↓
receiver-specific dynamic degree
      ↓
compile only that degree into material primitives
```

If real learned receivers all retain broad/full Hankel spectra, this compression story loses.

---

## 6. Candidate compiler

For receiver `i`, identify/learn an approximate transfer behavior

\[
H_i(s).
\]

Factor it into cheap blocks:

\[
H_i(s)\approx D
+\sum_r\frac{a_r}{s+\alpha_r}
+\sum_c\frac{b_cs+c_c}{(s+\alpha_c)^2+\omega_c^2}
\]

plus explicit delay factors

\[
e^{-sd}.
\]

Map terms to runtime:

```text
D                                -> JUMP/direct read
1/(s+alpha)                      -> RELAX
quadratic conjugate-pole block   -> ROTATE
exp(-s d)                        -> ROUTE/DELAY
```

Then add nonlinear `WINDOW`, `RESOURCE`, threshold, saturation, etc. only if the linear realization cannot preserve the needed behavior.

This is system identification/model reduction plus a sparse event runtime; those ingredients are established.

The testable engineering question is whether this compilation is useful at matched task quality and actual runtime/communication cost.

---

## 7. WorldModel / WorldSplat connection

Do **not** change the running/current WorldSplat architecture because of this theory.

After the ray-fix gate is complete, define receivers over one learned world:

```text
RGB synthesis
depth summary
image-plane motion
collision / near-field hazard
navigation
object continuity
```

For each receiver, estimate empirical dynamic spectra from controlled trajectories/perturbations.

Desired receipt would look like:

```text
RGB receiver          effective degree high
collision receiver    effective degree very low
motion receiver       intermediate
```

Then compile only the low-degree receivers into FLOW/JUMP bodies.

If all receiver spectra remain broad, do not claim a cheap observer atlas.

---

## 8. Wide Present refinement

A receiver's temporal present should not be summarized by one buffer length.

Use at least two quantities:

```text
H_i       useful history horizon
r_i(H)    effective dynamical degree over that horizon
```

So a receiver may have a long temporal horizon but only a few surviving slow modes, or a short horizon with many interacting fast modes.

Candidate sentence:

> **The present is the horizon over which past state remains causally useful, together with the number of dynamical distinctions that must survive across that horizon for this receiver.**

---

## 9. MP3 — next actual build: primitive auction

Give a learner explicit primitive costs:

```text
DELAY
WINDOW
RELAX
RESOURCE
ROTATE
```

Objective:

\[
L=L_{task}
+\lambda_s N_{states}
+\lambda_e N_{eventops}
+\lambda_c N_{communicated\ events}.
\]

Task families:

```text
temporal coincidence
fading recency
history-dependent transmission
true periodic/cyclic structure
```

Registered qualitative prediction:

```text
coincidence      -> DELAY/WINDOW
recency          -> RELAX
history context  -> RESOURCE
oscillation      -> ROTATE
```

Mandatory matched attackers:

```text
compact GRU
compact LSTM
small TCN
small diagonal/structured SSM
point-spiking baseline
```

If a compact ordinary recurrent/SSM model wins the resource frontier, the material-ISA story loses.

---

## 10. Runtime warning

Operation count is not GPU speed.

Sparse event execution can lose badly on ordinary GPUs because of:

```text
queue/scheduling overhead
scattered memory access
branching
poor SIMD occupancy
small irregular kernels
```

Eventually benchmark at least:

```text
dense PyTorch baseline
batched sparse GPU runtime
CPU event runtime
```

The stopwatch is mandatory.

---

## 11. Carry-forward stack

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
compile to cheapest FLOW/JUMP primitives
        ↓
execute only on causal events
        ↓
keep external-support / provenance ledger separate
```

Epistemic anchoring and receiver compression are distinct problems. A tiny receiver can still be confidently wrong.

The strongest sentence to preserve:

> **A neuron-like artificial element need not calculate the mathematical operator we use to describe it. A tiny local causal program can have that operator as its emergent input/output behavior; and each downstream receiver should carry only the smallest dynamical realization needed to preserve the consequences of the richer world that matter to it.**

Do not hype. Do not lie. Keep attacking.
