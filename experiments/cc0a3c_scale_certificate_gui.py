from __future__ import annotations

"""CC0-A3C: cross-scale multiplicity as a local persistence certificate.

A3/A3B showed that localized spectral wake activity often repeats across nearby
scales.  A3C keeps physical (x,y) fixed, collapses orientation, counts how many
scales wake at each spatial cell, and asks whether higher multiplicity predicts
future local activity.

Persistence is evaluated at lags 1, 2, 4, and 8 frames.  A source cell counts
as persistent if the future wake mask contains activity at the same cell or a
one-cell spatial neighbor.  The one-cell allowance prevents ordinary motion
from making a persistent moving structure look like a failure.

This remains a DENSE ORACLE.  The full Gabor bank is still computed every
frame.  It measures candidate certificate value, not sparse-runtime speed.
"""

import argparse
import csv
import json
import platform
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from typing import Dict, List

import cv2
import numpy as np

import cc0a3b_local_spectral_field_fixednorm_gui as a3b

base = a3b.base
LAGS = (1, 2, 4, 8)


def _dilate_one(mask: np.ndarray) -> np.ndarray:
    """Allow persistence to move by one spatial cell in any direction."""
    kernel = np.ones((3, 3), np.uint8)
    return cv2.dilate(mask.astype(np.uint8), kernel, iterations=1).astype(bool)


