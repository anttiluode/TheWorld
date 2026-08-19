"""Gate MP1 — primitive ladder for geometry x time.

Question:
    How much local mathematics is required once geometry converts a target
    travelling event pattern into local coincidence?

Arms:
    1) exponential leaky mass
    2) linear leaky mass
    3) finite coincidence window (integer occupancy only)

Controls:
    no delay geometry
    shuffled delay geometry

This is a mechanism gate, not a novelty benchmark. The structured delays encode
an intentionally favorable prior: a left-to-right event sheet near v=1.

Run:
    python experiments/mass_pulse_gate1_primitive_ladder.py
"""

import math
import numpy as np

SEED = 19082026
N = 12
X = np.arange(N, dtype=float)
V0 = 1.0
STRUCTURED_DELAYS = (N - 1 - X) / V0


def make_samples(seed, n_pos, n_neg, jitter=0.15, dropout=0.05, noise_rate=0.15):
    rng = np.random.default_rng(seed)

    def one(label):
        v = rng.uniform(0.85, 1.15)
        t0 = rng.uniform(0, 5)

        if label == 1:
            ts = t0 + X / v
        else:
            r = rng.random()
            if r < 0.45:
                ts = t0 + (N - 1 - X) / v
            elif r < 0.90:
                base = t0 + X / v
                ts = base[rng.permutation(N)]
            else:
                vw = rng.choice([rng.uniform(0.45, 0.70), rng.uniform(1.45, 1.8)])
                ts = t0 + X / vw

        events = []
        for i, t in enumerate(ts):
            if rng.random() > dropout:
                events.append((float(t + rng.normal(0, jitter)), int(i), 1.0))
            if rng.random() < noise_rate:
                events.append((float(t0 + rng.uniform(0, (N - 1) / 0.45)), int(i), 1.0))
        return events

    return [one(1) for _ in range(n_pos)], [one(0) for _ in range(n_neg)]


def arrivals(events, delays):
    return sorted((t + delays[i], a) for t, i, a in events)


def score_exp(events, delays, tau):
    arr = arrivals(events, delays)
    if not arr:
        return 0.0
    m = 0.0
    last = arr[0][0]
    peak = 0.0
    for t, a in arr:
        m *= math.exp(-(t - last) / tau)
        m += a
        peak = max(peak, m)
        last = t
    return peak


def score_linear(events, delays, leak):
    arr = arrivals(events, delays)
    if not arr:
        return 0.0
    m = 0.0
    last = arr[0][0]
    peak = 0.0
    for t, a in arr:
        m = max(0.0, m - leak * (t - last))
        m += a
        peak = max(peak, m)
        last = t
    return peak


def score_window(events, delays, width):
    ts = [t for t, _ in arrivals(events, delays)]
    if not ts:
        return 0.0
    j = 0
    peak = 0
    for i, t in enumerate(ts):
        while ts[j] < t - width:
            j += 1
        peak = max(peak, i - j + 1)
    return float(peak)


def choose_threshold(pos_scores, neg_scores):
    vals = np.sort(np.unique(np.r_[pos_scores, neg_scores]))
    ths = np.r_[vals[0] - 1e-6, (vals[:-1] + vals[1:]) / 2, vals[-1] + 1e-6]
    best = (-1.0, None)
    for th in ths:
        acc = ((pos_scores >= th).sum() + (neg_scores < th).sum()) / (
            len(pos_scores) + len(neg_scores)
        )
        if acc > best[0]:
            best = (float(acc), float(th))
    return best[1], best[0]


def tune_and_test(kind, delays, train, test):
    if kind == "exp":
        params = np.geomspace(0.08, 2.0, 20)
        scorer = score_exp
    elif kind == "linear":
        params = np.geomspace(0.1, 5.0, 20)
        scorer = score_linear
    else:
        params = np.linspace(0.05, 2.0, 20)
        scorer = score_window

    pt, nt = train
    pe, ne = test
    best = (-1.0, None, None)
    for p in params:
        ps = np.array([scorer(e, delays, p) for e in pt])
        ns = np.array([scorer(e, delays, p) for e in nt])
        th, acc = choose_threshold(ps, ns)
        if acc > best[0]:
            best = (acc, float(p), th)

    _, p, th = best
    ps = np.array([scorer(e, delays, p) for e in pe])
    ns = np.array([scorer(e, delays, p) for e in ne])
    acc = ((ps >= th).sum() + (ns < th).sum()) / (len(ps) + len(ns))
    return best, float(acc)


def main():
    train = make_samples(SEED, 2000, 2000)
    test = make_samples(SEED + 1, 4000, 4000)

    print("GATE MP1 — travelling event sheet, 12 sensors")
    print("=" * 64)

    for kind in ("exp", "linear", "window"):
        fit, acc = tune_and_test(kind, STRUCTURED_DELAYS, train, test)
        print(
            f"{kind:7s} structured delays: "
            f"train={fit[0]:.5f} test={acc:.5f} internal_parameter={fit[1]:.4f}"
        )

    fit_no, acc_no = tune_and_test("window", np.zeros(N), train, test)
    print(f"window  NO delays        : test={acc_no:.5f}")

    shuffle_acc = []
    for s in range(32):
        rr = np.random.default_rng(1000 + s)
        d = STRUCTURED_DELAYS[rr.permutation(N)]
        _, a = tune_and_test("window", d, train, test)
        shuffle_acc.append(a)

    print(
        f"window  SHUFFLED delays  : mean={np.mean(shuffle_acc):.5f} "
        f"sd={np.std(shuffle_acc):.5f} best={np.max(shuffle_acc):.5f}"
    )

    print("\nInterpretation:")
    print("  exponential mass is unnecessary on this task;")
    print("  delay + finite coincidence occupancy is enough.")
    print("  This is a built-in geometry prior, not a learned-architecture win.")


if __name__ == "__main__":
    main()
