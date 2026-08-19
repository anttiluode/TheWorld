"""Receiver-specific dynamical degree toy.

One shared six-state stable world is read by four different receivers.
The impulse-response Hankel rank exposes how many dynamical modes each receiver
actually needs in an exact linear realization.

This is standard realization theory; the experiment exists to connect that
object to SplatNeuron/observer-atlas resource questions.
"""

import numpy as np


def main():
    r1, r2 = 0.97, 0.50
    r3, th3 = 0.94, 0.40
    r4, th4 = 0.80, 1.00

    R3 = r3 * np.array([
        [np.cos(th3), -np.sin(th3)],
        [np.sin(th3),  np.cos(th3)],
    ])
    R4 = r4 * np.array([
        [np.cos(th4), -np.sin(th4)],
        [np.sin(th4),  np.cos(th4)],
    ])

    A = np.zeros((6, 6))
    A[0, 0] = r1
    A[1, 1] = r2
    A[2:4, 2:4] = R3
    A[4:6, 4:6] = R4

    B = np.array([1.0, 1.0, 1.0, 0.5, 0.8, -0.2])

    receivers = {
        "slow-only": np.array([1, 0, 0, 0, 0, 0.0]),
        "oscillation-only": np.array([0, 0, 1, 0, 0, 0.0]),
        "fast-only": np.array([0, 1, 0, 0, 0, 0.0]),
        "mixed receiver": np.array([0.6, 0.3, 0.5, -0.2, 0.4, 0.1]),
    }

    def impulse_response(C, T=80):
        x = B.copy()
        y = []
        for _ in range(T):
            y.append(float(C @ x))
            x = A @ x
        return np.array(y)

    def hankel(y, n=30):
        return np.array([[y[i + j] for j in range(n)] for i in range(n)])

    print("RECEIVER-SPECIFIC DYNAMICAL DEGREE")
    print("=" * 64)
    for name, C in receivers.items():
        s = np.linalg.svd(hankel(impulse_response(C)), compute_uv=False)
        rank = int(np.sum(s > 1e-8))
        print(
            f"{name:17s}: Hankel rank={rank} first singular values="
            f"{np.array2string(s[:6], precision=3, suppress_small=True)}"
        )

    print("\nSame six-state world; receiver degree ranges from 1 to 6.")
    print("This is expected linear-systems theory, not a novelty result.")


if __name__ == "__main__":
    main()
