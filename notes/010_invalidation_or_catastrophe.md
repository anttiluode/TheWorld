# Note 010 — The invalidation OR catastrophe

**Status:** simple scaling argument / reason to prefer receiver-local validity over one global wake gate. Not a novelty claim.  
**Date:** 2026-08-19

## 0. The problem

A single global surprise/change gate can look excellent on a small machine.

But in a large persistent world, **something is almost always changing**.

If the policy is

```text
ANY meaningful change anywhere
        -> wake the whole expensive machine
```

then adding more independently changing parts eventually drives the wake probability toward one.

This is the **invalidation OR catastrophe**.

It is a concrete scaling reason that `TheClutch2`-style global validity alone is not enough for the larger `DifferentMachine` / SplatNeuron / WorldModel picture.

---

## 1. Minimal calculation

Suppose there are `R` receiver computations.

Receiver `i` becomes invalid on a step with probability `p_i` and costs `C_i` when recomputed.

A receiver-local runtime has expected receiver work

\[
E[C_{local}]
=
\sum_i p_i C_i
+
C_{guards/routes}.
\]

A crude global gate that wakes **all** receivers if **any** receiver is invalid pays

\[
E[C_{global}]
=
P(\mathrm{any\ invalid})
\sum_i C_i
+
C_{global\ guard}.
\]

If, only for the toy calculation, invalidations are independent and identical:

\[
p_i=p,\qquad C_i=C,
\]

then

\[
P(\mathrm{any\ invalid})=1-(1-p)^R.
\]

So

\[
E[C_{local}]\approx RpC,
\]

while

\[
E[C_{global}]\approx [1-(1-p)^R]RC.
\]

Ignoring guard cost for the moment, the global/local ratio is

\[
\frac{E[C_{global}]}{E[C_{local}]}
=
\frac{1-(1-p)^R}{p}.
\]

---

## 2. Example

Let

```text
R = 100 receivers
p = 0.01 invalidation probability per receiver per step
same receiver cost C
```

Then

\[
P(\mathrm{any\ invalid})
=1-0.99^{100}
\approx0.634.
\]

Expected receiver work:

```text
always-on        = 100 C
one global gate  = 63.4 C
receiver-local   = 1.0 C
```

So a global gate still wakes almost two thirds of the whole machine even though each individual receiver needs work only one percent of the time.

The local architecture can in principle expose a much larger saving **if** routing and guards are cheap.

---

## 3. Large-system limit

For fixed `p>0`,

\[
1-(1-p)^R\to1
\quad\text{as}\quad R\to\infty.
\]

Therefore the global gate asymptotically becomes:

```text
wake almost every step
```

because some part of the world is almost always invalid.

This is exactly the failure mode one would expect in:

```text
large visual scenes
many tracked objects
many agent memories/tools
large persistent latent worlds
many downstream task receivers
```

A big world is not globally quiet even when most of its consequences are locally stable.

---

## 4. Why SplatNeuron matters here

Receiver-local invalidation requires an answer to:

> Which changes can this receiver actually distinguish or care about?

That is precisely the observer/equivalence geometry from Notes 001–003 and 009.

For

\[
y_i=h_i(x),
\]

a world change near

\[
\ker Dh_i(x)
\]

should not force receiver `i` to wake.

So SplatNeuron's surviving idea is no longer merely compression of an interface.

It supplies a possible **invalidation geometry**.

---

## 5. Why DifferentMachine matters here

Receiver-local validity is useless if every incoming change must be compared against every receiver.

That would cost

\[
O(R)
\]

just to discover who can sleep.

The `DifferentMachine` constraint therefore becomes load-bearing:

> **Relevance must be locally discoverable.**

A world event needs a cheap route to a small candidate receiver set, for example through:

```text
spatial bins / hashes
object ids
local graph adjacency
changed dependency ids
hierarchical bounding volumes
learned sparse routing with bounded fanout
```

The architecture only scales if candidate discovery remains sublinear / bounded enough to preserve the skipped work.

---

## 6. The break-even inequality

For one receiver with ordinary recomputation cost `C`, cheap guard/routing cost `g`, invalidation probability `p`, and occasional full-refresh probability `q` with cost `T`, receiver-local execution wins only when

\[
g+pC+qT<C.
\]

Equivalently,

\[
g+qT<(1-p)C.
\]

This is the entire economic problem in one line.

The right-hand side is the work made avoidable by sleeping.

The left-hand side is what we pay to know that sleeping is safe plus any reacquisition cost.

No architecture story can evade this inequality.

---

## 7. Correlation does not kill the point, but changes the geometry

Real receiver invalidations will not be independent.

A camera cut may invalidate almost everything together.

A moving car may invalidate a cluster of motion/collision receivers together.

A lighting change may invalidate RGB/appearance receivers while leaving route geometry mostly intact.

So the useful object is not merely scalar `p_i`; it is the **joint invalidation structure**.

That structure itself may have locality / low rank / hierarchy.

The next real benchmark should therefore log an invalidation matrix over time:

```text
rows    = time/events
columns = receivers
1       = receiver consequence crossed tolerance
0       = remained valid
```

Then measure:

```text
per-receiver invalidation rate
pairwise/shared invalidation
cluster structure
global-any rate
candidate-routing fanout
```

This tells us whether receiver-local sleeping has exploitable structure before building an elaborate runtime.

---

## 8. CC0 gets a cheap pre-gate: CC0-A

Before building the full compiler/runtime, measure the opportunity.

### CC0-A — invalidation sparsity census

On a real changing stream:

1. define several useful receivers;
2. run the rich teacher offline on every step;
3. record each receiver's true consequence;
4. choose task-meaningful tolerances;
5. mark when each receiver actually crosses its tolerance;
6. compare:

```text
raw input changed
ANY receiver changed
per-receiver changed
receiver clusters changed
```

A promising substrate should show:

```text
global world changes often
BUT
most individual receiver consequences remain valid most of the time
AND
a change addresses only a small receiver cluster
```

If that pattern is absent, do not build CC0-B.

### CC0-B

Only then learn/derive guards and routing that approximate the oracle invalidation matrix without running the teacher.

This separates:

```text
opportunity exists?
```

from

```text
can a cheap runtime exploit it?
```

That is a much cleaner gate.

---

## 9. WorldSplat prediction

For a learned scene world, the prediction is not that the entire latent becomes quiet.

It is almost the opposite:

> **The rich latent may change continuously while different task receivers remain piecewise valid for very different durations.**

Examples:

```text
sky appearance changes
    RGB receiver: wake
    collision receiver: sleep

near object shifts 20 cm
    collision receiver: wake
    far-building identity receiver: sleep

camera rotates
    image renderer: wake broadly
    some world-coordinate object facts: remain valid
```

If measured receiver invalidations look like this, the architecture has an opportunity.

If every receiver changes whenever the latent changes, it does not.

---

## Carry-forward sentence

> **A large world is almost never globally unchanged. The scalable question is whether most individual receivers remain valid, and whether the few invalidated receivers can be found without scanning the rest.**
