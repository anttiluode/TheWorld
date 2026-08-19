# Note 001 — Observer atlas: partial worlds, directional support, and a finite-width present

**Status:** thinking note, not a result.  
**Date:** 2026-08-19

## 0. Starting point

The intuition is:

> each unit relates to the larger state differently, and therefore each unit has access to a different small part of what the world can do.

The first mathematical correction is important:

> A unit does **not** globally own a nonlinear *subspace*. It owns a nonlinear **observation map**. The differential of that map defines a local observation subspace.

This distinction turns a metaphor into standard geometry and observability.

Let the surrounding world state be a point

\[
x \in \mathcal M,
\]

where `M` may be a learned latent manifold, an explicit splat scene, a neural population state, or a physical state space.

Unit `i` does not receive `x`. It receives

\[
y_i = h_i(x,m_i) + \epsilon_i,
\]

where

- `h_i` is its nonlinear observation map;
- `m_i` is local/private state or history;
- `y_i` is a small output;
- `epsilon_i` is observation noise.

At a particular state `x`, define

\[
J_i(x)=D_x h_i(x,m_i).
\]

Then two useful local objects appear:

\[
\mathcal O_i(x)=\mathrm{row}(J_i(x)) \subset T_x^*\mathcal M
\]

and

\[
\mathcal N_i(x)=\ker J_i(x) \subset T_x\mathcal M.
\]

`O_i` is the set of infinitesimal world directions to which the unit is sensitive. `N_i` is the set of world changes that are locally invisible to it.

Globally, the correct object is not a subspace but the fiber

\[
h_i^{-1}(y_i)=\{x\in\mathcal M:h_i(x)=y_i\},
\]

an equivalence class of worlds that look identical to observer `i`.

This is already the cleanest mathematical form of the SplatNeuron intuition: **a receiver need not possess the sender/world state; it only needs an observation map preserving distinctions relevant to that receiver.**

---

## 1. A population can know more than any unit

Stack the local Jacobians:

\[
J_{\mathrm{pop}}(x)=
\begin{bmatrix}
J_1(x)\\
J_2(x)\\
\vdots\\
J_n(x)
\end{bmatrix}.
\]

Local identifiability requires

\[
\mathrm{rank}(J_{\mathrm{pop}})=\dim \mathcal M.
\]

Equivalently,

\[
\bigcap_i \ker J_i = \{0\}.
\]

Nothing here says that individual units must be semantic specialists. In fact, mixed-selectivity results in cortex argue strongly against expecting neat one-variable neurons. The useful object can be a messy collection of nonlinear local maps whose *population span* contains task-relevant directions.

A useful pairwise quantity is observer overlap. If `P_i` and `P_j` are orthogonal projectors onto the row spaces of `J_i` and `J_j`, then

\[
\Omega_{ij}=\|P_iP_j\|_F^2
\]

measures how much of the same local world geometry the two observers see. Large overlap gives redundancy; small overlap can add complementary information.

This gives a natural **observer graph** whose edge weights are not merely synaptic strength but overlap in observable world directions.

---

## 2. Dendrites make the observation map state-dependent

A deliberately simple branch model is

\[
r_{ib}=\phi_{ib}(w_{ib}^{\top}x),
\]

\[
y_i=\psi_i\left(\sum_b a_{ib}r_{ib}\right).
\]

The local sensitivity is

\[
J_i
=\psi_i'\sum_b a_{ib}\phi_{ib}'\,w_{ib}^{\top}.
\]

The important part is not the exact equation. It is that `phi'_ib` depends on state. A branch that is below, inside, or above a nonlinear regime contributes differently to the local observation geometry. The unit's effective observable directions therefore **change with context**.

This is a reasonable mathematical bridge to dendritic compartmentalization, but it should not be sold as what biological dendrites literally compute.

The Aizenbud et al. 2026 PNAS paper supports three narrower statements:

1. larger dendritic surface and branching are associated with greater modeled single-neuron I/O complexity;
2. dendritic compartmentalization can support semi-independent computational subunits;
3. nonlinear NMDA-mediated integration further increases modeled I/O complexity.

