from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import time
import tkinter as tk
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageTk


# -----------------------------------------------------------------------------
# CC0-A3 LOCAL SPECTRAL FIELD
# -----------------------------------------------------------------------------
# This is an instrument/demo, not a speed claim.
# The dense Gabor bank is intentionally computed every frame so we can label
# which localized packets *could* have remained asleep.
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class SpectralConfig:
    wavelengths: Tuple[float, ...] = (4.0, 6.5, 10.0, 15.5, 24.0, 36.0)
    orientations_deg: Tuple[float, ...] = (0.0, 45.0, 90.0, 135.0)
    grid_cols: int = 8
    grid_rows: int = 6
    analysis_width: int = 128
    tolerance: float = 0.35
    tile_tolerance: float = 0.08
    raw_threshold: float = 0.0005


@dataclass
class FrameMetrics:
    frame_index: int
    raw_mae: float
    raw_changed: int
    spectral_wake_fraction: float
    spectral_spatial_fanout: float
    tile_wake_fraction: float
    any_spectral: int
    cross_scale_agreement: float
    active_bundle_count: int
    largest_bundle_fraction: float
    active_packet_count: int
    total_packet_count: int
    active_cells: int
    total_cells: int


def gray01(frame_bgr: np.ndarray, width: int) -> np.ndarray:
    h, w = frame_bgr.shape[:2]
    new_h = max(1, int(round(h * width / max(1, w))))
    g = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (width, new_h), interpolation=cv2.INTER_AREA)
    return g.astype(np.float32) / 255.0


def _pool_grid(img: np.ndarray, rows: int, cols: int) -> np.ndarray:
    """Average-pool HxW image to rows x cols without requiring divisibility."""
    h, w = img.shape
    ys = np.linspace(0, h, rows + 1, dtype=np.int32)
    xs = np.linspace(0, w, cols + 1, dtype=np.int32)
    out = np.zeros((rows, cols), np.float32)
    for gy in range(rows):
        for gx in range(cols):
            cell = img[ys[gy]:ys[gy + 1], xs[gx]:xs[gx + 1]]
            out[gy, gx] = float(cell.mean()) if cell.size else 0.0
    return out


