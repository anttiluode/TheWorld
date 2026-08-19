from __future__ import annotations

import argparse
import csv
import json
import platform
import time
import tkinter as tk
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Dict, List, Optional

import cv2
import numpy as np

from cc0a_invalidation_census import (
    SPECS,
    gray01,
    output_distance,
    receiver_outputs,
)


@dataclass
class LiveCensus:
    tolerance_scale: float = 0.35
    raw_threshold: float = 0.0005
    analysis_width: int = 192
    cached: Dict[str, np.ndarray] = field(default_factory=dict)
    prev_gray: Optional[np.ndarray] = None
    frames: int = 0
    steady_steps: int = 0
    raw_count: int = 0
    any_count: int = 0
    active_total: int = 0
    wake_counts: Dict[str, int] = field(default_factory=lambda: {name: 0 for name in SPECS})
    rows: List[dict] = field(default_factory=list)
    started_at: float = field(default_factory=time.perf_counter)

    def reset(self) -> None:
        self.cached.clear()
        self.prev_gray = None
        self.frames = 0
        self.steady_steps = 0
        self.raw_count = 0
        self.any_count = 0
        self.active_total = 0
        self.wake_counts = {name: 0 for name in SPECS}
        self.rows.clear()
        self.started_at = time.perf_counter()

    def process(self, frame: np.ndarray) -> dict:
        h, w = frame.shape[:2]
        resize_h = max(1, int(round(h * self.analysis_width / max(1, w))))
        gray = gray01(frame, (self.analysis_width, resize_h))
        outs = receiver_outputs(gray, self.prev_gray)

        acquisition = self.prev_gray is None
        if acquisition:
            mae = 0.0
            raw_changed = 1
        else:
            mae = float(np.mean(np.abs(gray - self.prev_gray)))
            raw_changed = int(mae > self.raw_threshold)

        wake: Dict[str, int] = {}
        distance: Dict[str, float] = {}
        for name in SPECS:
            y = outs[name]
            if name not in self.cached:
                woken = 1
                d = float("inf")
                self.cached[name] = y.copy()
            else:
                d = output_distance(y, self.cached[name])
                woken = int(d > SPECS[name].tolerance * self.tolerance_scale)
                if woken:
                    self.cached[name] = y.copy()
            wake[name] = woken
            distance[name] = d

        active_count = int(sum(wake.values()))
        any_changed = int(active_count > 0)

        if not acquisition:
            self.steady_steps += 1
            self.raw_count += raw_changed
            self.any_count += any_changed
            self.active_total += active_count
            for name, value in wake.items():
                self.wake_counts[name] += value

        row = {
            "frame": self.frames,
            "time_s": time.perf_counter() - self.started_at,
            "acquisition": int(acquisition),
            "frame_mae": mae,
            "raw_changed": raw_changed,
            "any_receiver_changed": any_changed,
            "active_count": active_count,
            "wake": wake.copy(),
            "distance": distance.copy(),
        }
        self.rows.append(row)
        self.frames += 1
        self.prev_gray = gray
        return row

    def summary(self) -> dict:
        n_receivers = len(SPECS)
        steps = max(1, self.steady_steps)
        raw_rate = self.raw_count / steps if self.steady_steps else 0.0
        any_rate = self.any_count / steps if self.steady_steps else 0.0
        local_fraction = self.active_total / (steps * n_receivers) if self.steady_steps else 0.0
        ratio = any_rate / max(local_fraction, 1e-12) if self.steady_steps else 0.0
        always_ratio = 1.0 / max(local_fraction, 1e-12) if self.steady_steps else 0.0
        return {
            "source_kind": "webcam",
            "frames_used": self.frames,
            "steady_steps": self.steady_steps,
            "raw_threshold_mae": self.raw_threshold,
            "tolerance_scale": self.tolerance_scale,
            "analysis_width": self.analysis_width,
            "raw_change_rate": raw_rate,
            "any_receiver_change_rate": any_rate,
            "mean_receivers_woken_per_step": (
                self.active_total / steps if self.steady_steps else 0.0
            ),
            "fraction_receivers_woken_per_step": local_fraction,
            "global_or_work_fraction_equal_cost": any_rate,
            "oracle_local_work_fraction_equal_cost": local_fraction,
            "global_or_vs_local_ratio_equal_cost": ratio,
            "always_on_vs_local_ratio_equal_cost": always_ratio,
            "receiver_names": list(SPECS),
            "receiver_tolerances": {
                name: SPECS[name].tolerance * self.tolerance_scale for name in SPECS
            },
            "receiver_wake_rates": {
                name: (self.wake_counts[name] / steps if self.steady_steps else 0.0)
                for name in SPECS
            },
            "elapsed_s": time.perf_counter() - self.started_at,
            "warning": (
                "Oracle opportunity census only. Dense receiver outputs are computed on every "
                "frame. Ratios are not measured runtime speedups."
            ),
        }


