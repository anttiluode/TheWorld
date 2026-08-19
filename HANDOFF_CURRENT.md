# TheWorld — current handoff

**Date:** 2026-08-19  
**State:** thinking ledger with three executed headless smokes; no architecture claim yet.

## One-line state

> **Treat a rich world as a physical/dynamical state that supports many receiver-specific observation geometries. Track not only what the model believes and which directions external measurements support, but also the causal lineage by which belief-driven actions changed later observations.**

---

## 1. The strongest mathematical object so far

A receiver `i` observes a richer state `x` through

\[
y_i=h_i(x)+\epsilon_i,
\qquad \epsilon_i\sim\mathcal N(0,R_i).
\]

Local Jacobian:

\[
J_i=Dh_i(x).
\]

Receiver-specific information metric:

\[
G_i=J_i^TR_i^{-1}J_i.
\]

For local perturbation `dx`,

\[
d_i^2=dx^TG_idx
\]

is how distinguishable that change is to receiver `i`.

Interpretation:

- `ker(G_i)` = world changes invisible to receiver `i`;
- eigenvectors/eigenvalues = directions and strengths of local distinguishability;
- different receivers induce different geometries on the same underlying state;
- nonlinear observation maps make these geometries state dependent.

Global version:

\[
x_1\sim_i x_2 \iff h_i(x_1)=h_i(x_2).
\]

So a receiver defines an **equivalence relation / quotient** over possible worlds.

This is cleaner than `neuron A knows red, neuron B knows motion`.

---

## 2. Confidence is not observability

Keep separate:

\[
\Lambda_{belief}
\]

(total posterior/belief precision, including prior/model structure)

and

\[
A_{ext}
\]

(directional information genuinely earned from external observations).

A strong learned prior can make `Lambda_belief` sharp where `A_ext` is weak.

Directional anchor ratio:

\[
r(v)=\frac{v^TA_{ext}v}{v^T\Lambda_{belief}v+\epsilon}.
\]

Weakest-supported relative-to-confidence direction:

\[
A_{ext}v_*=r_*\Lambda_{belief}v_*.
\]

Small `r_*` means:

```text
model is sharp along v*
external measurements barely earned that sharpness
```

Candidate active query:

\[
a_*=\arg\max_a
\frac{v_*^T\Delta A(a)v_*}{cost(a)}.
\]

Mandatory attackers: entropy/information gain, Fisher/logdet, coverage, active SLAM, ordinary uncertainty routing.

---

## 3. New today: external evidence can still be endogenous

For an acting model:

\[
a_t=\pi(b_t),
\]

\[
x_{t+1}=F(x_t,a_t,w_t),
\]

\[
y_{t+1}=h(x_{t+1},a_t)+\epsilon_t.
\]

Belief can change action; action can change the world/other agent; later observation then shares causal ancestry with the belief being confirmed.

Support bookkeeping therefore needs more than `external/internal`:

1. exogenous measurement;
2. active-sensing measurement (viewpoint/query chosen by model, scene geometry conditioned on known action);
3. intervention-mediated measurement (model action changed the latent world before observation);
4. recursive internal prediction (no new measurement).

Future provenance likely needs both:

```text
source lineage
+
intervention lineage
```

This is standard causal/control territory in ingredients; novelty not claimed.

---

## 4. Executed headless smokes

Results are frozen in `results/2026-08-19_headless_smokes.txt`.

### Gate 1 — intrinsic dimensionality

Registered:

```text
samples=20,000
local radius=.10
target coverage=.95
```

Result:

```text
2-D sheet:               49 centres, coverage .99980
same 2-D sheet in 3-D:   49 centres, coverage .99980
3-D volume:             343 centres, coverage .95835
ratio:                    7.0x
```

Interpretation only: covering number follows intrinsic dimension, not embedding dimension.

This does not prove a neural map architecture.

### Gate 2 — endogenous evidence

Toy:

\[
a_t=\tanh(\mu_t),
\]

\[
y_t=\theta+\beta a_t+\epsilon_t,
\qquad \theta=0.
\]

