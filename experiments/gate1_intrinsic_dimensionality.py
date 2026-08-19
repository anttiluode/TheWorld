from __future__ import annotations

import itertools
import numpy as np

SEED = 19082026
SAMPLES = 20_000
RADIUS = 0.10
TARGET = 0.95


def grid_centers(m: int, d: int) -> np.ndarray:
    xs = (np.arange(m, dtype=np.float64) + 0.5) / m
    return np.array(list(itertools.product(xs, repeat=d)), dtype=np.float64)


def coverage(samples: np.ndarray, centers: np.ndarray, radius: float, chunk: int = 4000) -> float:
    r2 = radius * radius
    hit = 0
    for start in range(0, len(samples), chunk):
        s = samples[start : start + chunk]
        d2 = ((s[:, None, :] - centers[None, :, :]) ** 2).sum(axis=-1)
        hit += int((d2.min(axis=1) <= r2).sum())
    return hit / len(samples)


def minimum_cover(samples: np.ndarray, d: int) -> tuple[int, int, float]:
    for m in range(2, 16):
        c = grid_centers(m, d)
        cov = coverage(samples, c, RADIUS)
        if cov >= TARGET:
            return m, len(c), cov
    raise RuntimeError("coverage target not reached")


def main() -> None:
    rng = np.random.default_rng(SEED)
    sheet2 = rng.random((SAMPLES, 2))
    volume3 = rng.random((SAMPLES, 3))

    # Same 2-D sheet, merely embedded in 3-D.  Distances within the sheet are
    # unchanged, so the representation cost should follow intrinsic dimension.
    sheet3 = np.column_stack([sheet2, np.full(SAMPLES, 0.5)])

    m2, n2, c2 = minimum_cover(sheet2, 2)
    m3, n3, c3 = minimum_cover(volume3, 3)

    # Embed the 2-D centres into 3-D and score against the embedded sheet.
    centers_sheet3 = np.column_stack([grid_centers(m2, 2), np.full(n2, 0.5)])
    c_emb = coverage(sheet3, centers_sheet3, RADIUS)

    print("OA-DIMENSIONALITY-SMOKE")
    print(f"seed={SEED} samples={SAMPLES} radius={RADIUS:.3f} target={TARGET:.2f}")
    print(f"2D sheet      : m={m2:2d} centres={n2:4d} coverage={c2:.5f}")
    print(f"same sheet 3D : m={m2:2d} centres={n2:4d} coverage={c_emb:.5f}")
    print(f"3D volume     : m={m3:2d} centres={n3:4d} coverage={c3:.5f}")
    print(f"centre ratio volume/sheet = {n3/n2:.3f}x")
    print()
    print("INTERPRETATION")
    print("This is a covering-number illustration, not a neuroscience result.")
    print("Embedding a 2-D behavioral sheet in 3-D does not create a 3-D covering cost.")
    print("A genuinely volumetric state space pays the dimensionality tax at fixed local resolution.")


if __name__ == "__main__":
    main()