class CC0AWebcamGUI:
    def __init__(
        self,
        root: tk.Tk,
        camera_index: int,
        tolerance_scale: float,
        raw_threshold: float,
        analysis_width: int,
        results_dir: Path,
    ) -> None:
        self.root = root
        self.root.title("TheWorld — CC0-A2 Webcam Invalidation Census")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.cap: Optional[cv2.VideoCapture] = None
        self.writer: Optional[cv2.VideoWriter] = None
        self.running = False
        self.photo: Optional[tk.PhotoImage] = None
        self.session_id = ""
        self.video_path: Optional[Path] = None
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.camera_var = tk.IntVar(value=camera_index)
        self.tolerance_var = tk.DoubleVar(value=tolerance_scale)
        self.raw_threshold_var = tk.DoubleVar(value=raw_threshold)
        self.analysis_width_var = tk.IntVar(value=analysis_width)
        self.record_var = tk.BooleanVar(value=False)

        self.census = LiveCensus(
            tolerance_scale=tolerance_scale,
            raw_threshold=raw_threshold,
            analysis_width=analysis_width,
        )

        self.metric_vars = {
            "frames": tk.StringVar(value="0"),
            "raw": tk.StringVar(value="—"),
            "any": tk.StringVar(value="—"),
            "local": tk.StringVar(value="—"),
            "ratio": tk.StringVar(value="—"),
            "fps": tk.StringVar(value="—"),
            "status": tk.StringVar(value="camera stopped"),
        }
        self.receiver_status: Dict[str, tk.StringVar] = {
            name: tk.StringVar(value="—") for name in SPECS
        }
        self.receiver_rate: Dict[str, tk.StringVar] = {
            name: tk.StringVar(value="0.000") for name in SPECS
        }
        self.receiver_distance: Dict[str, tk.StringVar] = {
            name: tk.StringVar(value="—") for name in SPECS
        }

        self._build_ui()
        self._last_ui_time = time.perf_counter()
        self._last_ui_frames = 0

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(1, weight=1)

        warning = ttk.Label(
            self.root,
            text="ORACLE CENSUS — NOT RUNTIME SPEED. Dense receivers still run every frame.",
            anchor="center",
            font=("TkDefaultFont", 10, "bold"),
        )
        warning.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))

        left = ttk.Frame(self.root, padding=8)
        left.grid(row=1, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        self.preview = ttk.Label(left, text="Start camera to begin", anchor="center")
        self.preview.grid(row=0, column=0, sticky="nsew")

        controls = ttk.LabelFrame(left, text="Session controls", padding=8)
        controls.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        for c in range(6):
            controls.columnconfigure(c, weight=1)

        ttk.Label(controls, text="Camera").grid(row=0, column=0, sticky="w")
        self.camera_spin = ttk.Spinbox(
            controls, from_=0, to=9, width=5, textvariable=self.camera_var
        )
        self.camera_spin.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ttk.Label(controls, text="Tolerance scale").grid(row=0, column=1, sticky="w")
        self.tolerance_spin = ttk.Spinbox(
            controls,
            from_=0.05,
            to=2.0,
            increment=0.05,
            width=8,
            textvariable=self.tolerance_var,
        )
        self.tolerance_spin.grid(row=1, column=1, sticky="ew", padx=6)

        ttk.Label(controls, text="Raw MAE threshold").grid(row=0, column=2, sticky="w")
        self.raw_spin = ttk.Spinbox(
            controls,
            from_=0.00001,
            to=0.05,
            increment=0.0001,
            width=10,
            textvariable=self.raw_threshold_var,
        )
        self.raw_spin.grid(row=1, column=2, sticky="ew", padx=6)

        ttk.Label(controls, text="Analysis width").grid(row=0, column=3, sticky="w")
        self.analysis_spin = ttk.Spinbox(
            controls,
            from_=96,
            to=512,
            increment=32,
            width=7,
            textvariable=self.analysis_width_var,
        )
        self.analysis_spin.grid(row=1, column=3, sticky="ew", padx=6)

        self.record_check = ttk.Checkbutton(
            controls, text="Record webcam video", variable=self.record_var
        )
        self.record_check.grid(row=0, column=4, columnspan=2, sticky="w", padx=6)

        self.start_button = ttk.Button(controls, text="Start", command=self.toggle_camera)
        self.start_button.grid(row=1, column=4, sticky="ew", padx=6)
        ttk.Button(controls, text="Reset session", command=self.reset_session).grid(
            row=1, column=5, sticky="ew", padx=(6, 0)
        )
        ttk.Button(controls, text="Save receipt", command=self.save_receipt).grid(
            row=2, column=4, sticky="ew", padx=6, pady=(6, 0)
        )
        ttk.Button(controls, text="Open results folder", command=self.open_results_folder).grid(
            row=2, column=5, sticky="ew", padx=(6, 0), pady=(6, 0)
        )
        ttk.Label(
            controls,
            text=(
                "Settings lock while running. Stop/reset before changing tolerance, "
                "so one receipt never mixes epsilon regimes."
            ),
            wraplength=620,
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))

        right = ttk.Frame(self.root, padding=8)
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        metrics = ttk.LabelFrame(right, text="Live opportunity receipt", padding=8)
        metrics.grid(row=0, column=0, sticky="ew")
        labels = [
            ("Frames", "frames"),
            ("Observed FPS", "fps"),
            ("Raw input changed", "raw"),
            ("ANY receiver invalid", "any"),
            ("Receiver slots invalid", "local"),
            ("GLOBAL-OR / local work", "ratio"),
        ]
        for r, (label, key) in enumerate(labels):
            ttk.Label(metrics, text=label).grid(row=r, column=0, sticky="w")
            ttk.Label(metrics, textvariable=self.metric_vars[key], width=16).grid(
                row=r, column=1, sticky="e", padx=(12, 0)
            )
        ttk.Separator(metrics).grid(row=len(labels), column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Label(
            metrics,
            textvariable=self.metric_vars["status"],
            wraplength=330,
        ).grid(row=len(labels) + 1, column=0, columnspan=2, sticky="w")

        receivers = ttk.LabelFrame(right, text="Receiver-local validity", padding=8)
        receivers.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        headers = ("receiver", "now", "wake rate", "distance / tol")
        for c, text in enumerate(headers):
            ttk.Label(receivers, text=text, font=("TkDefaultFont", 9, "bold")).grid(
                row=0, column=c, sticky="w", padx=(0, 8)
            )
        for r, name in enumerate(SPECS, start=1):
            ttk.Label(receivers, text=name).grid(row=r, column=0, sticky="w", padx=(0, 8))
            ttk.Label(receivers, textvariable=self.receiver_status[name], width=7).grid(
                row=r, column=1, sticky="w"
            )
            ttk.Label(receivers, textvariable=self.receiver_rate[name], width=8).grid(
                row=r, column=2, sticky="e", padx=(0, 8)
            )
            ttk.Label(receivers, textvariable=self.receiver_distance[name], width=13).grid(
                row=r, column=3, sticky="e"
            )

    def _set_settings_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for widget in (
            self.camera_spin,
            self.tolerance_spin,
            self.raw_spin,
            self.analysis_spin,
            self.record_check,
        ):
            widget.configure(state=state)

    def _open_camera(self) -> cv2.VideoCapture:
        index = int(self.camera_var.get())
        cap: Optional[cv2.VideoCapture] = None
        if platform.system() == "Windows" and hasattr(cv2, "CAP_DSHOW"):
            candidate = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if candidate.isOpened():
                cap = candidate
            else:
                candidate.release()
        if cap is None:
            cap = cv2.VideoCapture(index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        return cap

    def _apply_settings(self) -> None:
        tolerance = float(self.tolerance_var.get())
        raw_threshold = float(self.raw_threshold_var.get())
        analysis_width = int(self.analysis_width_var.get())
        if tolerance <= 0:
            raise ValueError("tolerance scale must be > 0")
        if raw_threshold < 0:
            raise ValueError("raw threshold must be >= 0")
        if analysis_width < 32:
            raise ValueError("analysis width must be >= 32")
        self.census.tolerance_scale = tolerance
        self.census.raw_threshold = raw_threshold
        self.census.analysis_width = analysis_width

    def _new_session(self) -> None:
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_path = None
        self.census.reset()
        self._last_ui_time = time.perf_counter()
        self._last_ui_frames = 0
        for name in SPECS:
            self.receiver_status[name].set("—")
            self.receiver_rate[name].set("0.000")
            self.receiver_distance[name].set("—")
        self._refresh_metrics(None)

    def _start_writer(self, frame: np.ndarray) -> None:
        if not self.record_var.get() or self.writer is not None:
            return
        h, w = frame.shape[:2]
        self.video_path = self.results_dir / f"cc0a_webcam_{self.session_id}.avi"
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        fps = float(self.cap.get(cv2.CAP_PROP_FPS) if self.cap is not None else 0.0)
        if not np.isfinite(fps) or fps <= 1.0:
            fps = 30.0
        self.writer = cv2.VideoWriter(str(self.video_path), fourcc, fps, (w, h))
        if not self.writer.isOpened():
            self.writer.release()
            self.writer = None
            self.video_path = None
            messagebox.showwarning(
                "Video recording unavailable",
                "The camera census will continue, but OpenCV could not open the MJPG AVI writer.",
            )

    def toggle_camera(self) -> None:
        if self.running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self) -> None:
        try:
            self._apply_settings()
        except Exception as exc:
            messagebox.showerror("Invalid settings", str(exc))
            return
        cap = self._open_camera()
        if not cap.isOpened():
            cap.release()
            messagebox.showerror(
                "Camera error",
                f"Could not open camera index {self.camera_var.get()}. Try another camera number.",
            )
            return
        self.cap = cap
        self._new_session()
        self.running = True
        self.start_button.configure(text="Stop")
        self._set_settings_enabled(False)
        self.metric_vars["status"].set(
            "Collecting dense oracle labels. A WAKE means that receiver crossed its cached tolerance."
        )
        self._tick()

    def stop_camera(self) -> None:
        self.running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        self.start_button.configure(text="Start")
        self._set_settings_enabled(True)
        self.metric_vars["status"].set(
            "Camera stopped. Save the receipt, or change settings and start a new session."
        )

    def reset_session(self) -> None:
        try:
            self._apply_settings()
        except Exception as exc:
            messagebox.showerror("Invalid settings", str(exc))
            return
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        self._new_session()
        self.metric_vars["status"].set(
            "Session reset. Cache, wake rates, and counters cleared."
        )

    def _tick(self) -> None:
        if not self.running or self.cap is None:
            return
        ok, frame = self.cap.read()
        if not ok:
            self.metric_vars["status"].set("Camera read failed; stopping.")
            self.stop_camera()
            return

        self._start_writer(frame)
        if self.writer is not None:
            self.writer.write(frame)

        row = self.census.process(frame)
        self._draw_preview(frame, row)
        self._refresh_metrics(row)
        self.root.after(1, self._tick)

    def _draw_preview(self, frame: np.ndarray, row: dict) -> None:
        display = frame.copy()
        h, w = display.shape[:2]
        cv2.rectangle(display, (0, int(0.05 * h)), (int(0.50 * w), int(0.95 * h)), (255, 255, 255), 1)
        cv2.rectangle(display, (int(0.50 * w), int(0.05 * h)), (w - 1, int(0.95 * h)), (255, 255, 255), 1)
        cv2.rectangle(display, (int(0.10 * w), int(0.55 * h)), (int(0.90 * w), h - 1), (255, 255, 255), 1)

        wake_names = [name for name, value in row["wake"].items() if value]
        caption = "WAKE: " + (", ".join(wake_names[:4]) if wake_names else "none")
        if len(wake_names) > 4:
            caption += f" +{len(wake_names) - 4}"
        cv2.putText(
            display,
            caption,
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        target_w = 760
        if display.shape[1] > target_w:
            target_h = int(round(display.shape[0] * target_w / display.shape[1]))
            display = cv2.resize(display, (target_w, target_h), interpolation=cv2.INTER_AREA)

        rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        hh, ww = rgb.shape[:2]
        ppm = f"P6\n{ww} {hh}\n255\n".encode("ascii") + rgb.tobytes()
        try:
            photo = tk.PhotoImage(data=ppm, format="PPM")
        except tk.TclError:
            ok, encoded = cv2.imencode(".png", display)
            if not ok:
                return
            import base64

            photo = tk.PhotoImage(data=base64.b64encode(encoded).decode("ascii"))
        self.photo = photo
        self.preview.configure(image=photo, text="")

    def _refresh_metrics(self, row: Optional[dict]) -> None:
        s = self.census.summary()
        self.metric_vars["frames"].set(str(s["frames_used"]))
        if s["steady_steps"] > 0:
            self.metric_vars["raw"].set(f"{100 * s['raw_change_rate']:.1f}%")
            self.metric_vars["any"].set(f"{100 * s['any_receiver_change_rate']:.1f}%")
            self.metric_vars["local"].set(
                f"{100 * s['fraction_receivers_woken_per_step']:.2f}%"
            )
            self.metric_vars["ratio"].set(
                f"{s['global_or_vs_local_ratio_equal_cost']:.2f}x"
            )
        else:
            self.metric_vars["raw"].set("—")
            self.metric_vars["any"].set("—")
            self.metric_vars["local"].set("—")
            self.metric_vars["ratio"].set("—")

        now = time.perf_counter()
        dt = now - self._last_ui_time
        if dt >= 0.5:
            frames_delta = self.census.frames - self._last_ui_frames
            self.metric_vars["fps"].set(f"{frames_delta / dt:.1f}")
            self._last_ui_time = now
            self._last_ui_frames = self.census.frames

        if row is not None:
            for name in SPECS:
                awake = bool(row["wake"][name])
                self.receiver_status[name].set("WAKE" if awake else "valid")
                tol = SPECS[name].tolerance * self.census.tolerance_scale
                d = row["distance"][name]
                if np.isfinite(d):
                    self.receiver_distance[name].set(f"{d / max(tol, 1e-12):.3f}x")
                else:
                    self.receiver_distance[name].set("acquire")
                rate = s["receiver_wake_rates"][name]
                self.receiver_rate[name].set(f"{rate:.3f}")

    def _receipt_paths(self) -> tuple[Path, Path, Path]:
        prefix = self.results_dir / f"cc0a_webcam_{self.session_id}"
        return (
            prefix.with_suffix(".json"),
            prefix.with_name(prefix.name + "_invalidation.csv"),
            prefix.with_suffix(".txt"),
        )

    def save_receipt(self) -> None:
        if not self.session_id:
            messagebox.showinfo("No session", "Start a camera session first.")
            return
        s = self.census.summary()
        s.update(
            {
                "session_id": self.session_id,
                "camera_index": int(self.camera_var.get()),
                "recorded_video": str(self.video_path) if self.video_path else None,
                "platform": platform.platform(),
                "opencv_version": cv2.__version__,
            }
        )
        json_path, csv_path, txt_path = self._receipt_paths()
        json_path.write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")

        fieldnames = [
            "frame",
            "time_s",
            "acquisition",
            "frame_mae",
            "raw_changed",
            "any_receiver_changed",
            "active_count",
        ]
        for name in SPECS:
            fieldnames.extend([f"{name}_wake", f"{name}_distance"])
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=fieldnames)
            wr.writeheader()
            for row in self.census.rows:
                flat = {
                    "frame": row["frame"],
                    "time_s": f"{row['time_s']:.9f}",
                    "acquisition": row["acquisition"],
                    "frame_mae": f"{row['frame_mae']:.9f}",
                    "raw_changed": row["raw_changed"],
                    "any_receiver_changed": row["any_receiver_changed"],
                    "active_count": row["active_count"],
                }
                for name in SPECS:
                    flat[f"{name}_wake"] = row["wake"][name]
                    d = row["distance"][name]
                    flat[f"{name}_distance"] = "" if not np.isfinite(d) else f"{d:.9f}"
                wr.writerow(flat)

        txt_lines = [
            "CC0-A2 WEBCAM INVALIDATION CENSUS",
            "=" * 72,
            f"session                   : {self.session_id}",
            f"camera index              : {self.camera_var.get()}",
            f"frames                    : {s['frames_used']}",
            f"steady steps              : {s['steady_steps']}",
            f"tolerance scale           : {s['tolerance_scale']}",
            f"raw MAE threshold         : {s['raw_threshold_mae']}",
            f"raw input change rate     : {s['raw_change_rate']:.6f}",
            f"ANY receiver change rate  : {s['any_receiver_change_rate']:.6f}",
            f"receiver slot wake frac   : {s['fraction_receivers_woken_per_step']:.6f}",
            (
                "GLOBAL-OR/local ratio     : "
                f"{s['global_or_vs_local_ratio_equal_cost']:.3f}x "
                "(equal receiver cost; oracle opportunity only)"
            ),
            "",
            "receiver wake rates:",
        ]
        for name, rate in sorted(s["receiver_wake_rates"].items(), key=lambda kv: kv[1]):
            txt_lines.append(
                f"  {name:18s} {rate:.6f}   "
                f"tol={s['receiver_tolerances'][name]:.6f}"
            )
        txt_lines.extend(
            [
                "",
                "WARNING:",
                "Dense receiver outputs were computed on every frame.",
                "This receipt measures skip opportunity, not runtime speedup.",
            ]
        )
        txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
        self.metric_vars["status"].set(f"Receipt saved: {txt_path.name}")
        messagebox.showinfo(
            "Receipt saved",
            f"Saved:\n{txt_path}\n{json_path}\n{csv_path}"
            + (f"\n{self.video_path}" if self.video_path else ""),
        )

    def open_results_folder(self) -> None:
        import os
        import subprocess

        path = self.results_dir.resolve()
        try:
            if platform.system() == "Windows":
                os.startfile(str(path))  # type: ignore[attr-defined]
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as exc:
            messagebox.showerror("Could not open folder", str(exc))

    def on_close(self) -> None:
        self.stop_camera()
        self.root.destroy()


def self_test() -> None:
    census = LiveCensus(tolerance_scale=0.35, analysis_width=128)
    h, w = 180, 320
    for t in range(80):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        x = 20 + (t % 50)
        cv2.rectangle(frame, (x, 70), (x + 35, 115), (220, 220, 220), -1)
        cv2.circle(frame, (250, 40), 18, (100, 100, 100), -1)
        census.process(frame)
    s = census.summary()
    assert s["frames_used"] == 80
    assert s["steady_steps"] == 79
    assert 0.0 <= s["fraction_receivers_woken_per_step"] <= 1.0
    assert set(s["receiver_wake_rates"]) == set(SPECS)
    print("CC0-A webcam GUI self-test PASS")
    print(
        f"frames={s['frames_used']} raw={s['raw_change_rate']:.4f} "
        f"any={s['any_receiver_change_rate']:.4f} "
        f"local={s['fraction_receivers_woken_per_step']:.4f}"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="CC0-A2 live webcam invalidation census GUI")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--tolerance-scale", type=float, default=0.35)
    ap.add_argument("--raw-threshold", type=float, default=0.0005)
    ap.add_argument("--analysis-width", type=int, default=192)
    ap.add_argument(
        "--results-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results" / "cc0a_webcam_runs",
    )
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    root = tk.Tk()
    root.geometry("1250x760")
    CC0AWebcamGUI(
        root=root,
        camera_index=args.camera,
        tolerance_scale=args.tolerance_scale,
        raw_threshold=args.raw_threshold,
        analysis_width=args.analysis_width,
        results_dir=args.results_dir,
    )
    root.mainloop()


if __name__ == "__main__":
    main()
