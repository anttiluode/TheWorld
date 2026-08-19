# Handoff — minimal material neuron

**Date:** 2026-08-19

## One-line state

> **The simplest useful descendant of Deerskin / GeometricNeuron may be an asynchronous local-state machine: sparse events lazily update relaxing local state, geometry supplies routing/delay, and threshold/reset emits pulses. The spike is the boundary message, not the whole internal computation.**

## What was re-read

- `deerskin-hypothesis`: the original membrane/Moiré/carrier-wave picture plus the ECG accident; later audit retracts the claim that oscillation was inevitable.
- `Geometric-Neuron`: original neuron was a real-valued sampling/delay/resonance/gate pipeline; later phase-memory claim killed by null.
- `GeometricNeuronV21`: ECG loop is a quantized aliasing map + variance thermostat, not the later lag/skew operator; variance governor failed as a general trainable architecture.
- `GeometricNeuron_V20`: surviving lessons include delay/history for direction, sparse delta-like communication, and the separation of soma computation / excitable propagation / capture.
- `GeometricNeuronV23`: strongest disciplined descendant: distributed local state + geometry-dependent coupling + event-driven state transitions + receiver-relative readout.

## Minimal causal grammar

Fast body:

```text
RELAX(local state to event time)
DEPOSIT(event amplitude)
PROPAGATE(event through sparse geometry/delay)
THRESHOLD(receiver)
RESET(after pulse)
```

Optional only when required:

```text
RECOVER / RESOURCE   slow activity-silent local history
ADAPT                slow structural / synaptic learning
LOCAL NONLINEARITY   saturation/NMDA/branch/interference
```

State per site can begin as:

```text
m_i       fast leaky state
last_i    last update time
```

and selected sites may add:

```text
r_i       slow recovery/resource/adaptation state
```

Geometry is stored as sparse routing metadata:

```text
target, gain, delay
```

No dense matrix multiply is required by the runtime semantics.

## Executed gates

See `experiments/minimal_material_neuron.py` and `results/2026-08-19_minimal_material_neuron.txt`.

### MP0 — lazy silence parity

100,000 clock ticks versus 180 actual event updates:

```text
update ratio          555.6x
spikes                61 / 61
spike times           identical
```

This is exact for the simple exponential-decay model used because state only falls during silence; upward threshold crossings happen at arrivals.

### MP1 — delay geometry gives temporal order

```text
A then B + asymmetric delays -> soma coincidence -> fire at t=2
B then A + same geometry      -> no fire
same-delay control            -> no order selectivity
```

Important lesson: some later "phase/direction" behavior can be realized much more cheaply as ordinary delay + local state + threshold. Passive reciprocal geometry alone still cannot create a preferred arrow; the delay/asymmetry/history is doing the work.

### MP2 — past as unrelaxed state

After conditioning a slow local resource, probe amplitude increases with wait:

```text
0.5 -> .389
2.0 -> .494
8.0 -> .761
32  -> .988
```

No timeline/history vector is stored. The present physical state contains a compressed trace of the past.

### MP3 — nominal sparse-body operation count

```text
512 compartments x 100 s x 1 kHz = 51,200,000 clocked compartment updates
2,500 actual touches              =      2,500 lazy relaxes
nominal ratio                     =     20,480x
```

NOT a GPU benchmark. Standard GPUs may dislike irregular event queues; this is an algorithmic operation-count opportunity suited to sparse/event runtimes or neuromorphic/custom hardware.

## Literature boundary

All primitive pieces have strong prior art:

- event-driven exact integrate-and-fire simulation (Brette);
- efficient reduced spiking models (Izhikevich);
- dynamic local synaptic state (Tsodyks–Markram);
- delay-line/coincidence detection;
- dendritic compartments;
- neuromorphic event processing.

So the primitive is not novel.

The possible research result is a **matched-resource systems claim**:

> Does structured local-history × geometry, executed lazily as sparse events, solve temporal/world-model tasks with less communication/state-update cost than compact point-LIF, RNN/GRU, SSM and shuffled-geometry baselines?

## Strongest conceptual correction

Do not copy the old ECG pulse as the neuron.

The ECG accident was useful because a tiny loop produced rich dynamics, but its specific variance thermostat is not the general mechanism.

Do not copy the old Moiré soma as mandatory either. Interference may be an optional local nonlinearity, but it has not earned the right to be paid for everywhere.

The minimal body is cheaper:

```text
unrelaxed local state
+
delayed sparse events
+
one receiver threshold
```

A pulse is still useful as the outward event / reset / plasticity marker.

## Next gate

Build a task that cannot be solved by location alone or age alone, only by their pairing.

Matched stored-state count:

```text
A point LIF network
B compact GRU/RNN
C delay-line / state-space baseline
D Mass–Pulse body
E Mass–Pulse with local states shuffled across geometry
```

The decisive V23 control is `D - E`: if shuffling local history across geometry does not hurt, geometry is ornamental.

Then separately benchmark actual CPU/GPU wall time. Do not infer hardware speed from primitive counts.

## Carry-forward sentence

> **The neuron-like body's cheapest language may be neither matrices nor a rich spike code: it may be local state that quietly relaxes, sparse pulses that sample and move that state through geometry, and slow material adaptation that rewrites the routes only occasionally. The mathematics can be recovered afterward as our description of the operator those local rules implement.**