class CertificateCensus(a3b.FixedNormCensus):
    def __post_init__(self):
        super().__post_init__()
        self._reset_certificate_state()

    def _reset_certificate_state(self):
        s_count = len(self.cfg.wavelengths)
        self.multiplicity_history: List[np.ndarray] = []
        self.tile_active_history: List[np.ndarray] = []
        self.multiplicity_trace: List[np.ndarray] = []
        self.persist_den: Dict[int, np.ndarray] = {
            lag: np.zeros(s_count + 1, dtype=np.int64) for lag in LAGS
        }
        self.persist_hit: Dict[int, np.ndarray] = {
            lag: np.zeros(s_count + 1, dtype=np.int64) for lag in LAGS
        }
        self.tile_den: Dict[int, int] = {lag: 0 for lag in LAGS}
        self.tile_hit: Dict[int, int] = {lag: 0 for lag in LAGS}

    def reset(self):
        super().reset()
        self._reset_certificate_state()

    def process(self, frame_bgr: np.ndarray):
        m, visuals = super().process(frame_bgr)

        # S,O,R,C -> S,R,C -> R,C. Multiplicity means number of scales with
        # at least one orientation crossing tolerance at this physical cell.
        scale_active = visuals["spectral_wake"].any(axis=1)
        multiplicity = scale_active.sum(axis=0).astype(np.uint8)
        spectral_active = multiplicity > 0
        tile_active = visuals["tile_wake"].any(axis=0)

        active_n = int(spectral_active.sum())
        multiscale = multiplicity >= 2
        multiscale_n = int(multiscale.sum())
        mean_mult = float(multiplicity[spectral_active].mean()) if active_n else 0.0
        multiscale_share = float(multiscale_n / active_n) if active_n else 0.0
        multiscale_fanout = float(multiscale.mean())

        # Evaluate old source multiplicities against the current target wake.
        # We use one-cell target dilation so a moving hand can remain the same
        # local structure without requiring pixel-perfect stationarity.
        target_spec = _dilate_one(spectral_active)
        target_tile = _dilate_one(tile_active)
        s_count = len(self.cfg.wavelengths)
        for lag in LAGS:
            if len(self.multiplicity_history) >= lag:
                src_mult = self.multiplicity_history[-lag]
                for k in range(1, s_count + 1):
                    src = src_mult == k
                    n = int(src.sum())
                    if n:
                        self.persist_den[lag][k] += n
                        self.persist_hit[lag][k] += int(np.logical_and(src, target_spec).sum())

                src_tile = self.tile_active_history[-lag]
                nt = int(src_tile.sum())
                if nt:
                    self.tile_den[lag] += nt
                    self.tile_hit[lag] += int(np.logical_and(src_tile, target_tile).sum())

        self.multiplicity_history.append(multiplicity.copy())
        self.tile_active_history.append(tile_active.copy())
        self.multiplicity_trace.append(multiplicity.copy())

        row = self.rows[-1]
        row["mean_scale_multiplicity_when_active"] = mean_mult
        row["multiscale_cell_share_among_active"] = multiscale_share
        row["multiscale_spatial_fanout"] = multiscale_fanout
        for k in range(1, s_count + 1):
            row[f"multiplicity_{k}_cells"] = int(np.sum(multiplicity == k))

        visuals["scale_active"] = scale_active
        visuals["multiplicity"] = multiplicity
        visuals["multiscale_certificate"] = multiscale
        return m, visuals

    def _persistence_summary(self) -> dict:
        s_count = len(self.cfg.wavelengths)
        out = {}
        for lag in LAGS:
            by_m = {}
            for k in range(1, s_count + 1):
                den = int(self.persist_den[lag][k])
                hit = int(self.persist_hit[lag][k])
                by_m[str(k)] = {
                    "rate": float(hit / den) if den else None,
                    "support_cells": den,
                    "hits": hit,
                }

            single_den = int(self.persist_den[lag][1])
            single_hit = int(self.persist_hit[lag][1])
            multi_den = int(self.persist_den[lag][2:].sum())
            multi_hit = int(self.persist_hit[lag][2:].sum())
            tile_den = int(self.tile_den[lag])
            tile_hit = int(self.tile_hit[lag])
            single_rate = float(single_hit / single_den) if single_den else None
            multi_rate = float(multi_hit / multi_den) if multi_den else None
            tile_rate = float(tile_hit / tile_den) if tile_den else None
            delta = (
                float(multi_rate - single_rate)
                if multi_rate is not None and single_rate is not None
                else None
            )
            out[str(lag)] = {
                "by_multiplicity": by_m,
                "single_scale_rate": single_rate,
                "single_scale_support": single_den,
                "multi_scale_rate": multi_rate,
                "multi_scale_support": multi_den,
                "multi_minus_single": delta,
                "plain_tile_rate": tile_rate,
                "plain_tile_support": tile_den,
                "spatial_tolerance_cells": 1,
            }
        return out

    def summary(self) -> dict:
        s = super().summary()
        steady = self.rows[1:] if len(self.rows) > 1 else self.rows

        def mean(key: str) -> float:
            vals = [float(r.get(key, 0.0)) for r in steady]
            return float(np.mean(vals)) if vals else 0.0

        s["mean_scale_multiplicity_when_active"] = mean("mean_scale_multiplicity_when_active")
        s["multiscale_cell_share_among_active"] = mean("multiscale_cell_share_among_active")
        s["multiscale_spatial_fanout"] = mean("multiscale_spatial_fanout")
        s["persistence_lags_frames"] = list(LAGS)
        s["persistence_spatial_tolerance_cells"] = 1
        s["persistence_by_scale_multiplicity"] = self._persistence_summary()
        s["hypothesis"] = (
            "If cross-scale multiplicity is a useful local persistence certificate, "
            "future local wake probability should increase from multiplicity=1 toward "
            "higher multiplicity, and aggregate multi-scale wake should persist more "
            "often than single-scale wake."
        )
        s["warning"] = (
            "Dense Gabor and tile analyzers still run every frame. A3C tests whether "
            "cross-scale wake multiplicity predicts future local wake; it is not a "
            "runtime speedup measurement."
        )
        return s


# SpectralFieldGUI._open_capture resolves this module-global name in base.
base.LocalFieldCensus = CertificateCensus


def _multiplicity_bgr(mult: np.ndarray, n_scales: int, size=(400, 280)) -> np.ndarray:
    val = np.clip(mult.astype(np.float32) / max(1, n_scales), 0.0, 1.0)
    u8 = (val * 255).astype(np.uint8)
    hm = cv2.applyColorMap(u8, cv2.COLORMAP_TURBO)
    hm[mult == 0] = 0
    hm = cv2.resize(hm, size, interpolation=cv2.INTER_NEAREST)
    return hm