It does **not** establish observer manifolds, world models, or an atlas architecture. That is our extrapolation.

A useful detail from that paper is that simple branch count is not the strongest morphological predictor. Total dendritic area was much more predictive of their FCI than the number of bifurcations, and combinations involving total area and bifurcation extent explained more variance. That argues against a cartoon where `more branches = more computation`; spatial extent, allocation, and nonlinear integration matter together.

---

## 3. Time turns weak instantaneous observers into stronger observers

Let the world evolve as

\[
x_{t+1}=F(x_t,u_t)+w_t.
\]

One instantaneous observer may be rank-deficient. Over a finite time window, dynamics can rotate previously hidden world directions into the observer's visible directions.

For a local linearization with transition Jacobian `A_t=D_xF`, the finite-horizon observability matrix has the familiar form

\[
\mathcal Q_{i,H}=
\begin{bmatrix}
J_{i,t}\\
J_{i,t+1}A_t\\
J_{i,t+2}A_{t+1}A_t\\
\vdots
\end{bmatrix}.
\]

A weighted information / observability metric is

\[
W_{i,H}
=\sum_{\tau=0}^{H}
\gamma_i^{\tau}\,
\Phi_{t\to t+\tau}^{\top}
J_{i,t+\tau}^{\top}R_i^{-1}J_{i,t+\tau}
\Phi_{t\to t+\tau},
\]

where `Phi` transports tangent directions through the dynamics.

This gives a mathematically conservative version of a **wide present**:

> a unit's effective present is the finite temporal window over which dynamics and memory make world directions jointly observable.

Different units can have different `gamma_i`, input geometry, and local dynamics, hence different temporal observation metrics.

This does not require a globally synchronized present or one master buffer.

---

## 4. Eyes closed: transport is not observation

Suppose the system has a current world belief `x_hat_t` and receives a self-motion command `g` (eye/head/body motion). A representation can be transported without external visual input:

\[
\hat x_{t+1}=\rho(g)\hat x_t.
\]

This can preserve trajectories or relative positions while the eyes are closed. But there is a crucial distinction:

\[
\text{transported belief} \neq \text{newly observed world}.
\]

If `A_t` denotes **external directional support**, a coordinate change may transport that support, but prediction must not add a fresh measurement term.

For an invertible local state transform with Jacobian `F_t`, a pure coordinate/dynamics transport has the information-form shape

\[
A^-_{t+1}\approx F_t^{-\top}A_tF_t^{-1}
\]

(up to process-noise handling and the exact state convention).

A genuine external observation adds

\[
\Delta A_{\mathrm{ext}}=J^{\top}R^{-1}J.
\]

So a useful invariant for WorldModel is

\[
A^+_{t+1}=\mathcal T_F(A_t)+\sum_{s\in\mathrm{new\ external\ measurements}}
J_s^{\top}R_s^{-1}J_s,
\]

with **no positive support term for self-generated prediction alone**.

This is the directional version of:

> Prediction may change belief. Prediction is not new evidence.

It also makes the subjective observation that a scene can seem to move with a head turn in darkness computationally unsurprising: an internal state can be transformed by self-motion while becoming progressively less certain. Reopening the eyes supplies innovation that corrects it.

---

## 5. Why the remembered world may feel blurry

Do not equate memory with low spatial frequency by default.

A generic memory model might be

\[
m_{t+1}=Dm_t+By_t,
\]

where the eigenvalues of `D` set different decay times. When sensory input disappears, fast modes decay first and the retained state contracts onto slow modes.

If the representation's slow modes happen to correspond to broad geometry / low spatial frequency, the remaining belief looks like a low-frequency gist. SplatField gives one explicit artificial example where recurrent dynamics preferentially retain particular basis eigenmodes.

But the general mathematical claim is weaker and better:

> **interrupted observation causes the represented world to collapse toward the subspace of modes that the internal dynamics can retain and transport reliably.**

Whether those modes are literally low-frequency image components is an empirical question.

---

## 6. Entorhinal and hippocampal sweeps fit as internal queries, not evidence

Two recent findings are especially relevant.

