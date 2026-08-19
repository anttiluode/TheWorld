from __future__ import annotations

import numpy as np

SEEDS = 1000
T = 500
ALPHA = 0.05
SIGMA = 0.25
MU0 = 0.20
BETAS = (0.8, 1.0, 1.2, 1.5)


def run(seed: int, beta: float, corrected: bool) -> float:
    rng = np.random.default_rng(seed)
    mu = MU0
    theta = 0.0
    for _ in range(T):
        action = np.tanh(mu)
        y = theta + beta * action + rng.normal(0.0, SIGMA)
        if corrected:
            # Condition on the known intervention-generated component.
            y = y - beta * action
        mu = (1.0 - ALPHA) * mu + ALPHA * y
    return float(mu)


def summarize(beta: float, corrected: bool) -> tuple[float, float, float, float, float]:
    vals = np.array([run(seed, beta, corrected) for seed in range(SEEDS)])
    q10, q50, q90 = np.quantile(vals, [0.1, 0.5, 0.9])
    frac = float((np.abs(vals) > 0.30).mean())
    return float(vals.mean()), float(vals.std()), float(q10), float(q50), float(q90), frac


def main() -> None:
    print("OA-ENDOGENOUS-EVIDENCE-GATE")
    print(f"seeds={SEEDS} T={T} alpha={ALPHA} sigma={SIGMA} mu0={MU0} true_theta=0")
    print()
    print(" beta  mode        mean      std       q10       median    q90       |mu|>.30")
    print(" ----- ---------   --------  --------  --------  --------  --------  --------")
    for beta in BETAS:
        for corrected in (False, True):
            mean, std, q10, q50, q90, frac = summarize(beta, corrected)
            mode = "corrected" if corrected else "naive"
            print(f" {beta:4.1f}  {mode:9s}  {mean:+.5f}  {std:.5f}  {q10:+.5f}  {q50:+.5f}  {q90:+.5f}   {frac:.3f}")
    print()
    print("MEAN-FIELD FIXED POINT")
    print("Naive noiseless dynamics satisfy mu = beta*tanh(mu).")
    print("At beta > 1 the zero fixed point is unstable and nonzero self-confirming attractors appear.")
    print("Correcting for the known action-induced term removes that feedback in this toy.")
    print()
    print("STOP LINE")
    print("This is a causal-feedback toy, not a clinical or social-behavior model.")


if __name__ == "__main__":
    main()