def _robust_unit(x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    q = float(np.quantile(x, 0.95))
    if q < eps:
        return np.zeros_like(x, dtype=np.float32)
    return np.clip(x / q, 0.0, 2.0).astype(np.float32)


class LocalSpectralAnalyzer:
    """Localized quadrature Gabor bank, pooled to a sparse address lattice."""

    def __init__(self, cfg: SpectralConfig):
        self.cfg = cfg
        self.kernels: List[Tuple[np.ndarray, np.ndarray]] = []
        for wavelength in cfg.wavelengths:
            sigma = max(1.2, 0.56 * wavelength)
            ksize = int(max(7, math.ceil(sigma * 6)))
            if ksize % 2 == 0:
                ksize += 1
            ksize = min(ksize, 63)
            for deg in cfg.orientations_deg:
                theta = math.radians(deg)
                k0 = cv2.getGaborKernel(
                    (ksize, ksize), sigma, theta, wavelength, 0.55, 0.0, ktype=cv2.CV_32F
                )
                k90 = cv2.getGaborKernel(
                    (ksize, ksize), sigma, theta, wavelength, 0.55, math.pi / 2.0, ktype=cv2.CV_32F
                )
                k0 = k0 - k0.mean()
                k90 = k90 - k90.mean()
                n0 = float(np.sqrt((k0 * k0).sum()) + 1e-8)
                n90 = float(np.sqrt((k90 * k90).sum()) + 1e-8)
                self.kernels.append((k0 / n0, k90 / n90))

    @property
    def shape(self) -> Tuple[int, int, int, int]:
        return (
            len(self.cfg.wavelengths),
            len(self.cfg.orientations_deg),
            self.cfg.grid_rows,
            self.cfg.grid_cols,
        )

    def analyze(self, gray: np.ndarray) -> np.ndarray:
        s_count = len(self.cfg.wavelengths)
        o_count = len(self.cfg.orientations_deg)
        out = np.zeros(self.shape, np.float32)
        ki = 0
        for si in range(s_count):
            for oi in range(o_count):
                k0, k90 = self.kernels[ki]
                ki += 1
                r0 = cv2.filter2D(gray, cv2.CV_32F, k0, borderType=cv2.BORDER_REFLECT101)
                r90 = cv2.filter2D(gray, cv2.CV_32F, k90, borderType=cv2.BORDER_REFLECT101)
                energy = np.sqrt(r0 * r0 + r90 * r90)
                pooled = _pool_grid(energy, self.cfg.grid_rows, self.cfg.grid_cols)
                out[si, oi] = _robust_unit(pooled)
        return out


class TileAnalyzer:
    """Embarrassing baseline: raw local intensity + gradient energy, no frequency story."""

    def __init__(self, cfg: SpectralConfig):
        self.cfg = cfg

    def analyze(self, gray: np.ndarray) -> np.ndarray:
        intensity = _pool_grid(gray, self.cfg.grid_rows, self.cfg.grid_cols)
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        edge = np.sqrt(gx * gx + gy * gy)
        edge = _robust_unit(_pool_grid(edge, self.cfg.grid_rows, self.cfg.grid_cols))
        intensity = np.clip(intensity, 0.0, 1.0)
        return np.stack([intensity, edge], axis=0).astype(np.float32)


def _cross_scale_agreement(obs: np.ndarray) -> float:
    """Mean adjacent-scale spatial correlation after collapsing orientation."""
    x = obs.mean(axis=1)
    vals: List[float] = []
    for s in range(x.shape[0] - 1):
        a = x[s].ravel().astype(np.float64)
        b = x[s + 1].ravel().astype(np.float64)
        sa, sb = a.std(), b.std()
        if sa < 1e-8 or sb < 1e-8:
            continue
        vals.append(float(np.corrcoef(a, b)[0, 1]))
    return float(np.mean(vals)) if vals else 0.0


def _bundle_stats(active: np.ndarray) -> Tuple[int, float, np.ndarray]:
    """
    active: S,O,R,C bool.
    Collapse orientation; components connect spatial 4-neighbors and adjacent scales.
    Returns component count, largest/active fraction, collapsed active S,R,C.
    """
    a = active.any(axis=1)
    S, R, C = a.shape
    total = int(a.sum())
    if total == 0:
        return 0, 0.0, a
    seen = np.zeros_like(a, bool)
    sizes: List[int] = []
    for s in range(S):
        for y in range(R):
            for x in range(C):
                if not a[s, y, x] or seen[s, y, x]:
                    continue
                stack = [(s, y, x)]
                seen[s, y, x] = True
                n = 0
                while stack:
                    cs, cy, cx = stack.pop()
                    n += 1
                    for ds, dy, dx in ((-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)):
                        ns, ny, nx = cs + ds, cy + dy, cx + dx
                        if 0 <= ns < S and 0 <= ny < R and 0 <= nx < C and a[ns, ny, nx] and not seen[ns, ny, nx]:
                            seen[ns, ny, nx] = True
                            stack.append((ns, ny, nx))
                sizes.append(n)
    return len(sizes), float(max(sizes) / max(total, 1)), a


@dataclass
class LocalFieldCensus:
    cfg: SpectralConfig
    spectral: LocalSpectralAnalyzer = field(init=False)
    tiles: TileAnalyzer = field(init=False)
    spectral_cache: Optional[np.ndarray] = None
    tile_cache: Optional[np.ndarray] = None
    prev_gray: Optional[np.ndarray] = None
    frames: int = 0
    rows: List[dict] = field(default_factory=list)
    spectral_wake_trace: List[np.ndarray] = field(default_factory=list)
    tile_wake_trace: List[np.ndarray] = field(default_factory=list)

    def __post_init__(self):
        self.spectral = LocalSpectralAnalyzer(self.cfg)
        self.tiles = TileAnalyzer(self.cfg)

    def reset(self):
        self.spectral_cache = None
        self.tile_cache = None
        self.prev_gray = None
        self.frames = 0
        self.rows.clear()
        self.spectral_wake_trace.clear()
        self.tile_wake_trace.clear()

    def process(self, frame_bgr: np.ndarray) -> Tuple[FrameMetrics, Dict[str, np.ndarray]]:
        gray = gray01(frame_bgr, self.cfg.analysis_width)
        sobs = self.spectral.analyze(gray)
        tobs = self.tiles.analyze(gray)

        acquisition = self.prev_gray is None
        if acquisition:
            raw_mae = 0.0
            raw_changed = 1
        else:
            raw_mae = float(np.mean(np.abs(gray - self.prev_gray)))
            raw_changed = int(raw_mae > self.cfg.raw_threshold)

        if self.spectral_cache is None:
            swake = np.ones_like(sobs, dtype=bool)
            sdist = np.full_like(sobs, np.inf, dtype=np.float32)
            self.spectral_cache = sobs.copy()
        else:
            denom = np.maximum(0.20, np.abs(self.spectral_cache))
            sdist = np.abs(sobs - self.spectral_cache) / denom
            swake = sdist > self.cfg.tolerance
            self.spectral_cache[swake] = sobs[swake]

        if self.tile_cache is None:
            twake = np.ones_like(tobs, dtype=bool)
            tdist = np.full_like(tobs, np.inf, dtype=np.float32)
            self.tile_cache = tobs.copy()
        else:
            tdist = np.abs(tobs - self.tile_cache)
            twake = tdist > self.cfg.tile_tolerance
            self.tile_cache[twake] = tobs[twake]

        bundle_count, largest_bundle_fraction, collapsed = _bundle_stats(swake)
        active_spatial = swake.any(axis=(0, 1))
        active_cells = int(active_spatial.sum())
        total_cells = int(active_spatial.size)

        total_packets = int(swake.size)
        active_packets = int(swake.sum())
        spectral_wake_fraction = float(active_packets / total_packets)
        spectral_spatial_fanout = float(active_cells / total_cells)
        tile_wake_fraction = float(twake.mean())
        cross_scale = _cross_scale_agreement(sobs)

        m = FrameMetrics(
            frame_index=self.frames,
            raw_mae=raw_mae,
            raw_changed=raw_changed,
            spectral_wake_fraction=spectral_wake_fraction,
            spectral_spatial_fanout=spectral_spatial_fanout,
            tile_wake_fraction=tile_wake_fraction,
            any_spectral=int(active_packets > 0),
            cross_scale_agreement=cross_scale,
            active_bundle_count=bundle_count,
            largest_bundle_fraction=largest_bundle_fraction,
            active_packet_count=active_packets,
            total_packet_count=total_packets,
            active_cells=active_cells,
            total_cells=total_cells,
        )

        row = m.__dict__.copy()
        for si in range(swake.shape[0]):
            row[f"scale_{si}_wake_fraction"] = float(swake[si].mean())
        self.rows.append(row)
        self.spectral_wake_trace.append(np.packbits(swake.reshape(-1)))
        self.tile_wake_trace.append(np.packbits(twake.reshape(-1)))
        self.prev_gray = gray
        self.frames += 1

        visuals = {
            "gray": gray,
            "spectral_obs": sobs,
            "spectral_wake": swake,
            "spectral_dist": sdist,
            "tile_obs": tobs,
            "tile_wake": twake,
            "collapsed_active": collapsed,
        }
        return m, visuals

    def summary(self) -> dict:
        steady = self.rows[1:] if len(self.rows) > 1 else self.rows
        def mean(key: str) -> float:
            return float(np.mean([r[key] for r in steady])) if steady else 0.0
        return {
            "frames_used": len(self.rows),
            "steady_steps": max(0, len(self.rows) - 1),
            "analysis_width": self.cfg.analysis_width,
            "grid": [self.cfg.grid_rows, self.cfg.grid_cols],
            "wavelengths": list(self.cfg.wavelengths),
            "orientations_deg": list(self.cfg.orientations_deg),
            "spectral_tolerance": self.cfg.tolerance,
            "tile_tolerance": self.cfg.tile_tolerance,
            "raw_threshold": self.cfg.raw_threshold,
            "raw_change_rate": mean("raw_changed"),
            "spectral_packet_wake_fraction": mean("spectral_wake_fraction"),
            "spectral_spatial_routing_fanout": mean("spectral_spatial_fanout"),
            "tile_wake_fraction": mean("tile_wake_fraction"),
            "any_spectral_rate": mean("any_spectral"),
            "cross_scale_agreement": mean("cross_scale_agreement"),
            "mean_bundle_count": mean("active_bundle_count"),
            "mean_largest_bundle_fraction": mean("largest_bundle_fraction"),
            "warning": "Dense Gabor and tile analyzers run every frame. This is an opportunity/locality instrument, not measured sparse-runtime speedup.",
        }


def _heatmap01(x: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    a = np.asarray(x, np.float32)
    if a.ndim != 2:
        raise ValueError("heatmap expects 2D")
    lo, hi = float(a.min()), float(a.max())
    if hi - lo < 1e-8:
        n = np.zeros_like(a, np.uint8)
    else:
        n = np.clip((a - lo) / (hi - lo), 0, 1)
        n = (n * 255).astype(np.uint8)
    hm = cv2.applyColorMap(n, cv2.COLORMAP_TURBO)
    return cv2.resize(hm, size, interpolation=cv2.INTER_NEAREST)


def _binary_map(x: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    n = (np.asarray(x, bool).astype(np.uint8) * 255)
    hm = cv2.applyColorMap(n, cv2.COLORMAP_HOT)
    return cv2.resize(hm, size, interpolation=cv2.INTER_NEAREST)


def _bgr_to_photo(bgr: np.ndarray, size: Tuple[int, int]) -> ImageTk.PhotoImage:
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb).resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(pil)


class SpectralFieldGUI:
    def __init__(self, root: tk.Tk, args):
        self.root = root
        self.args = args
        self.root.title("CC0-A3 Local Spectral Field — dense oracle / not runtime speed")
        self.root.geometry("1400x900")

        self.cap: Optional[cv2.VideoCapture] = None
        self.running = False
        self.source_kind = "webcam"
        self.source_name = "camera"
        self.census: Optional[LocalFieldCensus] = None
        self.last_visuals: Optional[Dict[str, np.ndarray]] = None
        self.last_metrics: Optional[FrameMetrics] = None
        self.started_at: Optional[float] = None

        self.camera_var = tk.IntVar(value=args.camera)
        self.tol_var = tk.DoubleVar(value=args.tolerance)
        self.tile_tol_var = tk.DoubleVar(value=args.tile_tolerance)
        self.width_var = tk.IntVar(value=args.analysis_width)
        self.status_var = tk.StringVar(value="Stopped")
        self.scale_view_var = tk.IntVar(value=2)

        self.metric_vars = {
            "raw": tk.StringVar(value="raw change: --"),
            "spec": tk.StringVar(value="spectral packet wake: --"),
            "fanout": tk.StringVar(value="spatial fanout: --"),
            "tile": tk.StringVar(value="tile wake: --"),
            "scale": tk.StringVar(value="cross-scale agreement: --"),
            "bundle": tk.StringVar(value="bundles: --"),
        }

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)
        ttk.Label(top, text="ORACLE CENSUS — Gabor bank is still computed densely", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=(0, 16))
        ttk.Label(top, textvariable=self.status_var).pack(side=tk.LEFT)

        controls = ttk.LabelFrame(self.root, text="Controls", padding=8)
        controls.pack(fill=tk.X, padx=8, pady=(0, 8))
        ttk.Label(controls, text="Camera").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(controls, from_=0, to=8, textvariable=self.camera_var, width=5).grid(row=0, column=1, padx=4)
        ttk.Label(controls, text="Spectral tol").grid(row=0, column=2, sticky="w", padx=(10,0))
        ttk.Entry(controls, textvariable=self.tol_var, width=8).grid(row=0, column=3, padx=4)
        ttk.Label(controls, text="Tile tol").grid(row=0, column=4, sticky="w", padx=(10,0))
        ttk.Entry(controls, textvariable=self.tile_tol_var, width=8).grid(row=0, column=5, padx=4)
        ttk.Label(controls, text="Analysis width").grid(row=0, column=6, sticky="w", padx=(10,0))
        ttk.Entry(controls, textvariable=self.width_var, width=7).grid(row=0, column=7, padx=4)
        ttk.Label(controls, text="View scale").grid(row=0, column=8, sticky="w", padx=(10,0))
        ttk.Spinbox(controls, from_=0, to=5, textvariable=self.scale_view_var, width=4).grid(row=0, column=9, padx=4)

        self.start_btn = ttk.Button(controls, text="Start webcam", command=self.start_webcam)
        self.start_btn.grid(row=0, column=10, padx=(14,4))
        ttk.Button(controls, text="Load video", command=self.load_video).grid(row=0, column=11, padx=4)
        ttk.Button(controls, text="Stop", command=self.stop).grid(row=0, column=12, padx=4)
        ttk.Button(controls, text="Reset", command=self.reset).grid(row=0, column=13, padx=4)
        ttk.Button(controls, text="Save receipt", command=self.save_receipt).grid(row=0, column=14, padx=4)

        metrics = ttk.LabelFrame(self.root, text="Live locality / invalidation metrics", padding=8)
        metrics.pack(fill=tk.X, padx=8, pady=(0,8))
        for i, key in enumerate(("raw","spec","fanout","tile","scale","bundle")):
            ttk.Label(metrics, textvariable=self.metric_vars[key], width=35).grid(row=i//3, column=i%3, sticky="w", padx=4, pady=2)

        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)
        for c in range(3):
            main.columnconfigure(c, weight=1)
        for r in range(2):
            main.rowconfigure(r, weight=1)

        self.panels: Dict[str, ttk.Label] = {}
        specs = [
            ("camera", "Camera / video", 0, 0),
            ("energy", "Selected localized spectral scale (orientation mean)", 0, 1),
            ("active", "Active spectral routing cells (space x scale)", 0, 2),
            ("scale", "Scale-space energy strips", 1, 0),
            ("tile", "Plain spatial tile wake baseline", 1, 1),
            ("info", "Interpretation", 1, 2),
        ]
        for key, title, row, col in specs:
            box = ttk.LabelFrame(main, text=title, padding=5)
            box.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            lbl = ttk.Label(box, anchor="center")
            lbl.pack(fill=tk.BOTH, expand=True)
            self.panels[key] = lbl

    def _make_cfg(self) -> SpectralConfig:
        return SpectralConfig(
            analysis_width=max(96, int(self.width_var.get())),
            tolerance=max(0.001, float(self.tol_var.get())),
            tile_tolerance=max(0.001, float(self.tile_tol_var.get())),
        )

    def _open_capture(self, source, kind: str, name: str):
        self.stop()
        cfg = self._make_cfg()
        pref = cv2.CAP_DSHOW if kind == "webcam" and platform.system() == "Windows" else cv2.CAP_ANY
        cap = cv2.VideoCapture(source, pref)
        if not cap.isOpened() and kind == "webcam" and pref != cv2.CAP_ANY:
            cap.release()
            cap = cv2.VideoCapture(source, cv2.CAP_ANY)
        if not cap.isOpened():
            messagebox.showerror("Open failed", f"Could not open {name}")
            return
        if kind == "webcam":
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap = cap
        self.census = LocalFieldCensus(cfg)
        self.source_kind = kind
        self.source_name = name
        self.running = True
        self.started_at = time.perf_counter()
        self.status_var.set(f"Running: {name}")
        self._tick()

    def start_webcam(self):
        self._open_capture(int(self.camera_var.get()), "webcam", f"camera {int(self.camera_var.get())}")

    def load_video(self):
        p = filedialog.askopenfilename(title="Choose video", filetypes=[("Video", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")])
        if p:
            self._open_capture(p, "video", p)

    def stop(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.status_var:
            self.status_var.set("Stopped")

    def reset(self):
        if self.census is not None:
            self.census.reset()
        self.last_visuals = None
        self.last_metrics = None
        self.started_at = time.perf_counter()
        self.status_var.set("Reset; continue current source" if self.running else "Reset")

    def _tick(self):
        if not self.running or self.cap is None or self.census is None:
            return
        ok, frame = self.cap.read()
        if not ok:
            if self.source_kind == "video":
                self.stop()
                self.status_var.set("Video finished")
            else:
                self.status_var.set("Camera read failed")
                self.root.after(100, self._tick)
            return
        try:
            m, v = self.census.process(frame)
            self.last_metrics, self.last_visuals = m, v
            self._update_metrics(m)
            self._update_panels(frame, m, v)
        except Exception as e:
            self.stop()
            messagebox.showerror("Processing error", str(e))
            return
        self.root.after(1, self._tick)

    def _set_panel(self, key: str, bgr: np.ndarray, size=(400, 280)):
        photo = _bgr_to_photo(bgr, size)
        self.panels[key].configure(image=photo)
        self.panels[key].image = photo

    def _update_metrics(self, m: FrameMetrics):
        s = self.census.summary() if self.census else {}
        self.metric_vars["raw"].set(f"raw change: {s.get('raw_change_rate',0):.3f}   MAE {m.raw_mae:.4f}")
        self.metric_vars["spec"].set(f"spectral packet wake: {s.get('spectral_packet_wake_fraction',0):.3f}   now {m.spectral_wake_fraction:.3f}")
        self.metric_vars["fanout"].set(f"spatial routing fanout: {s.get('spectral_spatial_routing_fanout',0):.3f}   now {m.spectral_spatial_fanout:.3f}")
        self.metric_vars["tile"].set(f"plain tile wake: {s.get('tile_wake_fraction',0):.3f}   now {m.tile_wake_fraction:.3f}")
        self.metric_vars["scale"].set(f"cross-scale agreement: {s.get('cross_scale_agreement',0):+.3f}   now {m.cross_scale_agreement:+.3f}")
        self.metric_vars["bundle"].set(f"bundles now: {m.active_bundle_count}   largest share {m.largest_bundle_fraction:.2f}")

    def _update_panels(self, frame: np.ndarray, m: FrameMetrics, v: Dict[str, np.ndarray]):
        self._set_panel("camera", frame)

        energy = v["spectral_obs"].mean(axis=1)
        sv = int(np.clip(self.scale_view_var.get(), 0, energy.shape[0]-1))
        selected = energy[sv]
        selected_vis = _heatmap01(selected, (400, 280))
        cv2.putText(selected_vis, f"scale {sv}  wavelength~{self.census.cfg.wavelengths[sv]:g}px", (8,22), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1, cv2.LINE_AA)
        self._set_panel("energy", selected_vis)

        active = v["spectral_wake"].any(axis=1).astype(np.float32)
        active_strip = np.concatenate([active[s] for s in range(active.shape[0])], axis=1)
        self._set_panel("active", _binary_map(active_strip > 0, (400, 280)))

        prof = energy.mean(axis=1)
        self._set_panel("scale", _heatmap01(prof, (400, 280)))

        tile_active = v["tile_wake"].any(axis=0)
        self._set_panel("tile", _binary_map(tile_active, (400, 280)))

        info = np.zeros((280, 400, 3), np.uint8)
        lines = [
            "QUESTION:",
            "Does change stay local in space x scale x time?",
            "",
            f"packets active now: {m.active_packet_count}/{m.total_packet_count}",
            f"spatial cells addressed: {m.active_cells}/{m.total_cells}",
            f"cross-scale agreement: {m.cross_scale_agreement:+.3f}",
            f"bundle count: {m.active_bundle_count}",
            f"largest bundle share: {m.largest_bundle_fraction:.2f}",
            "",
            "ATTACKER:",
            f"plain tile wake now: {m.tile_wake_fraction:.3f}",
            "",
            "Dense oracle only. Pretty != fast.",
        ]
        y = 24
        for line in lines:
            cv2.putText(info, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (235,235,235), 1, cv2.LINE_AA)
            y += 20
        self._set_panel("info", info)

    def save_receipt(self):
        if self.census is None or not self.census.rows:
            messagebox.showinfo("Nothing to save", "Run the webcam or a video first.")
            return
        outdir = Path(self.args.out_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        sid = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = outdir / f"cc0a3_spectral_field_{sid}"
        summary = self.census.summary()
        summary.update({
            "session_id": sid,
            "source_kind": self.source_kind,
            "source_name": self.source_name,
            "elapsed_s": float(time.perf_counter() - self.started_at) if self.started_at else None,
            "platform": platform.platform(),
            "opencv_version": cv2.__version__,
        })
        prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        keys = list(self.census.rows[0].keys())
        with prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=keys)
            wr.writeheader()
            wr.writerows(self.census.rows)
        txt = [
            "CC0-A3 LOCAL SPECTRAL FIELD",
            "=" * 72,
            f"source                    : {self.source_kind} {self.source_name}",
            f"frames                    : {summary['frames_used']}",
            f"raw change rate           : {summary['raw_change_rate']:.6f}",
            f"spectral packet wake frac : {summary['spectral_packet_wake_fraction']:.6f}",
            f"spatial routing fanout    : {summary['spectral_spatial_routing_fanout']:.6f}",
            f"plain tile wake frac      : {summary['tile_wake_fraction']:.6f}",
            f"cross-scale agreement     : {summary['cross_scale_agreement']:+.6f}",
            f"mean bundle count         : {summary['mean_bundle_count']:.3f}",
            f"largest bundle share      : {summary['mean_largest_bundle_fraction']:.6f}",
            "",
            "WARNING:",
            summary["warning"],
        ]
        prefix.with_suffix(".txt").write_text("\n".join(txt) + "\n", encoding="utf-8")
        if self.census.spectral_wake_trace:
            np.savez_compressed(
                prefix.with_name(prefix.name + "_wake_trace.npz"),
                spectral_wake_packed=np.stack(self.census.spectral_wake_trace),
                tile_wake_packed=np.stack(self.census.tile_wake_trace),
                spectral_shape=np.asarray(self.census.spectral.shape, dtype=np.int32),
                tile_shape=np.asarray((2, self.census.cfg.grid_rows, self.census.cfg.grid_cols), dtype=np.int32),
                wavelengths=np.asarray(self.census.cfg.wavelengths, dtype=np.float32),
                orientations_deg=np.asarray(self.census.cfg.orientations_deg, dtype=np.float32),
            )
        messagebox.showinfo("Receipt saved", f"Saved:\n{prefix.with_suffix('.txt')}\n{prefix.with_suffix('.json')}\n{prefix.with_suffix('.csv')}\n{prefix.with_name(prefix.name + '_wake_trace.npz')}")

    def close(self):
        self.stop()
        self.root.destroy()


def self_test() -> None:
    cfg = SpectralConfig(analysis_width=128)
    census = LocalFieldCensus(cfg)
    h, w = 96, 128
    rng = np.random.default_rng(4)
    for t in range(24):
        img = np.zeros((h, w, 3), np.uint8)
        cv2.rectangle(img, (20, 20), (85, 75), (70, 70, 70), -1)
        x = 10 + (t * 3) % 90
        cv2.rectangle(img, (x, 42), (x + 10, 58), (220, 220, 220), -1)
        noise = rng.normal(0, 2, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        m, v = census.process(img)
        assert v["spectral_obs"].shape == census.spectral.shape
        assert 0 <= m.spectral_wake_fraction <= 1
        assert 0 <= m.spectral_spatial_fanout <= 1
        assert 0 <= m.tile_wake_fraction <= 1
    s = census.summary()
    assert s["frames_used"] == 24
    print("CC0-A3 self-test PASS")
    print(json.dumps(s, indent=2))


def main():
    ap = argparse.ArgumentParser(description="CC0-A3 localized spectral field GUI")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--analysis-width", type=int, default=128)
    ap.add_argument("--tolerance", type=float, default=0.35)
    ap.add_argument("--tile-tolerance", type=float, default=0.08)
    ap.add_argument("--out-dir", type=str, default="results/cc0a3_spectral_field_runs")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    root = tk.Tk()
    SpectralFieldGUI(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()