class A3CGUI(a3b.A3BGUI):
    def __init__(self, root: tk.Tk, args):
        super().__init__(root, args)
        self.root.title("CC0-A3C Cross-Scale Certificate — multiplicity predicts persistence?")
        self.panels["active"].master.configure(text="Cross-scale multiplicity at fixed physical x,y")
        self.panels["scale"].master.configure(text="Multi-scale certificate cells (>=2 scales)")
        self.panels["info"].master.configure(text="Persistence test: multiplicity -> future local wake")

    def _update_metrics(self, m: base.FrameMetrics):
        super()._update_metrics(m)
        if not self.census or not self.census.rows:
            return
        s = self.census.summary()
        self.metric_vars["fanout"].set(
            f"spectral fanout: {s.get('spectral_spatial_routing_fanout',0):.3f}   "
            f">=2-scale fanout: {s.get('multiscale_spatial_fanout',0):.3f}"
        )
        self.metric_vars["scale"].set(
            f"mean scales/active cell: {s.get('mean_scale_multiplicity_when_active',0):.2f}   "
            f"multi-scale share: {s.get('multiscale_cell_share_among_active',0):.3f}"
        )
        self.metric_vars["bundle"].set(
            f"cross-scale obs agreement: {s.get('cross_scale_agreement',0):+.3f}   "
            f"bundles now {m.active_bundle_count}   largest {m.largest_bundle_fraction:.2f}"
        )

    def _update_panels(self, frame: np.ndarray, m: base.FrameMetrics, v: Dict[str, np.ndarray]):
        # Let A3B render camera, selected scale, and tile baseline first.
        super()._update_panels(frame, m, v)

        mult = v["multiplicity"]
        n_scales = len(self.census.cfg.wavelengths)
        mult_vis = _multiplicity_bgr(mult, n_scales)
        cv2.putText(
            mult_vis,
            "0 black; color = number of waking scales (1..6)",
            (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255,255,255), 1, cv2.LINE_AA,
        )
        self._set_panel("active", mult_vis)

        cert = v["multiscale_certificate"]
        cert_vis = base._binary_map(cert, (400, 280))
        cv2.putText(
            cert_vis,
            ">=2 scales agree at same physical cell",
            (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255,255,255), 1, cv2.LINE_AA,
        )
        self._set_panel("scale", cert_vis)

        s = self.census.summary()
        p = s.get("persistence_by_scale_multiplicity", {})
        info = np.zeros((280, 400, 3), np.uint8)
        lines = [
            "HYPOTHESIS:",
            "more scales agree -> wake persists longer",
            "future match allows +/-1 spatial cell",
            "",
            f"active cells now: {int((mult>0).sum())}/{mult.size}",
            f">=2 scales now: {int((mult>=2).sum())}/{mult.size}",
            f"mean multiplicity now: {float(mult[mult>0].mean()) if np.any(mult>0) else 0:.2f}",
            "",
            "lag   single   multi   delta   tiles",
        ]
        for lag in LAGS:
            q = p.get(str(lag), {})
            sr = q.get("single_scale_rate")
            mr = q.get("multi_scale_rate")
            dr = q.get("multi_minus_single")
            tr = q.get("plain_tile_rate")
            fmt = lambda x: " -- " if x is None else f"{x:5.2f}"
            lines.append(f"{lag:>2}f   {fmt(sr)}   {fmt(mr)}   {fmt(dr)}   {fmt(tr)}")
        lines += ["", "Positive multi-single across lags = interesting.", "Dense oracle only. Pretty != fast."]

        y = 20
        for line in lines:
            cv2.putText(info, line, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (235,235,235), 1, cv2.LINE_AA)
            y += 18
        self._set_panel("info", info)

    def save_receipt(self):
        if self.census is None or not self.census.rows:
            messagebox.showinfo("Nothing to save", "Run the webcam or a video first.")
            return

        outdir = Path(self.args.out_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        sid = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = outdir / f"cc0a3c_scale_certificate_{sid}"
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
        for r in self.census.rows[1:]:
            for k in r.keys():
                if k not in keys:
                    keys.append(k)
        with prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=keys)
            wr.writeheader()
            wr.writerows(self.census.rows)

        txt = [
            "CC0-A3C CROSS-SCALE PERSISTENCE CERTIFICATE",
            "=" * 72,
            f"source                         : {self.source_kind} {self.source_name}",
            f"frames                         : {summary['frames_used']}",
            f"raw change rate                : {summary['raw_change_rate']:.6f}",
            f"spectral packet wake frac      : {summary['spectral_packet_wake_fraction']:.6f}",
            f"spectral spatial fanout        : {summary['spectral_spatial_routing_fanout']:.6f}",
            f"multi-scale (>=2) fanout       : {summary['multiscale_spatial_fanout']:.6f}",
            f"tile spatial fanout            : {summary.get('tile_spatial_routing_fanout',0):.6f}",
            f"mean scales per active cell    : {summary['mean_scale_multiplicity_when_active']:.6f}",
            f"multi-scale share active cells : {summary['multiscale_cell_share_among_active']:.6f}",
            f"cross-scale obs agreement      : {summary['cross_scale_agreement']:+.6f}",
            "",
            "Persistence: future local wake within +/-1 spatial cell",
            "lag   single-scale   multi-scale   delta(multi-single)   tiles",
        ]
        for lag in LAGS:
            q = summary["persistence_by_scale_multiplicity"][str(lag)]
            def fmt(x):
                return "NA" if x is None else f"{x:.6f}"
            txt.append(
                f"{lag:>2}    {fmt(q['single_scale_rate']):>12}   {fmt(q['multi_scale_rate']):>12}   "
                f"{fmt(q['multi_minus_single']):>18}   {fmt(q['plain_tile_rate']):>12}"
            )
        txt += ["", "WARNING:", summary["warning"]]
        prefix.with_suffix(".txt").write_text("\n".join(txt) + "\n", encoding="utf-8")

        if self.census.spectral_wake_trace:
            np.savez_compressed(
                prefix.with_name(prefix.name + "_trace.npz"),
                spectral_wake_packed=np.stack(self.census.spectral_wake_trace),
                tile_wake_packed=np.stack(self.census.tile_wake_trace),
                multiplicity=np.stack(self.census.multiplicity_trace).astype(np.uint8),
                spectral_shape=np.asarray(self.census.spectral.shape, dtype=np.int32),
                tile_shape=np.asarray((2, self.census.cfg.grid_rows, self.census.cfg.grid_cols), dtype=np.int32),
                wavelengths=np.asarray(self.census.cfg.wavelengths, dtype=np.float32),
                orientations_deg=np.asarray(self.census.cfg.orientations_deg, dtype=np.float32),
                lags=np.asarray(LAGS, dtype=np.int32),
            )

        messagebox.showinfo(
            "Receipt saved",
            f"Saved:\n{prefix.with_suffix('.txt')}\n{prefix.with_suffix('.json')}\n"
            f"{prefix.with_suffix('.csv')}\n{prefix.with_name(prefix.name + '_trace.npz')}",
        )


