# Note 004 — Intrinsic dimension, movement ecology, and spatial codes

**Status:** literature-grounded derivation / hypothesis ledger, not a novelty claim.  
**Date:** 2026-08-19

## 0. The hunch

A surface-dwelling animal lives in a 3-D world but often moves on a much lower-dimensional subset of it.

That suggests separating:

- **embedding dimension** — the dimension of physical space around the animal;
- **behavioral / reachable dimension** — the intrinsic dimension of the states the animal actually occupies;
- **sensory dimension** — the dimensionality of the immediate observation surface;
- **task dimension** — the number of distinctions a receiver actually needs.

A human walking on ordinary terrain may spend most locomotor time on a roughly 2-D manifold embedded in 3-D. A flying animal can use more of the surrounding volume, but even flight trajectories can be structured onto lower-dimensional subspaces.

The claim to test is not `humans have a 2-D brain map and birds have a deeper 3-D map`.

A better hypothesis is:

> **Spatial codes adapt to the intrinsic dimension and geometry of behaviorally relevant state space, which need not equal the Euclidean dimension of the environment.**

---

## 1. The dimensionality tax

For a state manifold of intrinsic dimension `d`, the number of local patches of radius `epsilon` needed to cover it scales roughly as

\[
N(\epsilon) \propto \epsilon^{-d}.
\]

So holding resolution fixed while moving from a 2-D surface to a 3-D volume can be very expensive.

This is arithmetic, not a neuroscience discovery. It simply says that a volumetric map has a larger covering number than a surface map at the same local resolution.

`experiments/gate1_intrinsic_dimensionality.py` is a tiny numerical illustration. With the registered radius and coverage target, a regular local-code lattice needs tens of centres for a 2-D sheet but hundreds for a 3-D volume.

The important control is an embedded 2-D sheet in 3-D: it costs like 2-D, not like 3-D. The relevant quantity is intrinsic dimension.

---

## 2. One eye view is a 2-D angular observation of a 3-D world

For a camera or eye at a point, ignoring lens details, visible direction can be represented by two angular coordinates.

A pinhole observation maps

\[
(X,Y,Z) \mapsto (u,v) = (fX/Z, fY/Z).
\]

So a single instantaneous view has a 2-D observation surface while the visible world contains depth.

Every image location corresponds to a ray/fiber of possible 3-D points:

\[
\{\lambda (X,Y,Z) : \lambda > 0\}.
\]

Depth cues from binocular disparity, motion parallax, occlusion, perspective, familiar size, shading, etc. progressively break those equivalences.

This is exactly the observer-fiber language from Notes 001–003.

The retina need not be a 3-D map for an organism to estimate 3-D structure. Several observer maps over time can constrain depth.

---

## 3. What the comparative literature actually says

### Surface-dwelling mammals

In rats moving on vertical surfaces, place/grid representations are anisotropic: vertical position is generally represented less precisely than horizontal position. This is consistent with the idea that the code reflects movement ecology rather than treating all Euclidean axes identically.

### Flying bats

The strongest directly comparable medial-entorhinal result is from freely flying bats. 3-D border cells, 3-D head-direction cells, and multifield/grid-like cells exist. However, 3-D grid fields showed **local order without a global 3-D lattice**. That is already evidence that the 2-D hexagonal story does not simply extrude into a 3-D crystal.

A June 2026 preprint goes further: large-scale wireless recordings during 3-D bat flight reported ensemble topology consistent with a **2-D toroidal grid manifold**, while behavioral flight paths were organized along approximately planar subspaces. The authors argue that a 2-D grid code can align to behaviorally relevant planes inside a 3-D world.

That result is not peer reviewed yet. It is nevertheless almost exactly the distinction this note is making: **behavioral intrinsic dimension can be lower than embedding dimension.**

### Birds

Birds do not have a mammalian medial entorhinal cortex that is simply made `deeper`. Their hippocampal formation is considered homologous in broad function/developmental position but is organized very differently anatomically.

In freely flying barn owls, hippocampal neurons encode spatially restricted 3-D positions, flight direction, and perch position; many cells multiplex these variables.

In chickadees, a 2025 Nature study found an especially relevant phenomenon: hippocampal place cells activated not only when the bird occupied a place but also when it **gazed at that remote place**. Head-saccade cycles alternated between an internal prediction of what would be seen and a response to what was actually seen.

That result strongly argues against a simple `place cell = current body coordinate` interpretation. A spatial code can represent the **currently relevant remote location** as selected by gaze.

---

## 4. A possible unification: relevant-state dimension

Let physical space be `E`, behavior occupy a manifold

\[
\mathcal B \subset E,
\]

and a receiver care about a task map

\[
h_i : \mathcal B \to Y_i.
\]

Three dimensionalities can differ:

\[
\dim E \neq \dim \mathcal B \neq \operatorname{rank}(Dh_i).
\]

Example:

```text
physical world:            3-D
walking trajectory:        ~2-D surface
retinal observation:       2-D angular sheet
collision-control output:  maybe only a few task directions
```

A bird/bat can increase `dim(B)` by using altitude freely, but a stereotyped flight corridor can still be locally near-2-D.

This suggests that evolution does not need to allocate a full uniform Euclidean map. It can allocate representation to the dimensions actually used.

---

## 5. Circular walls / egocentric visual cone

The intuitive picture of `I am a point, with a circular visual world around me, looking into one sector` is useful if we separate coordinate frames.

At an instant, visual input is naturally egocentric:

```text
self point
   |
   +-- angular ray field / field of view
```

But navigation and object memory need transformations between:

- retinal / eye-centered coordinates;
- head-centered coordinates;
- body-centered coordinates;
- allocentric / world-centered coordinates;
- object-centered coordinates.

The stable world need not be one giant spherical framebuffer. It can be the consistency relation among these maps plus self-motion transforms.

That is compatible with the observer-atlas view: different circuits preserve different quotient geometries of the same situation.

---

## 6. Prediction for artificial world models

Do not force every receiver to consume a full isotropic 3-D latent.

Instead measure the intrinsic dimension of the trajectories/tasks actually used.

For a learned world `W`, estimate local task Jacobians and singular spectra:

\[
J_i = D h_i(W).
\]

If a navigation controller uses only a rank-`r` subspace, communicate/maintain that subspace rather than the whole scene representation.

This is exactly where SplatNeuron's receiver-resource result can meet WorldModel.

---

## 7. Stop lines

This note does **not** support:

- birds having a `deeper entorhinal cortex`;
- humans having only a 2-D representation of space;
- 3-D navigation requiring a literal 3-D topographic neural lattice;
- mapping anatomical depth onto scene depth;
- calling the 2026 bat preprint settled fact.

The supported direction is narrower:

> **Neural spatial representations can be anisotropic and species/task dependent; the dimensionality and geometry of behavior may be more important than the ambient Euclidean dimension alone.**

---

## 8. Literature anchors

- Ginosar et al. (2021), *Locally ordered representation of 3D space in the entorhinal cortex*, Nature.
- Agarwal et al. (2023), *Spatial coding in the hippocampus and hyperpallium of flying owls*.
- Payne & Aronov (2025), *Remote activation of place codes by gaze in a highly visual animal*, Nature.
- Qi & Yartsev (2026 preprint), *A Two-Dimensional Grid-Cell Code for Three-Dimensional Navigation in Freely Flying Bats*.
- Hayman et al. (2011), *Anisotropic encoding of three-dimensional space by place cells and grid cells*, Nature Neuroscience.
