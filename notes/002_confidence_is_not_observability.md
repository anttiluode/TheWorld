# Note 002 — Confidence is not observability

**Status:** candidate mathematical instrument, not a novelty claim.  
**Date:** 2026-08-19

## 0. Two tensors, not one

A generative world model can be extremely confident about a direction that current external observations barely constrain.

So do not use one covariance / precision object for two different questions.

Let

\[
\Lambda_{\mathrm{belief}}
\]

be the local precision / curvature of the current **total belief**. It can include prior structure, learned regularity, dynamics, constraints, and external observations.

Separately let

\[
A_{\mathrm{ext}}
\]

be a directional **external-support** tensor: information attributable to genuinely external measurements, with common-source / lineage correlations handled rather than blindly double-counted.

For a fresh independent local observation

\[
y=h(x)+\epsilon,\qquad \epsilon\sim\mathcal N(0,R),
\]

the usual local measurement information is

\[
\Delta A = J^TR^{-1}J,\qquad J=D_xh.
\]

A learned prior can sharpen `Lambda_belief`; it must not by itself increment `A_ext`.

This yields a precise form of the WorldModel invariant:

> **low posterior entropy does not imply strong external anchoring.**

---

## 1. The anchor ratio is directional

For a tangent direction `v`, compare external support with total confidence:

\[
r(v)=
\frac{v^T A_{\mathrm{ext}}v}
     {v^T\Lambda_{\mathrm{belief}}v+\varepsilon}.
\]

If the decomposition is constructed so that external information is a positive-semidefinite component of total precision, then `r` has the intuitive range from near 0 (prior/model dominated) toward 1 (largely externally anchored).

The most suspicious direction is

\[
v_* = \arg\min_{v\neq 0}
\frac{v^T A_{\mathrm{ext}}v}
     {v^T\Lambda_{\mathrm{belief}}v}.
\]

This is a generalized eigenvalue problem:

\[
A_{\mathrm{ext}}v = r\,\Lambda_{\mathrm{belief}}v.
\]

A **small generalized eigenvalue** means:

```text
current model:      very sure along v
external world:     has barely constrained v
```

That is more informative than either posterior variance or coverage alone.

Possible scalar summaries:

\[
r_{\min}=\lambda_{\min}(A_{\mathrm{ext}},\Lambda_{\mathrm{belief}})
\]

or an anchor-gap score

\[
g=-\log(r_{\min}+\epsilon).
\]

But the eigenvector `v_*` is probably more useful than the scalar: it tells the active system **what distinction it needs evidence about**.

---

## 2. Active observation can target the missing direction

For candidate sensing action / camera pose `a`, let

\[
\Delta A(a)=J_a^T R_a^{-1}J_a.
\]

A very cheap directional routing rule is

\[
a_*=\arg\max_a
\frac{v_*^T\Delta A(a)v_*}{\mathrm{cost}(a)}.
\]

Interpretation:

> Look where a real measurement is expected to constrain the direction in which belief most outruns evidence.

This is not automatically better than expected information gain, log-det Fisher information, coverage, or active-SLAM objectives. Those are mandatory attackers.

The potentially interesting difference is that the query is defined by a mismatch between **belief geometry** and **external-support geometry**, rather than by uncertainty alone.

---

## 3. The ray-fix gives the perfect concrete example

For a pinhole camera at the origin,

\[
h(X,Y,Z)=\left(\frac{fX}{Z},\frac{fY}{Z}\right).
\]

Its Jacobian is

\[
J=
\begin{bmatrix}
 f/Z & 0 & -fX/Z^2\\
 0 & f/Z & -fY/Z^2
\end{bmatrix}.
\]

Now multiply by the radial world direction

\[
v_r=(X,Y,Z)^T.
\]

Exactly:

\[
Jv_r=0.
\]

So moving a point along the same viewing ray is invisible to that single idealized image observation. The local measurement information

\[
A=J^TR^{-1}J
\]

