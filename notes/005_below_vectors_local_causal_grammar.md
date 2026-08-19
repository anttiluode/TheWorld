# Note 005 — Below vectors: local causal grammar and physical operators

**Status:** conceptual compression / engineering hypothesis, not a novelty claim.  
**Date:** 2026-08-19

## 0. The discomfort

The brain does not contain explicit vectors, Jacobian matrices, eigendecompositions, or Fourier-transform instructions.

Those are descriptions made by an external observer.

The physical system has matter, charge, conductances, geometry, delays, thresholds, fields, diffusion, and plasticity. The mathematics appears when we choose coordinates and summarize the causal behavior.

So the useful question is not:

> Where in the neuron is the matrix multiplication?

It is:

> What local physical law produces the transformation that a matrix would describe after linearization?

---

## 1. Coordinate description versus physical implementation

Let the complete physical state be `q`.

We write

\[
\dot q = F(q,u).
\]

The biological system does not evaluate `F` symbolically. It **is the physical process represented by `F`**.

Likewise, the Jacobian

\[
J(q)=DF(q)
\]

is not stored anywhere. It is the local input/output consequence we would measure by perturbing the system.

Eigenmodes are not little vectors inside tissue. They are perturbation patterns that reproduce, decay, grow, or rotate in characteristic ways under the dynamics.

This distinction matters because a digital simulator pays to *represent and update* all coordinates explicitly, while the physical substrate evolves all coupled degrees of freedom directly.

That does not make physical computation free. It changes where the cost lives: material, energy, noise, bandwidth, relaxation time, fabrication/development, and adaptability.

---

## 2. A possible lower-level language

Instead of beginning from dense vectors and matrices, describe a physical neural system with a small causal grammar:

1. **state** — local variables that can persist;
2. **couple** — who/what can influence whom;
3. **propagate** — signals move with finite geometry/delay;
4. **integrate** — multiple influences accumulate;
5. **nonlinearize** — thresholds, saturation, coincidence, regenerative events;
6. **relax** — leak, dissipation, diffusion, homeostasis;
7. **modulate** — local state changes gains/time constants/coupling;
8. **adapt** — slower plasticity changes the causal structure.

A generic local law is

\[
\dot q_i
= f_i\left(
q_i,
\{q_j:j\in \mathcal N_{\rm wired}(i)\},
\sum_j K(r_i,r_j)g(q_j),
u_i
\right).
\]

Here `N_wired` can represent addressed synaptic coupling, while `K(r_i,r_j)` represents a metric/shared route such as diffusion or a weak extracellular interaction.

After choosing coordinates and linearizing, the same system may become

\[
\delta \dot q = A\,\delta q + B\,\delta u.
\]

The matrix is a **summary of the local causal grammar**, not necessarily its implementation.

---

## 3. Why a chain can perform a global-looking transform

Take a one-dimensional material/cable with only nearest-neighbor exchange:

\[
q_i(t+1)
= q_i(t)+\eta[q_{i-1}(t)-2q_i(t)+q_{i+1}(t)].
\]

No site knows a Gaussian kernel.

Yet repeated local interaction gives

\[
q(T)=(I-\eta L)^T q(0),
\]

where `L` is the graph Laplacian, and in the continuum limit the impulse response approaches a Gaussian heat kernel.

So a global low-pass/smoothing operator can emerge from **nothing but repeated local causation**.

`experiments/gate3_local_physics_operator.py` verifies this numerically.

This is intentionally standard physics. Its purpose is conceptual: it demonstrates why `the brain would have to calculate a huge matrix` can be the wrong cost model.

---

## 4. Physical depth versus computational depth

Three different meanings of `depth` must remain separate:

### Scene depth

\[
Z_{scene}
\]

distance in the external world.

### Computational/compositional depth

\[
h=h_L\circ h_{L-1}\circ\cdots\circ h_1.
\]

The local sensitivity is a product of transformations:

\[
Dh = Dh_L Dh_{L-1}\cdots Dh_1.
\]

### Anatomical/path depth

Literal distance and number of causal stages through tissue.

