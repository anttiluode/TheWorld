"""Minimal material neuron headless gates.

No FFT, no complex arithmetic, no dense matrix multiply.
Primitive language:
    RELAX -> DEPOSIT -> PROPAGATE -> THRESHOLD -> RESET
Optional slow local resource adds activity-silent history.

This is a research instrument, not a novelty claim.
"""
from __future__ import annotations

import heapq
import math
import random


def gate_lazy_parity():
    ticks = 100_000
    tau = 120.0
    threshold = 0.45
    rng = random.Random(19082026)
    event_ticks = sorted(rng.sample(range(1, ticks), 180))
    amps = {t: rng.uniform(0.15, 0.55) for t in event_ticks}

    decay = math.exp(-1.0 / tau)
    mass = 0.0
    fires_clock = []
    for t in range(ticks):
        mass *= decay
        if t in amps:
            mass += amps[t]
            if mass >= threshold:
                fires_clock.append(t)
                mass = 0.0

    mass = 0.0
    last_t = 0
    fires_lazy = []
    for t in event_ticks:
        mass *= math.exp(-(t - last_t) / tau)
        mass += amps[t]
        if mass >= threshold:
            fires_lazy.append(t)
            mass = 0.0
        last_t = t

    assert fires_clock == fires_lazy
    return {
        "clock_updates": ticks,
        "lazy_updates": len(event_ticks),
        "ratio": ticks / len(event_ticks),
        "spikes": len(fires_clock),
        "identical": fires_clock == fires_lazy,
        "first_spikes": fires_clock[:12],
    }


def soma_sequence(events, delays, *, tau=0.5, threshold=1.5):
    queue = []
    for t, port, amp in events:
        heapq.heappush(queue, (t + delays[port], amp, port))

    mass = 0.0
    last_t = 0.0
    fires = []
    trace = []
    while queue:
        t, amp, port = heapq.heappop(queue)
        mass *= math.exp(-(t - last_t) / tau)
        mass += amp
        trace.append((t, port, mass))
        if mass >= threshold:
            fires.append(t)
            mass = 0.0
        last_t = t
    return fires, trace


def gate_delay_order():
    ab = [(0.0, "A", 1.0), (1.0, "B", 1.0)]
    ba = [(0.0, "B", 1.0), (1.0, "A", 1.0)]

    delays = {"A": 2.0, "B": 1.0}
    fires_ab, _ = soma_sequence(ab, delays)
    fires_ba, _ = soma_sequence(ba, delays)

    control = {"A": 1.0, "B": 1.0}
    ctrl_ab, _ = soma_sequence(ab, control)
    ctrl_ba, _ = soma_sequence(ba, control)

    assert bool(fires_ab) and not bool(fires_ba)
    assert bool(ctrl_ab) == bool(ctrl_ba)
    return {
        "ab": fires_ab,
        "ba": fires_ba,
        "ctrl_ab": ctrl_ab,
        "ctrl_ba": ctrl_ba,
    }


def resource_probe(wait, *, tau_rec=8.0, depletion=0.65):
    resource = 1.0
    conditioning_amp = resource
    resource *= 1.0 - depletion
    resource = 1.0 - (1.0 - resource) * math.exp(-wait / tau_rec)
    return conditioning_amp, resource


def gate_local_age():
    waits = [0.5, 2.0, 8.0, 32.0]
    vals = [resource_probe(w) for w in waits]
    assert all(vals[i][1] < vals[i + 1][1] for i in range(len(vals) - 1))
    return list(zip(waits, vals))


def gate_nominal_budget():
    n_compartments = 512
    sim_ms = 100_000
    touched_states = 2_500
    dense_updates = n_compartments * sim_ms
    return {
        "dense_updates": dense_updates,
        "lazy_updates": touched_states,
        "ratio": dense_updates / touched_states,
    }


def main():
    print("MINIMAL MATERIAL NEURON — headless gates")
    print("=" * 62)

    g0 = gate_lazy_parity()
    print("GATE MP0 — silence costs nothing")
    print(f"clocked state updates : {g0['clock_updates']:,}")
    print(f"lazy state updates    : {g0['lazy_updates']:,}")
    print(f"update ratio          : {g0['ratio']:.1f}x")
    print(f"spikes                : {g0['spikes']}")
    print(f"spike times identical : {g0['identical']}")
    print(f"first spikes          : {g0['first_spikes']}")

    g1 = gate_delay_order()
    print("\nGATE MP1 — geometry turns time into coincidence")
    print(f"A then B asymmetric delays : {g1['ab']}")
    print(f"B then A asymmetric delays : {g1['ba']}")
    print(f"equal-delay control AB/BA  : {g1['ctrl_ab']} / {g1['ctrl_ba']}")

    g2 = gate_local_age()
    print("\nGATE MP2 — the past survives as unrelaxed local state")
    for wait, (conditioning, probe) in g2:
        print(f"wait={wait:4.1f} -> conditioning={conditioning:.3f}, probe={probe:.3f}")

    g3 = gate_nominal_budget()
    print("\nGATE MP3 — nominal sparse-body operation count")
    print(f"clocked compartment ticks : {g3['dense_updates']:,}")
    print(f"lazy touched states       : {g3['lazy_updates']:,}")
    print(f"nominal update ratio      : {g3['ratio']:,.0f}x")
    print("NOTE: operation-count illustration, not a GPU benchmark.")


if __name__ == "__main__":
    main()