Naive observer ignores the action-caused component.

Noiseless fixed point:

\[
\mu=\beta\tanh\mu.
\]

At `beta>1`, zero becomes unstable and two non-zero self-confirming attractors appear.

Executed 1,000-seed result at `beta=1.2`:

```text
naive      mean mu = +0.75314, |mu|>.30 in 99.4% runs
corrected  mean mu = +0.00058, |mu|>.30 in  0.0% runs
```

Stop line: causal-feedback toy, not a clinical/social model.

### Gate 3 — local physical operator

Nearest-neighbour diffusion only:

\[
q_i(t+1)=q_i+\eta(q_{i-1}-2q_i+q_{i+1}).
\]

Executed:

```text
N=201, eta=.2, steps=40
variance                  16.000000
predicted 2*eta*T         16.000000
L1 vs matched Gaussian     .00142042
correlation                .999999160
```

Purpose: no site evaluates a Gaussian/dense matrix; repeated local causal interaction realizes the global-looking operator. Standard diffusion, not a result claim.

---

## 5. Comparative-navigation update

The user's `surface animal versus flying animal` hunch should be reframed as **intrinsic behavioral dimension**.

Literature anchors checked today:

- 3-D bat MEC: local 3-D grid-field order without a global 3-D lattice (Ginosar et al., Nature 2021).
- freely flying barn owls: hippocampal 3-D position, flight-direction and perch coding (2023).
- chickadees: remote gaze can activate the same hippocampal place code as occupying the location; head-saccade cycles separate prediction/reaction components (Payne & Aronov, Nature 2025).
- June 2026 bat preprint: ensemble topology reported as a 2-D toroidal code during 3-D flight, aligned to approximately planar behavioral trajectories. Interesting but not peer reviewed.

Do **not** say `birds have a deeper entorhinal cortex`. Avian hippocampal formation is organized differently from mammalian hippocampal/entorhinal circuitry.

Candidate principle:

\[
\dim(E_{physical})\neq\dim(\mathcal B_{behavior})\neq rank(Dh_{task}).
\]

Represent the dimensions behavior/tasks actually use.

---

## 6. Below the maths

Do not ask where the brain stores a Jacobian/eigenvector.

Physical state evolves:

\[
\dot q=F(q,u).
\]

The brain does not symbolically evaluate `F`; the physical substrate **is the process described by `F`**.

`DF(q)` is what an external experimenter obtains by perturbing the system.

Candidate lower-level causal grammar:

```text
state
couple
propagate
integrate
nonlinearize
relax
modulate
adapt
```

A future artificial system could be specified in these local primitives and analyzed afterward with Jacobians/spectra/information metrics.

Modern physical-neural-network work is a mandatory neighbor: trainable optical/mechanical/electronic systems can perform useful transformations through their physical dynamics without operation-by-operation isomorphism to ordinary digital neural layers.

---

## 7. The visual-illusion example is exactly an observation fiber

A real opening and a sufficiently convincing painting of an opening can produce nearly identical instantaneous retinal measurements.

At that instant:

\[
h(x_{opening})\approx h(x_{painting}).
\]

They lie in the same or nearby observation fiber for that view.

New cues break the equivalence:

```text
binocular disparity
head motion / parallax
occlusion changes
focus/accommodation cues
interaction / touch
walking toward it
```

So `I see an opening` can be a posterior belief formed from appearance + prior before external geometry has strongly anchored the depth interpretation.

This is the same mathematics as monocular WorldSplat depth.

---

## 8. WorldSplat run: do not interfere

Observed intermediate screenshots today:

```text
~62,125 / 80,000: loss .0604, rgb .0390, depth .0159
~67,850 / 80,000: loss .0558, rgb .0308, depth .0221
```

The rendered world is visibly structured but still extremely coarse; cars/trees/road are packet masses, not recognizable objects.

No architecture change should be inferred from intermediate snapshots.

Finish the registered 80k ray-fix A/B and compare against the preserved old run.

---

## 9. Post-run opportunity: test `car concept` without training semantics

