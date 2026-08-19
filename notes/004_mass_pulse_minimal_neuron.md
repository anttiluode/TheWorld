# Note 004 — Mass–Pulse: a minimal material neuron

**Status:** architecture sketch + executed toy gates; not a novelty claim.  
**Date:** 2026-08-19

## 0. Question

Can we describe a useful neuron-like computational body with much less explicit mathematics than the later Geometric Neuron machinery, while retaining the useful surviving ideas from Deerskin / GeometricNeuron / V23?

The aim is not to simulate Hodgkin–Huxley faithfully. The aim is to find a **minimal causal language** that a sparse computer implementation can execute cheaply and that can later be analyzed with richer mathematics.

The candidate answer is:

> **Local state + relaxation + delayed event routing + threshold/reset.**

Call the fast local state `m` ("mass" only as a bookkeeping metaphor: charge/evidence/resource-like state, not literal physical mass) and the transmitted event a **pulse**.

The spike is therefore **not the whole internal language**. It is the message that crosses a boundary. Inside the body, most of the computation can live in slowly changing local state.

---

## 1. What the old repos actually leave us with

The audited Deerskin / ECG line says:

- the original ECG accident is a quantized aliasing map inside a variance-regulated loop, not the later skew/Koopman Geometric Neuron;
- rich pulse trains, bistability and several regimes can arise in entirely real amplitude-only dynamics;
- passive geometry alone does not buy an arrow; direction requires delay/history/asymmetry;
- the original Geometric Neuron was itself primarily a **sampling/delay/resonance/gate** object, not necessarily a complex-valued one;
- V23's disciplined descendant is `distributed local state + geometry-dependent coupling + event-driven transitions + receiver-relative readout`.

Therefore a minimal descendant does **not** need to start with Moiré interference, complex phase, Koopman fits, eigenmodes or a global field. Those can remain analysis tools or optional mechanisms.

---

## 2. Minimal fast state

For compartment/contact `i`, store only

```text
m_i       current fast local state
last_i    last time this state was touched
```

Between events the state relaxes. For the analytically convenient exponential case:

\[
m_i(t)=m_i(t_0)e^{-(t-t_0)/\tau_i}.
\]

But the implementation need not integrate this at every millisecond. When the next event arrives at time `t`, lazily apply the entire silent interval in one operation:

```text
RELAX(i,t):
    m_i *= decay_i[t-last_i]
    last_i = t
```

where `decay_i[dt]` may be an exponential, a lookup table, a linear decay, or an integer approximation.

Then:

```text
DEPOSIT(i,a):
    m_i += a
```

This already creates temporal integration and memory. Silence costs no state updates.

---

## 3. Geometry is routing metadata, not a matrix multiply

Each connection stores only something like:

```text
target
amplitude / gain
delay
```

A pulse schedules a future event:

```text
PROPAGATE(i -> j, a):
    queue.push(time + delay_ij, j, gain_ij * a)
```

No dense `W @ x` is required.

If only a sparse set of events occurs, runtime scales with **events actually delivered**, not with every possible synapse at every simulation tick.

On ordinary GPUs this is not automatically faster: irregular queues and memory accesses can under-use SIMD hardware. The architectural advantage is most plausible in sparse regimes, CPU/event runtimes, batched sparse kernels, or neuromorphic/custom hardware. This note claims an operation-count opportunity, not a GPU speed result.

---

## 4. Soma / receiver

The soma can be just another compartment with one nonlinearity:

```text
if m_soma >= threshold:
    FIRE
    m_soma = reset
```

The outward language is now a pulse:

```text
(time, source, optional amplitude/type)
```

The **body's** language is more primitive:

```text
RELAX
DEPOSIT
PROPAGATE
THRESHOLD
RESET
```

That is sufficient for the first model.

---

## 5. What geometry buys with no complex numbers

Two input sites A and B can have different propagation delays.

If

```text
delay_A = 2
delay_B = 1
```

then the temporal sequence

```text
A at t=0
B at t=1
```

arrives at the soma simultaneously at `t=2` and can cross a coincidence threshold.

Reverse the order:

```text
B at t=0  -> arrives t=1
A at t=1  -> arrives t=3
```

and a sufficiently fast soma leak prevents coincidence.

Thus

> **geometry turns temporal order into local coincidence.**

This is established delay-line/coincidence-detector territory, not a novelty claim. But it is important for this program because it shows that one useful part of the later Geometric Neuron can be realized with only delayed events + one leaky scalar.

The executed Gate 2 in `experiments/minimal_material_neuron.py` passes this order test; equal-delay control is order-symmetric.

---

## 6. What one extra slow state buys

One scalar `m` cannot express every history-dependent effect cheaply. Add a slow resource/recovery state only where needed:

```text
r_i        local availability / recovery / adaptation
```

After an event, deplete it; during silence it recovers lazily:

\[
r(t)=1-[1-r(t_0)]e^{-(t-t_0)/\tau_r}.
\]

The next pulse samples `r`.

Now the same incoming event can have a different effect depending on recent local history.

This is the key V23 idea in its smallest form:

> **The past need not be stored as a history vector. Some consequences of the past simply have not relaxed yet.**