Vollan et al. reported entorhinal–hippocampal theta-cycle sweeps that extend outward into surrounding locations, including never-visited/inaccessible locations, alternate left/right, and persist during REM sleep. Their coverage model chooses sweep directions that reduce overlap with already sampled surrounding manifold space.

Tang et al. later reported learning- and goal-dependent hippocampal theta sweeps that predict upcoming goal-directed trajectories, coordinate with prefrontal activity, and are preferentially replayed during sharp-wave ripples.

These suggest at least two forms of internal manifold query:

\[
\text{coverage query: sample nearby possible space}
\]

and

\[
\text{goal query: sample task-relevant possible trajectories}.
\]

Within the present framework, an internal sweep can inspect or propagate a world model without adding external support. That is useful: **imagination can guide where to look next without becoming evidence that the imagined location is correct.**

There is also a separate MEC result showing minute-scale population sequences in darkness that can continue through immobility. This is strong evidence for internally organized dynamics, but not evidence that a specific sweep mechanism runs literally `24/7`. Keep those claims separate.

---

## 7. Visual stability probably is not one perfect internal framebuffer

Several results warn against a naive master-canvas picture.

- Extrastriate populations can preserve recent pre-saccadic visual information across the brief sensory interruption of a saccade.
- Predictive remapping and corollary-discharge mechanisms exist in parts of the visuomotor system.
- Yet recordings during natural viewing also show strong fixation-linked / retinotopic responses and only limited evidence for a globally integrated spatiotopic representation in the ventral stream.
- Posterior parietal and hippocampal activity is coordinated around saccades and landmarks, consistent with multiple interacting reference frames rather than one literal pixel buffer.

That is compatible with an **atlas of partial observers**:

```text
world
  |
  +--> observer A: retinotopic feature consequences
  +--> observer B: head/body/world-relative consequences
  +--> observer C: object/landmark consequences
  +--> observer D: action/goal consequences
  +--> observer E: entorhinal spatial consequences
```

The stable experienced world would then be a consistency property of overlapping partial representations and self-motion transforms, not a full-resolution picture stored in one place.

---

## 8. Connection back to the splat repos

### SplatWorld / WorldSplat

A small latent invokes a large coordinated structured hypothesis:

\[
z \mapsto S(z).
\]

### TinyAvatar2

The decoder Jacobian exposes which rendered changes are locally cheap or coupled:

\[
J_D(z)=\frac{\partial S}{\partial z}.
\]

This is already an observation of local manifold geometry.

### SplatNeuron

The surviving result is not `Gabor neuron`. It is receiver-resource geometry: a structured observation vocabulary can reduce repeated logical width when the task aligns with that vocabulary, and the advantage disappears under bad alignment / strong attackers.

### SplatNeuronPlusField

Separates external innovation from recursive projection.

### WorldModel

Adds the missing epistemic object:

\[
\mathrm{World}=(\mathrm{content},\mathrm{support},\mathrm{lineage}).
\]

### Candidate join

The possible new synthesis is therefore not `splats are neurons`.

It is:

> **A rich persistent world can be shared through many small, receiver-specific nonlinear observation maps, while external support is tracked directionally and cannot be manufactured by internal recurrence.**

That is a much narrower and testable statement.

---

## 9. Existing literature boundary

Most ingredients already have strong neighbors:

- nonlinear mixed selectivity and high-dimensional population codes;
- dendritic subunits and branch-specific nonlinear integration;
- predictive remapping / sensory memory across eye movements;
- cognitive maps and entorhinal / hippocampal sweeps;
- nonlinear observability and Fisher-information geometry;
- active view selection / active SLAM;
- object-centric world models and persistent belief states under occlusion;
- local-chart / atlas models for learned manifolds;
- distributed estimation and unknown-correlation fusion.

Therefore **observer atlas** by itself is not a novelty claim.

The narrower thing worth attacking is the combination:

```text
receiver-specific nonlinear observation maps
+
finite-horizon directional observability
+
separate externally anchored support geometry
+
lineage-safe recurrence / communication
+
internal queries that can choose new observations without increasing support
```

If this combination reduces communication / state / sensing cost in a real world-model task versus strong generic alternatives, then there is something to discuss.