Longer anatomical paths can create more delays and more opportunities for nonlinear transformation, but scene depth does not need to map onto anatomical depth.

A 3-D distance can be represented by population state, timing, disparity, phase relations, recurrence, learned object scale, or mixtures of cues.

---

## 5. Material / electrical / field / slow-state layers

A deliberately schematic multi-timescale physical description is

\[
C(m)\dot v
=F_v(v,s,c,m,u)+B\phi,
\]

\[
\dot s=F_s(v,s),
\]

\[
\phi=G(m)I_{membrane}(v,s,c,u),
\]

\[
\partial_t c=D\nabla^2c-\kappa c+Q(v,s),
\]

\[
\dot m=\epsilon F_m(m,v,s,c),\qquad \epsilon\ll 1.
\]

Interpretation:

- `m`: morphology/material structure — the slowly changing bias defining what interactions are easy;
- `v`: membrane voltage/electrical state;
- `s`: synaptic/channel states providing nonlinear and history-dependent transformations;
- `phi`: quasi-static extracellular electric potential, a weak shared metric route;
- `c`: genuinely slow extracellular/chemical state with diffusion/relaxation;
- plasticity/development changes `m` and coupling over much longer times.

This is not offered as a complete brain equation. It is a bookkeeping grammar that prevents collapsing different physical mechanisms into one mystical `field`.

---

## 6. Where the Aizenbud result fits

Aizenbud et al. 2026 support a narrow but important piece of this picture: dendritic morphology and nonlinear synaptic integration affect the complexity of the neuron's input/output transformation.

Their result argues against reducing morphology to `wire carrying scalar input to soma`.

In this language, morphology changes the family of physical transfer functions available to the cell before any abstract network-level interpretation is imposed.

The stronger extrapolation — that morphology implements particular observer charts/world transformations — remains our hypothesis, not their result.

---

## 7. Existing engineering neighbors

This line has obvious neighbors and therefore should not be presented as new by itself:

- analog computing;
- neuromorphic computing;
- physical reservoir computing;
- morphological computation;
- trainable physical neural networks;
- reaction-diffusion computation;
- wave/optical computing;
- in-memory and event-driven computation.

A particularly direct modern example is Wright et al. (Nature, 2022): they train controllable optical, mechanical and electronic physical systems so that the **physical transformations themselves** perform machine-learning computations. Their framing explicitly rejects the requirement that hardware implement every mathematical operation one-for-one.

That is almost the exact engineering version of the intuition here.

---

## 8. Why the brain can look efficient without `using less mathematics`

The brain's advantage is plausibly a mixture of:

- massive physical parallelism;
- memory and computation co-located;
- sparse/event-driven communication;
- low precision where high precision is unnecessary;
- local interactions rather than repeated global memory traffic;
- slow but very low-energy components;
- morphology doing useful preprocessing automatically;
- specialized rather than universally programmable circuits;
- continual reuse of persistent state rather than regenerating everything every frame.

Comparing `~20 W brain` with a supercomputer running an explicit simulation is therefore not an operation-for-operation comparison. The simulator is paying to emulate the substrate on a very different machine.

The potentially useful AI question is:

> **Can we design an architecture whose primitive operations resemble the local causal grammar closely enough that useful computation arises from state evolution rather than from repeatedly materializing dense global transforms?**

---

## 9. Candidate software abstraction

A minimal `physical unit` simulator would expose only:

```text
state
wired_neighbors
metric_position
local_update()
slow_update()
emit()
observe()
```

Then analysis tools may derive Jacobians, spectra, information metrics and effective transfer kernels **afterward**.

That reverses the normal order:

```text
usual ML:
    choose matrix/function -> execute it

physical grammar:
    choose local causal laws -> let system evolve -> measure emergent operator
```

This may be a productive way to build future experiments in TheWorld without pretending the brain explicitly computes our equations.

---

## Carry-forward sentence

> **The mathematics is not necessarily the algorithm the brain executes. It is the external compression of a physical causal process. A useful artificial architecture may therefore be easier to specify as local state, coupling, propagation, nonlinearity and relaxation than as a sequence of explicit global matrix operations.**
