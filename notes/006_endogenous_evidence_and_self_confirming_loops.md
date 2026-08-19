# Note 006 — Endogenous evidence: when belief changes the observations that follow

**Status:** candidate WorldModel bookkeeping extension / toy dynamics, not a psychological diagnosis and not a novelty claim.  
**Date:** 2026-08-19

## 0. The missing category

Notes 001–003 separate internal prediction from external evidence.

But an active agent introduces a harder case:

> **An observation can be physically external and still be partly caused by the model's own prior action.**

This matters in robotics, active perception, social interaction, and any closed loop where belief changes behavior and behavior changes what is observed next.

So `external` versus `internal` is not enough. We also need **intervention lineage**.

---

## 1. Closed-loop observer

Let the hidden world state be `x_t`, belief be `b_t`, action be

\[
a_t=\pi(b_t),
\]

world dynamics be

\[
x_{t+1}=F(x_t,a_t,w_t),
\]

and observation be

\[
y_{t+1}=h(x_{t+1},a_t)+\epsilon_t.
\]

Now the data distribution itself depends on the current belief through the chosen action.

The causal loop is

```text
belief
  -> action
  -> world / other agent changes
  -> observation
  -> updated belief
```

A later observation is real, but it is not necessarily evidence about the *counterfactual world that would have occurred under another action*.

---

## 2. A toy self-confirming loop

`experiments/gate2_endogenous_evidence.py` uses the smallest possible model.

There is a neutral hidden truth

\[
\theta=0.
\]

The observer has scalar belief `mu_t` and emits an action

\[
a_t=\tanh(\mu_t).
\]

The environment reacts to that action:

\[
y_t=\theta+\beta a_t+\epsilon_t.
\]

A naïve observer treats `y_t` as if it were direct evidence for `theta`:

\[
\mu_{t+1}=(1-\alpha)\mu_t+\alpha y_t.
\]

Ignoring noise, fixed points satisfy

\[
\mu=\beta\tanh(\mu).
\]

For

\[
\beta>1,
\]

the zero fixed point becomes unstable and two non-zero stable attractors appear.

This is a pitchfork-like self-confirmation regime:

```text
small initial positive expectation
 -> positive action
 -> environment produces more positive cue
 -> cue is misattributed to hidden truth
 -> stronger positive expectation
```

The mirror-image negative loop exists as well.

If the observer knows the action-induced term and conditions on it,

\[
y_t^{corrected}=y_t-\beta a_t,
\]

then the estimated hidden truth returns toward zero.

---

## 3. Why this matters to WorldModel

A robot that moves a camera does something benign and desirable: the action changes the observation geometry. The new measurement is still genuine information about the same mostly unchanged scene, conditioned on known pose.

A robot that pushes an object changes the world itself. A later image is evidence about the **post-intervention** world, not an independent measurement of the pre-intervention state.

A social agent can be even more coupled: its expression, posture, wording or avoidance may change another agent's response, creating observations correlated with its own expectation.

Therefore support bookkeeping should distinguish at least:

```text
1. exogenous measurement
   source not caused by current model action

2. active-sensing measurement
   model chose viewpoint/query, but measurement constrains a state that is transformed in a known way

3. intervention-mediated measurement
   model action changed the latent world / other agent before measurement

4. recursive internal prediction
   no new external measurement at all
```

All four can change belief.

They should not receive identical provenance treatment.

---

## 4. External does not mean independent

Suppose two observations are collected after actions selected from the same belief state.

Even if sensor noise is independent, the observations can share causal ancestry through the policy.

So lineage ultimately has at least two components:

- **measurement ancestry** — shared sensor/teacher/data ancestors;
- **intervention ancestry** — which prior beliefs/actions altered the process that generated the observation.

This resembles familiar problems in causal inference, adaptive data collection, active learning, feedback systems, and `data incest` in distributed inference.

The claim here is not that these fields missed it. The point is that WorldModel's support ledger must eventually account for it if the model becomes an acting agent.

---

## 5. Social interpretation as a computational analogy

A person sees an ambiguous expression and infers an internal state in someone else.

The first observation can be weak:

```text
brief gaze / facial expression / posture
```

while the prior over possible meanings can be strong.

If the resulting expectation changes one's own expression or behavior, the other person may respond to that behavior. The next observation is then partly endogenous.

This does **not** mean the external social world is imaginary, and it does not imply that earlier adverse experiences were not real. The model simply demonstrates how genuine experience, learned priors, and present-day interaction can become coupled strongly enough that a belief helps shape the evidence it later receives.

That is a dynamics statement, not a blame statement.

---

## 6. Relation to hallucination / anchoring

Earlier we defined a direction with high total belief precision but weak external support.

Closed-loop action adds another question:

> If apparently confirming evidence arrives, how much of it was causally independent of the belief being confirmed?

A future support object may therefore need something richer than a matrix:

\[
A_{ext} + \mathcal L_{source} + \mathcal L_{intervention}.
\]

`A_ext` says which directions are constrained.

`L_source` says which observations share informational ancestry.

`L_intervention` says which observations arose after the model acted on the world based on the current belief.

---

## 7. A useful active-sensing rule survives

None of this invalidates active sensing.

Moving the camera specifically to increase information along the weakly anchored direction `v*` remains excellent behavior:

\[
a_*=\arg\max_a v_*^T\Delta A(a)v_*/cost(a).
\]

But the update must be conditioned on the action and its known geometry.

That is very different from internally imagining Camera B and then pretending its expected view was observed.

---

## 8. Stop lines

Do not turn this toy into:

- a clinical model of trauma;
- a claim that social rejection is self-generated;
- a general theory of psychopathology;
- evidence that all active observations are biased;
- a novelty claim over causal inference / control theory.

The legitimate engineering conclusion is:

> **For an acting world model, provenance must include not only where an observation came from but whether the model's own belief-driven action changed the process that generated it.**

---

## Carry-forward sentence

> **Prediction can create an action; an action can create a new external observation; but an external observation caused by the model's intervention is not epistemically identical to an independent observation of the untouched world.**
