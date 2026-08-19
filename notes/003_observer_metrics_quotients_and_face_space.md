# Note 003 — Observer metrics, quotient geometry, and face space

**Status:** derivation / hypothesis ledger, not a novelty claim.  
**Date:** 2026-08-19

## 0. The sharper object: each observer induces a metric

Let the richer state be

\[
x\in\mathcal M
\]

and observer / receiver `i` measure

\[
y_i=h_i(x)+\epsilon_i,\qquad \epsilon_i\sim\mathcal N(0,R_i).
\]

At `x`, let

\[
J_i=D h_i(x).
\]

The local object is not merely a row-space. It is the positive-semidefinite pullback information metric

\[
G_i(x)=J_i^T R_i^{-1}J_i.
\]

For a tiny world perturbation `dx`,

\[
d_i^2(dx)=dx^T G_i dx
\]

measures local distinguishability to observer `i` in noise units.

This gives one compact object with several interpretations:

- `rank(G_i)` = number of locally distinguishable directions;
- `ker(G_i)` = world changes locally invisible to the observer;
- large eigenvalues = highly sensitive directions;
- zero / tiny eigenvalues = local equivalence directions;
- because `h_i` is nonlinear, `G_i(x)` changes with state.

Globally, the observer defines fibers

\[
h_i^{-1}(y)=\{x:h_i(x)=y\},
\]

so the metric is generally **degenerate**: distinct states can have zero observer-distance because the receiver intentionally identifies them.

This is the mathematical version of:

> different receivers do not merely receive different amounts of the same world; they define different notions of which world differences matter.

---

## 1. Multiple observers add geometry when their evidence is independent

For conditionally independent measurements,

\[
G_{\rm pop}=\sum_i G_i.
\]

Then complementary observers shrink one another's nullspaces.

For correlated measurements, stacking and using the full covariance is the correct object:

\[
y=H(x)+\epsilon,\qquad \epsilon\sim\mathcal N(0,R),
\]

\[
G=J_H^T R^{-1}J_H.
\]

The off-diagonal blocks of `R` are where shared-source / lineage dependence enters. Therefore lineage is not just metadata once estimates interact: it changes how much information may legitimately be added.

This gives a cleaner target for WorldModel than a scalar confidence flag.

---

## 2. Recognition is deliberately throwing information away

Suppose a face-generating state has coordinates

\[
x=(\iota,p,e,\ell),
\]

where

- `iota` = identity;
- `p` = pose / viewpoint;
- `e` = expression;
- `ell` = illumination / appearance nuisance.

A renderer produces

\[
I=R(\iota,p,e,\ell).
\]

Different downstream tasks should induce **different metrics on exactly the same face state**.

An identity receiver should ideally satisfy

\[
\frac{\partial h_{id}}{\partial p}\approx0,\qquad
\frac{\partial h_{id}}{\partial e}\approx0,\qquad
\frac{\partial h_{id}}{\partial \ell}\approx0,
\]

while retaining sensitivity to identity directions.

A pose receiver wants almost the opposite geometry:

\[
\left\|\frac{\partial h_{pose}}{\partial p}\right\|\gg0
\]

and may be nearly invariant to identity.

An expression receiver preserves another set of directions.

So **invariance is a chosen nullspace**.

Recognition can therefore be described as constructing a quotient of the sensory / generative manifold: states that differ only by nuisance transformations are intentionally mapped together.

If a nuisance group `G` acts on a face state, the identity representation is approximately a map on the quotient

\[
\mathcal M/G.
\]

This is the right mathematical connection to 'equivalence relations'.

---

## 3. Why the Jennifer-Aniston cell and the face-space literature fit together

Quian Quiroga et al. (Nature 2005) found medial-temporal-lobe units responding selectively and invariantly to very different images of particular people / objects, and sometimes to their written names. This is evidence for sparse, abstract downstream representations; it is not evidence that one cell alone stores a person.

Chang & Tsao (Cell 2017) found something importantly different earlier in the macaque face system: individual face-patch neurons were well described as projecting faces onto preferred axes in a high-dimensional face-feature space. The population coordinates the face; individual neurons were not simple detectors for particular identities.

These two observations are compatible with a hierarchy such as