Tsodyks–Markram dynamic synapses are an established biological/mathematical neighbor; this note does not claim the mechanism as new.

---

## 7. Minimal hierarchy

The architecture can be grown only when a gate requires it.

### Level 0 — point pulse neuron

```text
one m
one threshold/reset
```

This is basically event-driven leaky integrate-and-fire.

### Level 1 — geometric material neuron

```text
many local m_i
sparse geometry/delays
one or several receiver thresholds
```

The point neuron is the degenerate limit obtained by collapsing all locations/delays into one state.

### Level 2 — history-bearing material neuron

```text
selected local m_i + r_i
geometry/delays
receiver thresholds
```

This gives local activity-silent history and refractory/facilitation/depression-like effects.

### Level 3 — optional nonlinear compartments

Only if required by a task:

```text
local saturation
NMDA-like voltage dependence
branch threshold
interference/resonance
```

Do not pay for these everywhere by default.

### Level 4 — slow adaptation / learning

Keep slow material plasticity separate from fast inference:

```text
ADAPT edge/location/threshold on selected events
```

Oja/STDP/homeostatic updates are possible, but the fast body does not need to evaluate a learning rule on every tick.

---

## 8. Executed headless gates

### Gate MP0 — lazy silence parity

One exponential leaky state, 100,000 clock ticks, 180 sparse input events.

Clocked implementation updates the state every tick.
Event-driven implementation analytically relaxes it only when an event arrives.

With a threshold that produced 61 spikes:

```text
clocked updates        100,000
lazy updates               180
update ratio              555.6x
spike count              61 / 61
spike times              identical
```

This is an exact property for this simple model because between inputs the state only decays; an upward threshold crossing can occur only at an arrival event.

This is not a GPU benchmark.

### Gate MP1 — delay geometry gives order selectivity

```text
A->B with asymmetric delays : fires at t=2
B->A with asymmetric delays : no fire
same-delay control          : neither order selectively fires
```

No phase / FFT / matrix multiply is used.

### Gate MP2 — local unrelaxed state carries age

Condition a resource and then probe after different waits:

```text
wait .5   -> probe .389
wait 2.0  -> probe .494
wait 8.0  -> probe .761
wait 32   -> probe .988
```

A later event can therefore read a compressed physical trace of elapsed local history without a stored timeline.

### Gate MP3 — nominal sparse-body budget

For illustration only:

```text
512 compartments x 100 s x 1 kHz = 51,200,000 compartment-ticks
2,500 touched states               =      2,500 lazy relaxes
nominal update-count ratio         =     20,480x
```

Again: operation count, not measured hardware speed.

---

## 9. Relationship to the ECG pulse

The old PerceptionLab ECG pulse should **not** be copied as the minimal neuron.

Its audited mechanism is specific:

```text
quantized checkerboard transfer map
+
finite readout geometry
+
50-tick variance thermostat
->
relaxation/spiking regimes
```

That accident was valuable because it showed how unexpectedly rich global dynamics can arise from a tiny local loop. But the variance thermostat later failed as a general trainable architecture.

The transferable lesson is therefore:

> **Do not reproduce the ECG waveform. Reproduce the economy that made a rich waveform emerge from very few local rules.**

Mass–Pulse does that more directly.

---

## 10. Is the Geometric-Neuron-like spike still useful?

Yes, but demoted to its correct role.

A pulse is excellent as:

```text
boundary crossing
sparse communication event
reset / broadcast trigger
plasticity timing marker
```

It is probably **not** the full computational state of the body.

The working body can remain mostly silent while local `m_i/r_i` states decay, interact and wait to be sampled.

This is exactly where V23, WidePresent and the current "below the maths" idea converge.

---

## 11. Mandatory literature neighbors / attackers

The primitive pieces are established:

- leaky integrate-and-fire / spike-response models;
- Izhikevich's efficient two-state spiking model;
- exact/event-driven integrate-and-fire simulation (Brette and related work);
- Tsodyks–Markram dynamic synapses;
- cable/delay-line coincidence detection;
- compartmental/dendritic models;
- neuromorphic event-driven computation.

So `Mass–Pulse` is **not** a novelty claim.

The potentially interesting research question is narrower:

> At a matched state/communication/description budget, can receiver-specific sparse material bodies with local lazy state and geometry-dependent event routing perform useful world-model / temporal tasks more efficiently than compact dense RNN/SSM/spiking baselines?

That must be measured.

---

## 12. Next gate

Build a small network where the target genuinely requires both:

```text
where an event arrived
+
how old the local trace is
```

Compare at matched stored-state count:

```text
A: point LIF network
B: compact GRU/RNN
C: delay-line state-space model
D: Mass–Pulse body
E: Mass–Pulse with local states shuffled across geometry
```

The decisive contrast remains V23's:

```text
STRUCTURED local-history x geometry
versus
SHUFFLED local-history x geometry
```

If shuffled performs equally, geometry is ornamental.

---

## Carry-forward sentence

> **The minimal computational language may not be vectors and matrix multiplication, and it may not even be spikes. A body can be specified as local state that relaxes, sparse events that deposit and route state through geometry, and thresholds that emit new events. The rich mathematics is then our analysis of what those cheap causal rules collectively implement.**