Virtual KITTI 2 officially provides, in addition to RGB/depth:

```text
class segmentation
instance segmentation
2-D / 3-D object tracking ground truth
camera intrinsics/extrinsics
optical flow
scene flow
```

This creates an unusually clean post-hoc probe.

Do **not** train WorldSplat with semantic labels first.

After the 80k run, optionally download class/instance ground truth and ask whether the unsupervised/shared decoder has developed stable primitive roles.

Candidate probe:

1. encode held-out frames;
2. decode the 512 splats;
3. project each splat into the image;
4. use class/instance masks only for scoring;
5. estimate per-splat or per-latent-direction semantic role consistency;
6. measure whether the same decoder components repeatedly support `car`, `road`, `sky`, etc. across scene, distance and appearance variation;
7. compare against shuffled splat indices, spatial-anchor-only predictor, and random-weight decoder.

Critical confound: fixed image-ray anchors can make a splat look semantically consistent merely because `road tends to be low / sky high`. Controls must condition on image position.

A stronger object result would require **instance-relative consistency across changing image positions**, not simply class-by-location.

If it exists, the interesting interpretation is not `Jennifer Aniston splat`. It is that a shared generative manifold learned reusable roles whose nuisance transformations can later be quotiented by a semantic receiver.

---

## 10. Next real experiments

### OA1-FACE — multiple receiver metrics on one learned face manifold

Use TinyAvatar/SplatWorld `z` and fit/read receiver heads for:

```text
identity
pose
expression
illumination
```

Measure

\[
G_k=J_k^TR_k^{-1}J_k
\]

and principal angles/nullspaces between receiver metrics.

Question: do identity receivers suppress pose directions while pose receivers amplify them?

Mandatory controls: dense/random heads, rotated tasks, random decoder.

### OA2-WORLD — stereo support rank

After ray-fix passes/fails cleanly, pair Camera_0 and Camera_1 for the **same scene state**.

Measure:

```text
J_C0
J_C1
ker(J_C0)
ker(J_C1)
intersection of nullspaces
weakest generalized anchor-gap direction v*
```

Ask whether Camera_1 specifically adds external support along directions Camera_0 leaves weak.

### OA3-CONCEPT — post-hoc VKITTI role probe

Use official segmentation only as measurement, not training signal. Test whether stable object/class roles exist above spatial-anchor baselines.

### OA4-PHYSICAL-GRAMMAR

Build a tiny local-state network with only local wired + metric coupling, leak, thresholds and slow adaptation. Do **not** specify the target global matrix. Train/select local parameters and then measure the emergent operator afterward.

Attack with an ordinary compact RNN/conv/state-space model at matched state/communication/energy proxy.

---

## 11. Important personal analogy, kept outside claims

A strong learned social prior plus ambiguous observations can yield a sharp interpretation. If the interpretation changes behavior, the behavior can alter other people's responses, producing real but partially endogenous confirming evidence.

This is a useful causal analogy for the engineering problem. It does not imply that adverse social experiences are imagined or self-created.

The technical lesson is only:

> **An acting model must know whether evidence merely arrived, was actively sought, or was partly generated by the consequences of its own belief-driven intervention.**

---

## 12. Carry-forward stack

The current synthesis is:

```text
physical local dynamics
        ↓
rich persistent state / learned manifold
        ↓
receiver-specific observation maps
        ↓
receiver-specific information metrics / quotients
        ↓
finite-horizon observability (different-width presents)
        ↓
belief precision versus externally earned support
        ↓
source lineage + intervention lineage
        ↓
internal sweeps/queries choose what to inspect
        ↓
new external measurement is allowed to add support
```

The strongest sentence to preserve:

> **The mathematics may not be the algorithm the physical system executes. It is our compressed description of the causal transformations that the material system performs directly. A world model should therefore track not only what state it predicts, but which receiver can distinguish which changes, which external observations earned those distinctions, and which of those observations were themselves altered by the model's prior actions.**

Do not hype. Do not lie. Keep attacking.
