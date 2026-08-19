"""Gate OA0 — prediction is not new observation.

Tiny numerical instrument for notes/001_observer_atlas.md.

World state x = [X, Y, Z, a]: one 3-D point plus one appearance scalar.
A camera returns only [u, v, nonlinear appearance]. A single view therefore
cannot determine all four world dimensions: points at different depths on the
same ray can be observationally identical. A second baseline view can expose
the hidden depth direction.

The point of the script is deliberately narrow:

    one observer          -> rank-deficient directional support
    internal prediction   -> no new support rank
    second external view  -> may add the missing rank

This is standard local observability / Fisher-information algebra. It is an
instrument, not a novelty claim.
"""

from __future__ import annotations

import math
import numpy as np


def yaw_matrix(yaw: float) -> np.ndarray:
    c, s = math.cos(yaw), math.sin(yaw)
    return np.array(
        [
            [c, 0.0, s],
            [0.0, 1.0, 0.0],
            [-s, 0.0, c],
        ],
        dtype=float,
    )


def observe(
    x: np.ndarray,
    camera_position: np.ndarray,
    yaw: float = 0.0,
    focal: float = 1.0,
) -> np.ndarray:
    """Small nonlinear camera-like observer.

    x[:3] is a 3-D point and x[3] is a scalar appearance variable.
    The appearance channel is weakly mixed with image position so the map is
    nonlinear/mixed rather than four independent textbook coordinates.
    """
    p = x[:3]
    appearance = x[3]
    q = yaw_matrix(-yaw) @ (p - camera_position)
    X, Y, Z = q
    if Z <= 0.1:
        raise ValueError("point must remain in front of the camera")
    u = focal * X / Z
    v = focal * Y / Z
    c = math.tanh(float(appearance + 0.15 * u))
    return np.array([u, v, c], dtype=float)


def numerical_jacobian(fn, x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    y0 = fn(x)
    J = np.zeros((y0.size, x.size), dtype=float)
    for k in range(x.size):
        xp = x.copy()
        xm = x.copy()
        xp[k] += eps
        xm[k] -= eps
        J[:, k] = (fn(xp) - fn(xm)) / (2.0 * eps)
    return J


def support_matrix(J: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """Local Fisher/normal matrix J^T R^-1 J with isotropic noise."""
    return (J.T @ J) / (sigma * sigma)


def matrix_rank(A: np.ndarray, tol: float = 1e-8) -> int:
    return int(np.linalg.matrix_rank(A, tol=tol))


def spectrum(A: np.ndarray) -> np.ndarray:
    return np.linalg.eigvalsh(0.5 * (A + A.T))


def main() -> None:
    x = np.array([0.35, 0.10, 3.00, 0.40], dtype=float)

    cam_a = np.array([0.0, 0.0, 0.0], dtype=float)
    cam_b = np.array([0.8, 0.0, 0.0], dtype=float)

    obs_a = lambda z: observe(z, cam_a)
    obs_b = lambda z: observe(z, cam_b)

    J_a = numerical_jacobian(obs_a, x)
    J_b = numerical_jacobian(obs_b, x)

    A_a = support_matrix(J_a)

    # Pure internal prediction / replay is NOT another independent camera
    # measurement. In this static-coordinate toy, support simply remains A_a.
    A_after_prediction = A_a.copy()

    # A genuinely distinct external view adds a new information term.
    A_ab = A_after_prediction + support_matrix(J_b)

    print("Gate OA0 — directional support")
    print("world dimension:", x.size)
    print("camera-A output dimension:", obs_a(x).size)
    print()
    print("rank after external camera A :", matrix_rank(A_a))
    print("rank after internal prediction:", matrix_rank(A_after_prediction))
    print("rank after external camera B :", matrix_rank(A_ab))
    print()
    print("eigenvalues A only :", np.round(spectrum(A_a), 8))
    print("eigenvalues A + B  :", np.round(spectrum(A_ab), 8))

    # Construct a second physical world that lies farther along camera A's ray.
    # The [u,v] coordinates remain identical. Because the appearance state is
    # unchanged and its nonlinear term depends on u, camera A cannot distinguish
    # these two worlds at all.
    x_alias = x.copy()
    x_alias[:3] *= 1.30

    ya = obs_a(x)
    ya_alias = obs_a(x_alias)
    yb = obs_b(x)
    yb_alias = obs_b(x_alias)

    err_a = float(np.linalg.norm(ya - ya_alias))
    err_b = float(np.linalg.norm(yb - yb_alias))

    print()
    print("single-view ambiguity test")
    print("||h_A(x)-h_A(x_alias)|| =", f"{err_a:.12f}")
    print("||h_B(x)-h_B(x_alias)|| =", f"{err_b:.12f}")

    pass_rank = (
        matrix_rank(A_a) == 3
        and matrix_rank(A_after_prediction) == 3
        and matrix_rank(A_ab) == 4
    )
    pass_alias = err_a < 1e-9 and err_b > 1e-3

    print()
    print("OA0a prediction adds no rank:", "PASS" if pass_rank else "FAIL")
    print("OA0b baseline breaks alias    :", "PASS" if pass_alias else "FAIL")

    if not (pass_rank and pass_alias):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