has a null direction along the ray.

A translated second camera has a different radial null direction. Generically,

\[
\ker J_A \cap \ker J_B
\]

shrinks, which is the local algebra behind triangulation.

This is almost comically close to the current WorldSplat ray-coordinate correction: image-plane ray position and depth should be separate coordinates because **the observation geometry itself treats them differently**.

Important bookkeeping point for the present VKITTI2 experiment:

```text
metric depth used as a training target
    !=
independent metric depth observed at deployment from a monocular RGB frame
```

Depth supervision can teach a powerful RGB-to-depth prior / estimator. At deployment, if the only external input is one RGB camera, predicted depth can still be confident while being prior-dominated. Stereo, active baseline change, RGB-D, lidar, etc. can supply genuinely new geometric support.

That is exactly the situation `A_ext` is meant to distinguish from `Lambda_belief`.

---

## 4. Receiver-specific support

Now combine this with Note 001.

Receiver `i` has local observation/task directions described by a projector `P_i` or Jacobian `H_i`. It may not care whether the whole world is anchored. It cares whether **its relevant distinctions** are anchored.

A simple receiver support score is

\[
s_i = \operatorname{tr}(P_i A_{\mathrm{ext}}P_i),
\]

or, normalized against total belief precision,

\[
q_i=
\frac{\operatorname{tr}(P_i A_{\mathrm{ext}}P_i)}
     {\operatorname{tr}(P_i\Lambda_{\mathrm{belief}}P_i)+\epsilon}.
\]

Then two receivers can rationally behave differently while reading the same world:

```text
receiver A: its relevant directions are well anchored -> act cheaply
receiver B: its relevant direction overlaps v_*       -> probe / route / wait
```

This is the SplatNeuron receiver-specific observation idea meeting WorldModel's support bookkeeping.

---

## 5. Internal sweeps become queries over the gap, not evidence

An internal generative process may traverse candidate states or candidate future viewpoints. It can estimate

\[
J_a,\quad \Delta A(a),\quad \text{or expected task consequence}
\]

for actions that have not yet been executed.

That is valuable computation.

But until an external measurement arrives:

\[
A_{\mathrm{ext}} \text{ does not receive } \Delta A(a).
\]

So imagination can choose the next measurement without becoming that measurement.

This is the cleanest connection so far between the entorhinal / hippocampal sweep intuition and the anchored-world invariant.

---

## 6. Lineage is where simple addition breaks

For independent observations, information terms add nicely.

For descendants of a shared measurement or shared teacher, naïvely adding

\[
J_1^TR_1^{-1}J_1 + J_2^TR_2^{-1}J_2
\]

can double-count common information.

Therefore `A_ext` cannot ultimately be only a matrix. It needs enough lineage / cross-correlation structure to know which support increments are independent.

Mandatory neighboring literatures include distributed data fusion with unknown correlations, common-information filtering, covariance intersection, factor-graph provenance, and data-incest avoidance.

Do not claim novelty until those attackers are implemented.

---

## 7. Next real gate after the toy

When the WorldSplat ray-fix control is finished, do not immediately increase capacity.

The clean representation gate is paired views of the **same** VKITTI2 scene state:

```text
              one W
             /     \
         Camera0  Camera1
            |        |
           I0       I1
```

Then measure, for the actual learned scene representation:

1. the singular spectrum of the Camera0 rendering Jacobian;
2. the weakest externally supported directions;
3. how much Camera1 increases support in those directions;
4. whether confidence-only and entropy-only routing decline a view that anchor-gap routing requests;
5. whether the extra view recovers an actual hidden geometric distinction.

That would be the first non-toy place where the observer-atlas mathematics, the ray-fix lineage, and anchored-world bookkeeping meet in one experiment.

---

## Carry-forward sentence

> **A world model should know not only how sharply it believes each local direction, but how much independent external observation actually earned that sharpness. The difference is a geometry, not a scalar uncertainty.**