---

## 10. First falsifiable gates

### Gate OA0 — prediction does not increase observation rank

Construct a scene with a single-view ambiguity. Compute

\[
A=J^TR^{-1}J.
\]

Repeated internal prediction may transport `A` but may not increase its rank by pretending the same information is new. A second geometrically distinct external view should increase rank if it observes the missing direction.

`experiments/observer_atlas_gate0.py` is the tiny instrument for this.

### Gate OA1 — heterogeneous receivers

Use one persistent scene `W` and several tasks/receivers. Compare matched total communication budget:

1. every receiver gets one global bottleneck `z`;
2. fixed random projections;
3. learned dense receiver maps;
4. compact structured receiver-specific maps.

Score task error, observer-description bits, repeated interface width, receiver compute, and robustness to task rotation.

Expected stop line from SplatNeuron: if dense/random alternatives match at equal resource budget, there is no special observer-vocabulary result.

### Gate OA2 — finite-width present

Keep instantaneous observation width fixed. Compare an instantaneous receiver against a finite-horizon receiver that integrates the same observation map through known dynamics.

Question:

> Can time recover a world distinction that no instantaneous sample contains?

This is standard observability in a new instrument, not a novelty claim by itself.

### Gate OA3 — internal sweep versus external support

Let an internal query search the current generative world for a candidate observation pose. It may change routing / attention / next-view choice, but external support must remain unchanged until a real observation arrives.

Compare:

- confidence-only next view;
- coverage;
- entropy / expected information gain;
- weakest-supported-direction query.

The interesting failure case is a sharp generative posterior that is weakly externally anchored along one hidden direction.

---

## 11. The sentence to carry forward

The original sentence can now be made precise:

> **Each unit owns a small nonlinear observation map of a richer surrounding state. At any moment, the map's Jacobian defines the world directions that unit can distinguish; its nullspace defines the worlds that remain equivalent to it. Across units and across a finite temporal window, these partial views may jointly make a larger world observable.**

And the WorldModel addition is:

> **Internal dynamics may transport and interrogate those partial beliefs, but only external innovation is allowed to add directional support.**

That seems worth testing.

---

## Primary literature touched in this note

- Aizenbud I. et al. (2026), *Dendritic morphology and synaptic nonlinearities enhance functional complexity in human cortical neurons*, PNAS, doi:10.1073/pnas.2533168123.
- Takahashi N. et al. (2023), *Cortico-cortical feedback engages active dendrites in visual cortex*, Nature, doi:10.1038/s41586-023-06007-6.
- Rigotti M. et al. (2013), *The importance of mixed selectivity in complex cognitive tasks*, Nature, doi:10.1038/nature12160.
- Vollan A.Z. et al. (2025), *Left-right-alternating theta sweeps in entorhinal-hippocampal maps of space*, Nature, doi:10.1038/s41586-024-08527-1.
- Tang W. et al. (2026), *Goal-directed hippocampal theta sweeps during memory-guided navigation*, Nature Neuroscience, doi:10.1038/s41593-026-02364-3.
- Gonzalo Cogno S. et al. (2024), *Minute-scale oscillatory sequences in medial entorhinal cortex*, Nature, doi:10.1038/s41586-023-06864-1.
- Akbarian A. et al. (2021), *A sensory memory to preserve visual representations across eye movements*, Nature Communications, doi:10.1038/s41467-021-26756-0.
- Shahidi N. et al. (2024), *Feature-selective responses in macaque visual cortex follow eye movements during natural vision*, Nature Neuroscience, doi:10.1038/s41593-024-01631-5.
- Shao Q. et al. (2024), *A non-canonical visual cortical-entorhinal pathway contributes to spatial navigation*, Nature Communications, doi:10.1038/s41467-024-48483-y.
- Singh G. et al. (2021), *Structured World Belief for Reinforcement Learning in POMDP*, ICML / PMLR 139.
- Mosbach M. et al. (2025), *SOLD: Slot Object-Centric Latent Dynamics Models for Relational Manipulation Learning from Pixels*, ICML / PMLR 267.