def self_test() -> None:
    cfg = base.SpectralConfig(analysis_width=128)
    census = CertificateCensus(cfg)
    h, w = 96, 128
    rng = np.random.default_rng(7)
    for t in range(40):
        img = np.zeros((h, w, 3), np.uint8)
        cv2.rectangle(img, (8, 10), (118, 85), (45, 45, 45), -1)
        x = 14 + (t * 2) % 90
        cv2.rectangle(img, (x, 28), (x + 14, 72), (220, 220, 220), -1)
        cv2.line(img, (x, 20), (x + 10, 82), (120, 120, 120), 2)
        noise = rng.normal(0, 1.5, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        m, v = census.process(img)
        assert v["multiplicity"].shape == (cfg.grid_rows, cfg.grid_cols)
        assert int(v["multiplicity"].max()) <= len(cfg.wavelengths)
    s = census.summary()
    assert s["frames_used"] == 40
    assert len(census.multiplicity_trace) == 40
    assert set(s["persistence_by_scale_multiplicity"].keys()) == {"1", "2", "4", "8"}
    print("CC0-A3C self-test PASS")
    print(json.dumps(s, indent=2))


def main():
    ap = argparse.ArgumentParser(description="CC0-A3C cross-scale persistence certificate GUI")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--analysis-width", type=int, default=128)
    ap.add_argument("--tolerance", type=float, default=0.35)
    ap.add_argument("--tile-tolerance", type=float, default=0.08)
    ap.add_argument("--out-dir", type=str, default="results/cc0a3c_scale_certificate_runs")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    root = tk.Tk()
    A3CGUI(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()