```text
retinal variation
    -> local visual features
    -> face-feature coordinate system
    -> increasingly invariant identity representation
    -> sparse concept / associative readouts
```

not as a literal proven serial pipeline, but as a useful distinction between **metric coordinates** and **quotient / concept readouts**.

Freiwald & Tsao (2009) found face-patch neurons tuned to constellations and geometry of facial features. Landi & Freiwald (Science 2017) found temporal-pole and perirhinal areas especially recruited by personally familiar faces, with nonlinear response emergence from blur. Clinical work also links right anterior temporal damage to impaired familiar-person recognition, sometimes across face and voice while name-based access is relatively preserved. That literature makes the 'face geometry -> familiar person association' separation biologically plausible, without implying a one-to-one map onto any individual patient.

Primary references:

- Quian Quiroga R. et al. 2005, Nature 435, 1102–1107. doi:10.1038/nature03687
- Freiwald W.A., Tsao D.Y., Livingstone M.S. 2009, Nature Neuroscience 12, 1187–1196. doi:10.1038/nn.2363
- Chang L., Tsao D.Y. 2017, Cell 169, 1013–1028.e14. doi:10.1016/j.cell.2017.05.011
- Landi S.M., Freiwald W.A. 2017, Science 357, 591–595. doi:10.1126/science.aan1139

---

## 4. This is almost exactly what the splat-face lineage can test

SplatWorld / TinyAvatar already contain a learned face manifold.

TinyAvatar2 showed that the decoder Jacobian

\[
J_D(z)=\frac{\partial S}{\partial z}
\]

reveals local compliant and stiff directions.

The next useful experiment is not another renderer. Use one learned face state and attach several receivers:

```text
same latent z
   |
   +--> identity receiver
   +--> pose receiver
   +--> expression receiver
   +--> appearance / lighting receiver
```

For each receiver compute

\[
G_i(z)=J_i^T R_i^{-1}J_i.
\]

Then measure:

- spectra / effective ranks;
- principal angles between receiver-sensitive subspaces;
- overlap of nullspaces;
- whether known pose directions lie near `ker(G_id)`;
- whether identity directions lie near `ker(G_pose)`;
- how these geometries change across latent locations.

This would turn the receiver-specific SplatNeuron intuition into a real measurement on a learned manifold rather than a toy world.

Strong controls:

1. dense learned probes;
2. random projections at matched width;
3. PCA / CCA baselines;
4. shuffled labels;
5. random-weight decoder;
6. task rotation / misalignment.

Stop line: if all receiver metrics collapse onto the same generic low-rank latent directions, then there is no interesting task-specific atlas.

---

## 5. One world, many task geometries

Let task `k` have loss `L_k` and output `h_k(x)`. Around a state, every task induces its own local metric

\[
G_k=J_k^T W_k J_k
\]

for a suitable output weighting `W_k`.

Therefore there is no reason to expect a single canonical geometry of 'the representation'.

The same state can be:

- close under identity;
- far under pose;
- close under expression;
- uncertain under depth;
- strongly anchored for collision avoidance;
- weakly anchored for semantic interpretation.

This seems closer to cortex than the cartoon `neuron A=red, neuron B=motion, neuron C=face`: a population can support many partially overlapping degenerate metrics at once.

---

## 6. Time simply transports and accumulates these metrics

If

\[
x_{t+1}=F_t(x_t)
\]

with tangent transport

\[
\Phi_{t\to t+\tau},
\]

then an observer's finite-window metric is

\[
G_{i,H}
=
\sum_{\tau=0}^H
\gamma_i^\tau
\Phi_{t\to t+\tau}^T
G_{i,t+\tau}
\Phi_{t\to t+\tau}.
\]

This is Note 001's finite-width present in one line: time can rotate a currently invisible direction into a visible one.

A world difference that is in today's instantaneous nullspace need not remain invisible over a trajectory.

---

## 7. Belief geometry and externally earned geometry are different metrics

Near a MAP estimate, a Bayesian posterior has local curvature roughly

\[
\Lambda_{belief}
\approx
\Lambda_{prior}+G_{ext}
\]

under the usual local-Gaussian approximation.

The prior may make a direction very sharp even when external likelihood contributes little.

Thus the generalized eigenproblem from Note 002

