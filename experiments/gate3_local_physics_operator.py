from __future__ import annotations

import numpy as np

N = 201
ETA = 0.20
STEPS = 40


def diffuse() -> np.ndarray:
    q = np.zeros(N, dtype=np.float64)
    q[N // 2] = 1.0
    for _ in range(STEPS):
        qn = q.copy()
        qn[1:-1] = q[1:-1] + ETA * (q[:-2] - 2.0 * q[1:-1] + q[2:])
        # Reflecting boundaries; they are far enough away not to matter here.
        qn[0] = q[0] + ETA * (q[1] - q[0])
        qn[-1] = q[-1] + ETA * (q[-2] - q[-1])
        q = qn
    return q


def main() -> None:
    q = diffuse()
    x = np.arange(N, dtype=np.float64) - N // 2
    mass = q.sum()
    variance = float((q * x * x).sum() / mass)
    expected_variance = 2.0 * ETA * STEPS

    gaussian = np.exp(-(x * x) / (2.0 * variance))
    gaussian /= gaussian.sum()
    l1 = float(np.abs(q - gaussian).sum())
    corr = float(np.corrcoef(q, gaussian)[0, 1])

    print("OA-LOCAL-PHYSICS-OPERATOR")
    print(f"N={N} eta={ETA} steps={STEPS}")
    print(f"mass                    = {mass:.16f}")
    print(f"measured variance       = {variance:.8f}")
    print(f"expected 2*eta*T        = {expected_variance:.8f}")
    print(f"L1 vs matched Gaussian  = {l1:.8f}")
    print(f"corr vs matched Gaussian= {corr:.9f}")
    print()
    print("INTERPRETATION")
    print("Each site only exchanges state with immediate neighbors.")
    print("No site evaluates a Gaussian or a dense matrix, yet the global impulse response becomes Gaussian-like.")
    print("This is standard diffusion, used only to demonstrate the distinction between physical implementation and external mathematical description.")


if __name__ == "__main__":
    main()
