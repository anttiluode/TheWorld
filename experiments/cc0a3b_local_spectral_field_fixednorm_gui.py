from __future__ import annotations

"""CC0-A3B: same A3 GUI, but remove framewise global renormalization.

A3 normalized every Gabor map by *that frame's* q95.  That creates a hidden
global dependency: one local event can move the scale factor and therefore move
all spatial cells.  A3B freezes one q95 scale per spectral channel from the
first frame and never changes it during the run.  The tile edge channel is
handled the same way.  Reset starts a new calibration.

This is still a DENSE ORACLE.  It measures locality/opportunity, not runtime
speed.
"""

import argparse
import cv2
import numpy as np
import tkinter as tk

import cc0a3_local_spectral_field_gui as base


_OriginalCensus = base.LocalFieldCensus


class FixedNormSpectralAnalyzer(base.LocalSpectralAnalyzer):
    """Quadrature Gabor energy with a fixed first-frame channel scale."""

    def __init__(self, cfg: base.SpectralConfig):
        super().__init__(cfg)
        self.fixed_scale = None

    def reset_scale(self):
        self.fixed_scale = None

    def analyze(self, gray: np.ndarray) -> np.ndarray:
        s_count = len(self.cfg.wavelengths)
        o_count = len(self.cfg.orientations_deg)
        raw = np.zeros(self.shape, np.float32)
        ki = 0
        for si in range(s_count):
            for oi in range(o_count):
                k0, k90 = self.kernels[ki]
                ki += 1
                r0 = cv2.filter2D(gray, cv2.CV_32F, k0, borderType=cv2.BORDER_REFLECT101)
                r90 = cv2.filter2D(gray, cv2.CV_32F, k90, borderType=cv2.BORDER_REFLECT101)
                energy = np.sqrt(r0 * r0 + r90 * r90)
                raw[si, oi] = base._pool_grid(energy, self.cfg.grid_rows, self.cfg.grid_cols)

        if self.fixed_scale is None:
            # One scalar per (scale, orientation), fixed for the whole session.
            q = np.quantile(raw, 0.95, axis=(2, 3), keepdims=True).astype(np.float32)
            positive = q[q > 1e-6]
            floor = max(1e-5, float(np.median(positive)) * 0.02) if positive.size else 1e-5
            self.fixed_scale = np.maximum(q, floor).astype(np.float32)

        return np.clip(raw / self.fixed_scale, 0.0, 4.0).astype(np.float32)


class FixedNormTileAnalyzer(base.TileAnalyzer):
    """Plain tile attacker with a fixed first-frame edge-energy scale."""

    def __init__(self, cfg: base.SpectralConfig):
        super().__init__(cfg)
        self.edge_scale = None

    def reset_scale(self):
        self.edge_scale = None

    def analyze(self, gray: np.ndarray) -> np.ndarray:
        intensity = base._pool_grid(gray, self.cfg.grid_rows, self.cfg.grid_cols)
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        edge = np.sqrt(gx * gx + gy * gy)
        pooled = base._pool_grid(edge, self.cfg.grid_rows, self.cfg.grid_cols)
        if self.edge_scale is None:
            self.edge_scale = max(1e-5, float(np.quantile(pooled, 0.95)))
        edge_norm = np.clip(pooled / self.edge_scale, 0.0, 4.0)
        intensity = np.clip(intensity, 0.0, 1.0)
        return np.stack([intensity, edge_norm], axis=0).astype(np.float32)


# Patch the names used by the inherited census __post_init__.
base.LocalSpectralAnalyzer = FixedNormSpectralAnalyzer
base.TileAnalyzer = FixedNormTileAnalyzer


class FixedNormCensus(_OriginalCensus):
    def reset(self):
        super().reset()
        if hasattr(self.spectral, "reset_scale"):
            self.spectral.reset_scale()
        if hasattr(self.tiles, "reset_scale"):
            self.tiles.reset_scale()

    def process(self, frame_bgr: np.ndarray):
        m, visuals = super().process(frame_bgr)
        tile_spatial = float(visuals["tile_wake"].any(axis=0).mean())
        self.rows[-1]["tile_spatial_fanout"] = tile_spatial
        return m, visuals

    def summary(self) -> dict:
        s = super().summary()
        steady = self.rows[1:] if len(self.rows) > 1 else self.rows
        tile_spatial = float(np.mean([r.get("tile_spatial_fanout", 0.0) for r in steady])) if steady else 0.0
        s["tile_spatial_routing_fanout"] = tile_spatial
        s["normalization"] = "FIXED first-frame q95 per spectral channel; fixed first-frame q95 for tile edge channel"
        if getattr(self.spectral, "fixed_scale", None) is not None:
            s["spectral_fixed_scales"] = self.spectral.fixed_scale[:, :, 0, 0].tolist()
        if getattr(self.tiles, "edge_scale", None) is not None:
            s["tile_edge_fixed_scale"] = float(self.tiles.edge_scale)
        s["warning"] = (
            "Dense Gabor and tile analyzers still run every frame. A3B removes "
            "framewise global q95 renormalization but remains an opportunity/locality "
            "instrument, not measured sparse-runtime speedup."
        )
        return s


base.LocalFieldCensus = FixedNormCensus


class A3BGUI(base.SpectralFieldGUI):
    def __init__(self, root: tk.Tk, args):
        super().__init__(root, args)
        self.root.title("CC0-A3B Local Spectral Field — FIXED normalization / dense oracle")

    def _update_metrics(self, m: base.FrameMetrics):
        super()._update_metrics(m)
        s = self.census.summary() if self.census else {}
        now = self.census.rows[-1].get("tile_spatial_fanout", 0.0) if self.census and self.census.rows else 0.0
        self.metric_vars["tile"].set(
            f"tile wake: {s.get('tile_wake_fraction',0):.3f}   "
            f"tile spatial fanout: {s.get('tile_spatial_routing_fanout',0):.3f}   now {now:.3f}"
        )


def main():
    ap = argparse.ArgumentParser(description="CC0-A3B localized spectral field with fixed normalization")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--analysis-width", type=int, default=128)
    ap.add_argument("--tolerance", type=float, default=0.35)
    ap.add_argument("--tile-tolerance", type=float, default=0.08)
    ap.add_argument("--out-dir", type=str, default="results/cc0a3b_fixednorm_runs")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        base.self_test()
        return
    root = tk.Tk()
    A3BGUI(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()
