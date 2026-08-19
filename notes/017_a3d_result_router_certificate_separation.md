# Note 017 — A3D result: separate router, certificate, and persistent state

**Status:** first A3D webcam receipt analyzed. Mixed result. Cross-scale persistence signal survives; full spectral runtime body does not earn itself.

## The result that survived twice

The narrow replicated observation is:

> **A local wake supported across multiple scales is more likely to remain locally active later than a single-scale wake.**

First A3C webcam run, multi-minus-single future-wake delta:

```text
1f  +0.082
2f  +0.094
4f  +0.128
8f  +0.094
```

A3D webcam run, same measurement:

```text
1f  +0.061
2f  +0.066
4f  +0.101
8f  +0.082
```

So the sign survives a second ordinary webcam session and all four tested lags.

This is not enough to claim a general law, but it is enough to keep the certificate hypothesis alive.

## The stronger monotonic story does not survive cleanly

Do **not** say:

> more scales always means more reliable / more persistent.

In the A3D run the 1-frame persistence rates were:

```text
m=1  .859
m=2  .936
m=3  .952
m=4  .984
m=5  .992
m=6  .619
```

The all-six-scale class behaves differently. It may contain broad/global transients, saturation-like events, large motion, lighting changes, calibration effects, or another event class. Those are hypotheses, not established explanations.

The useful current certificate is therefore coarse:

```text
single-scale
vs
multi-scale (>=2)
```

not a monotone 1..6 confidence ladder.

## A3D tracker receipt

A3D connected `multiplicity >= 2` cells into local tracks and separated:

```text
SUPPORTED  current sensory certificate exists
REUSE      support exists, consequence stable
HOLD       state persists without current support
WAKE       NEW / UPDATE / REACQUIRE / EXPIRE
```

`HOLD` was explicitly kept separate from evidence.

On the first A3D webcam run:

```text
                              certificate     tiles
current spatial fanout          .1373          .0602
belief spatial fanout           .2099          .1254
held-only fanout                .0726          .0652
receiver WAKE fraction          .3996          .4378
mean track age                 13.1f          16.6f
```

Certificate tracking lowered downstream WAKE fraction by only about 0.038 absolute / 8.7% relative versus the same tracker on plain tiles.

But it paid for that with:

```text
~2.28x current spatial fanout
~1.67x persistent belief fanout
shorter mean track life
more create/expire churn
```

The event counts make the mixed character clear:

```text
certificate: NEW 38, UPDATE 71, REACQUIRE 53, REUSE 39, HOLD 260, EXPIRE 37
tiles:       NEW 30, UPDATE 93, REACQUIRE 66, REUSE 17, HOLD 263, EXPIRE 29
```

The certificate stream gave more `REUSE` and fewer `UPDATE`/`REACQUIRE` events, but also more `NEW`/`EXPIRE` churn.

## What I think now

The earlier mental picture was:

```text
localized spectral packets
    -> become the persistent computational substrate
```

The experiments do not support that as the next engineering move.

A better decomposition is now visible:

```text
cheap local event geometry
        -> ADDRESS / candidate routing

cross-scale agreement
        -> CERTIFICATE / persistence prior / verifier

persistent local consequence
        -> BELIEF / cached state

materially changed consequence
        -> WAKE / communication
```

This is a much cleaner architecture.

### Router and certificate are different jobs

The plain tile representation has repeatedly been the sharper spatial router. That should be respected rather than fought.

The spectral/multiscale representation has repeatedly carried information about future persistence. That should also be respected rather than inflated into a universal representation claim.

So the likely useful combination is not `spectral beats tiles`.

It is:

> **tiles tell us where to look; multiscale agreement tells us how much to trust/retain what we found.**

This is exactly the kind of decomposition a sparse runtime needs.

## Relation to the original 'communicate yet hold belief' idea

A3D is the first tiny executable object in this line where the phrase becomes literal bookkeeping:

```text
support arrives
    -> local state becomes/continues SUPPORTED

support vanishes briefly
    -> local state can HOLD

support returns
    -> REACQUIRE

consequence changes enough
    -> WAKE receiver
```

This should not be overread as a brain model. The hold window was hand-set and the tracker is ordinary connected-components plus nearest-centroid matching.

But conceptually it is useful because it separates:

```text
what the sensor currently says
from
what the persistent local state currently believes
from
whether a downstream consumer needs to hear about a change
```

That separation is central to the larger WorldModel / CC0 line.

## The Mass–Pulse connection, narrowly stated

The old material intuition can now be restated without mysticism:

```text
persistent local state = mass-like residue / stored consequence
new support or contradiction = pulse / innovation
receiver-relevant change = emitted event
```

A3D does not prove that this is the right neuron primitive. It simply gives the metaphor a concrete software analogue with explicit support bookkeeping.

## Main next systems gate — A3E / first real CC0-B move

Do not add a richer dense spectral field.

Use the cheap router to avoid computing the expensive verifier globally:

```text
raw / plain-tile local change
        -> candidate cells
        -> fixed small spatial neighborhood
        -> compute multiscale verifier ONLY there
        -> approximate dense certificate teacher
        -> update persistent local tracks
        -> emit WAKE only on consequence change
```

The dense spectral bank becomes an offline/parallel **teacher**, not the hot-loop implementation.

Measure:

```text
candidate-cell fraction
certificate recall vs dense teacher
certificate precision
missed persistent events
local verifier calls
actual CPU wall time
memory / state touched
receiver WAKE fraction
belief fanout
track churn
```

Mandatory attackers:

```text
tile-only tracker
dense Gabor certificate tracker
simple Gaussian/Laplacian/DoG image pyramid
raw-delta local verifier
```

The image-pyramid attacker is important. The surviving observation is multiscale agreement, not Gabor specificity. If an ordinary cheap pyramid gives the same persistence certificate, use it.

## A second scientific gate: learn persistence instead of hand-setting HOLD=4

A3C/A3D already estimate a conditional survival curve:

```text
P(local wake at t+k | source multiplicity class)
```

A later version should replace the arbitrary four-frame hold with a calibrated hazard / survival rule.

For example, a local state's support score could decay according to an empirically measured hazard conditioned on its certificate class and recent history.

But do not do this before attacking the cheaper router/verifier path. A sophisticated persistence law is useless if obtaining the certificate costs more than the computation it suppresses.

## Stop lines

Current surviving claim:

> **Cross-scale agreement appears to contain local persistence information on these webcam runs.**

Current failed/unearned claims:

```text
Gabor packets are a better spatial router       not supported
spectral field is a faster AI substrate         not supported
more scales always means more persistence       not supported
A3D tracker beats the tile tracker overall      not supported
runtime speedup                                 not measured
brain/cortical mechanism                        not established
```

## Carry-forward

> **Use the cheapest geometry to address a change, a richer local test to decide whether it deserves persistence, and wake downstream computation only when the persistent consequence itself becomes invalid.**
