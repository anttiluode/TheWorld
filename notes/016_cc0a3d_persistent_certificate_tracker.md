# Note 016 — CC0-A3D persistent certificate tracker

**Status:** executable GUI/instrument ready. Dense oracle front end; no runtime-speed claim.

## Why this exists

The first A3C webcam receipt gave a narrow positive result:

```text
lag    single-scale   multi-scale   delta
1f        .887           .969       +.082
2f        .859           .953       +.094
4f        .795           .923       +.128
8f        .745           .839       +.094
```

So, in that run, a local wake supported by two or more scales was more likely to remain locally active later than a one-scale wake.

That does **not** mean the spectral representation is already a good router. Full spectral spatial fanout remained worse than the plain tile attacker. The surviving question is whether the multi-scale certificate can be collapsed into a much smaller persistent local state.

---

## Instrument

Run:

```bat
run_cc0a3d_certificate_tracker.bat
```

or:

```bat
python3.13 experiments\cc0a3d_certificate_tracker_gui.py
```

A3D inherits A3C and takes the fixed certificate:

```text
certificate(x,y) := multiplicity(x,y) >= 2 scales
```

Connected certificate cells on the 6x8 routing lattice become tiny blob tracks.

The tracker state is deliberately simple and ordinary. It uses connected components plus greedy nearest-centroid matching on the coarse lattice.

Each track can be:

```text
SUPPORTED
    certificate evidence exists this frame

REUSE
    evidence exists, but the track consequence did not change enough
    to justify a downstream wake

HOLD
    evidence is temporarily absent, but local state remains resident
    for a short fixed window

WAKE
    NEW / UPDATE / REACQUIRE / EXPIRE event that a downstream
    receiver would need to process
```

Default hold window:

```text
4 frames
```

Important bookkeeping rule:

> **HOLD is belief/state, not current sensory support.**

The GUI therefore renders supported and held state differently and separately bills held-only spatial fanout.

---

## Tile attacker

The same tracker logic is applied to the plain spatial-tile wake mask.

This matters because a certificate tracker is not interesting merely because tracking is useful. The cross-scale version must earn something over a simpler local spatial event stream.

The GUI compares:

```text
certificate current fanout
certificate tracker belief fanout
certificate held-only fanout
certificate receiver WAKE fraction

plain tile current fanout
plain tile tracker belief fanout
plain tile receiver WAKE fraction
```

---

## What counts as a track WAKE

A supported track wakes downstream on:

```text
NEW
REACQUIRE after HOLD
centroid motion >= 0.75 grid cell
area change >= 50%
mean multiplicity change >= 0.75
EXPIRE after the hold window
```

Otherwise a supported matched track is `REUSE`.

These thresholds are hand-set plumbing for the first gate. They are not learned and are not claimed optimal.

---

## GUI

The main persistent-track panel uses:

```text
bright cell = currently SUPPORTED
 dim cell   = HOLD only
red label   = track id
```

A held track may remain visible for up to four frames after certificate support disappears.

The live info panel reports:

```text
active/supported/held tracks
WAKE / REUSE / HOLD decisions this frame
session receiver WAKE fraction
current certificate vs belief fanout
held-only fanout
plain tile tracker attacker statistics
```

---

## Saved receipt

Default folder:

```text
results/cc0a3d_certificate_tracker_runs/
```

Files:

```text
cc0a3d_certificate_tracker_YYYYMMDD_HHMMSS.txt
cc0a3d_certificate_tracker_YYYYMMDD_HHMMSS.json
cc0a3d_certificate_tracker_YYYYMMDD_HHMMSS.csv
cc0a3d_certificate_tracker_YYYYMMDD_HHMMSS_track_events.csv
cc0a3d_certificate_tracker_YYYYMMDD_HHMMSS_trace.npz
```

The track-event CSV records every:

```text
NEW / UPDATE / REUSE / HOLD / REACQUIRE / EXPIRE
```

for both certificate and tile trackers.

The NPZ stores per-frame multiplicity, certificate belief, held state and tile belief masks.

---

## First gate

The useful pattern is not merely `WAKE fraction low`.

A3D should show all of:

```text
1. multi-scale certificate blobs form trackable local regions;
2. track state survives brief evidence gaps without exploding spatially;
3. downstream WAKE decisions are substantially sparser than naive per-frame track recomputation;
4. held-only fanout remains modest;
5. the certificate tracker offers some advantage over the same tracker on plain tiles.
```

Possible advantages could be:

```text
lower receiver WAKE fraction at comparable belief fanout
longer track lifetime at comparable false persistence
fewer create/expire churn events
more robust reacquisition after brief support gaps
```

Do not pick whichever metric looks flattering after the run. Inspect all of them.

---

## Kill / demote lines

Demote the certificate-tracker story if:

```text
plain tile tracker is equally stable or better with lower fanout
OR
HOLD causes belief fanout to grow much beyond current evidence
OR
track identity churn is high
OR
receiver WAKE remains close to every-frame update
OR
apparent persistence comes mostly from the hand-set hold window rather than reacquisition/continuity
```

Even if A3D loses, A3C's narrow observation can remain true: cross-scale multiplicity may predict persistence without being the best runtime representation.

---

## Boundary

The Gabor bank and tile front end are still computed densely every frame.

A3D is testing the **control-plane state machine after oracle certificate extraction**. It is not yet the CC0-B sparse front end.

No claim yet of:

```text
faster AI
GPU speedup
energy speedup
brain mechanism
learned object tracker
```

## Carry-forward sentence

> **A3C asked whether several scales agreeing predicts persistence. A3D asks whether that agreement can be collapsed into a small local state that can be SUPPORTED, REUSED, HELD without support, and WOKEN only when its consequence materially changes.**