\[
G_{ext}v=r\,\Lambda_{belief}v
\]

finds directions where belief sharpness outruns external support.

The social-reading example has exactly this form in abstract:

```text
brief facial look / posture / context
        -> weak ambiguous likelihood
history + self-model + social prior
        -> strong hypothesis about what the other person meant
```

The hypothesis can be psychologically immediate and still be weakly externally anchored.

The same mathematics applies to monocular depth prediction: one RGB image plus a strong learned world prior can produce a sharp depth belief even though the current image geometry leaves radial directions poorly constrained.

---

## 8. The brain does not need to contain vectors for this mathematics to be true

This is a category error worth removing.

A physical neural system has voltages, conductances, transmitter states, concentrations, morphology, extracellular potentials, etc. Call the total physical state `q`.

The physics evolves as

\[
\dot q=F(q,u).
\]

The brain need not symbolically represent `q` as a vector and it certainly need not calculate a Jacobian matrix.

`q`, `D F`, `G_i`, eigenvectors and manifolds are **our coordinate descriptions of what the physical system does under perturbation**.

A lens does not know Fourier analysis; wave propagation can nevertheless realize a Fourier transform under the appropriate geometry. A cochlea does not run an FFT routine; its mechanics produce an overlapping frequency-selective filter bank. Neurons do not solve differential equations on paper; their material dynamics *are* the differential equations we write down afterward.

So the remarkable fact is not that biology learned symbolic mathematics. It is that evolution and learning shaped physical systems whose causal transformations are compactly described by mathematics.

---

## 9. Material, membrane, field: one coupled physical dynamical system

A conservative multi-scale abstraction is

\[
C(m)\dot v = F_v(v,s,c,m,u)+B\phi,
\]

\[
\dot s=F_s(v,s),
\]

\[
\phi=G(m)\,I_{mem}(v,s,c,u),
\]

\[
\partial_t c=D\nabla^2c-\kappa c+Q(v,s),
\]

\[
\dot m=\epsilon F_m(m,v,s,c),\qquad \epsilon\ll1.
\]

Here `m` is morphology / slow material state, `v` membrane voltage, `s` gating/synaptic state, `phi` extracellular electric potential, and `c` a genuinely slow extracellular milieu variable.

For ordinary low-frequency extracellular cortical fields, `phi` should first be treated quasi-statically rather than given free autonomous wave memory. Eliminating it yields a geometry-induced effective coupling term. Experiments show weak extracellular fields can modulate membrane potential and entrain / coordinate spiking, especially for slow fluctuations, but 'the field enslaves the population' is stronger than the evidence warrants.

The conceptual point is enough:

> morphology constrains the operator; membrane and synaptic states make it nonlinear and history-dependent; extracellular geometry can add a shared coupling route; slow plastic / material variables change the operator itself.

Aizenbud et al. 2026 strengthens the first two pieces: dendritic extent / branching and nonlinear NMDA integration increase the I/O complexity of detailed neuron models. It does not establish the observer-metric architecture above.

---

## 10. Three different meanings of depth

Do not collapse these:

1. **scene depth** `Z` — a hidden geometric property of the outside world;
2. **causal / computational depth** `L` — how many nonlinear transformations are composed before a readout;
3. **anatomical depth / path length** — where a signal travels through tissue and circuitry.

A signal travelling through `L` stages implements the composition

\[
h=h_L\circ h_{L-1}\circ\cdots\circ h_1.
\]

Its sensitivity is

\[
Dh=Dh_L\,Dh_{L-1}\cdots Dh_1.
\]

This is why 'a path like a vector' is suggestive but should be translated carefully: physical propagation through successive nonlinear elements creates a composed transformation. Scene depth need not be literally encoded by anatomical depth, although a system is free to exploit topography, timing, population axes or any other physical code.

---

## Carry-forward statement

> **A receiver induces a task-specific, generally degenerate information metric on a richer world. Recognition is partly the deliberate creation of null directions: pose, lighting or modality differences become equivalent while identity survives. Different receivers quotient the same world in different ways. Across receivers and time, the sum of these partial metrics can make distinctions observable that no single unit contains.**

And the anchored-world addition remains:

> **The metric of what the model believes is not the metric of what independent external evidence has earned.**
