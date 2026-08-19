from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class ReceiverSpec:
    name: str
    tolerance: float
    kind: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def gray01(frame: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, size, interpolation=cv2.INTER_AREA)
    return g.astype(np.float32) / 255.0


def roi(img: np.ndarray, x0: float, x1: float, y0: float, y1: float) -> np.ndarray:
    h, w = img.shape[:2]
    xa, xb = int(round(x0*w)), int(round(x1*w))
    ya, yb = int(round(y0*h)), int(round(y1*h))
    return img[ya:yb, xa:xb]


def gist(r: np.ndarray, out=(8, 6)) -> np.ndarray:
    return cv2.resize(r, out, interpolation=cv2.INTER_AREA).astype(np.float32).reshape(-1)


def edge_density(r: np.ndarray) -> np.ndarray:
    gx = cv2.Sobel(r, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(r, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx*gx + gy*gy)
    return np.array([float(np.mean(mag))], dtype=np.float32)


def center_of_light(r: np.ndarray) -> np.ndarray:
    mass = np.maximum(r - 0.03, 0.0)
    s = float(mass.sum())
    if s <= 1e-8:
        return np.array([0.5, 0.5, 0.0], dtype=np.float32)
    yy, xx = np.mgrid[0:r.shape[0], 0:r.shape[1]]
    x = float((mass*xx).sum()/s) / max(1, r.shape[1]-1)
    y = float((mass*yy).sum()/s) / max(1, r.shape[0]-1)
    brightness = float(np.mean(r))
    return np.array([x, y, brightness], dtype=np.float32)


def motion_triplet(curr: np.ndarray, prev: np.ndarray | None, x0: float, x1: float, y0: float, y1: float) -> np.ndarray:
    if prev is None:
        return np.zeros(3, dtype=np.float32)
    c = roi(curr, x0, x1, y0, y1)
    p = roi(prev, x0, x1, y0, y1)
    d = np.abs(c-p)
    return np.array([
        float(d.mean()),
        float(np.quantile(d, 0.90)),
        float(np.mean(d > 0.04)),
    ], dtype=np.float32)


def receiver_outputs(curr: np.ndarray, prev: np.ndarray | None) -> Dict[str, np.ndarray]:
    center = roi(curr, .25, .75, .20, .80)
    left = roi(curr, 0.0, .50, .10, .90)
    right = roi(curr, .50, 1.0, .10, .90)
    bottom = roi(curr, .15, .85, .60, 1.0)
    outer = curr.copy()
    h, w = outer.shape
    outer[int(.22*h):int(.78*h), int(.25*w):int(.75*w)] = 0.0

    return {
        'global_gist': gist(curr, (10, 6)),
        'center_gist': gist(center, (8, 6)),
        'left_gist': gist(left, (6, 6)),
        'right_gist': gist(right, (6, 6)),
        'periphery_gist': gist(outer, (10, 6)),
        'global_edge': edge_density(curr),
        'bottom_edge': edge_density(bottom),
        'light_centroid': center_of_light(curr),
        'left_motion': motion_triplet(curr, prev, 0.0, .50, .05, .95),
        'right_motion': motion_triplet(curr, prev, .50, 1.0, .05, .95),
        'bottom_motion': motion_triplet(curr, prev, .10, .90, .55, 1.0),
    }


SPECS: Dict[str, ReceiverSpec] = {
    'global_gist': ReceiverSpec('global_gist', 0.030, 'appearance'),
    'center_gist': ReceiverSpec('center_gist', 0.035, 'appearance'),
    'left_gist': ReceiverSpec('left_gist', 0.035, 'appearance'),
    'right_gist': ReceiverSpec('right_gist', 0.035, 'appearance'),
    'periphery_gist': ReceiverSpec('periphery_gist', 0.030, 'appearance'),
    'global_edge': ReceiverSpec('global_edge', 0.015, 'structure'),
    'bottom_edge': ReceiverSpec('bottom_edge', 0.020, 'structure'),
    'light_centroid': ReceiverSpec('light_centroid', 0.020, 'geometry'),
    'left_motion': ReceiverSpec('left_motion', 0.035, 'motion'),
    'right_motion': ReceiverSpec('right_motion', 0.035, 'motion'),
    'bottom_motion': ReceiverSpec('bottom_motion', 0.035, 'motion'),
}


def output_distance(a: np.ndarray, b: np.ndarray) -> float:
    d = a.astype(np.float64)-b.astype(np.float64)
    return float(np.sqrt(np.mean(d*d)))


def pairwise_phi(matrix: np.ndarray) -> np.ndarray:
    n = matrix.shape[1]
    out = np.eye(n, dtype=np.float64)
    for i in range(n):
        for j in range(i+1, n):
            x = matrix[:, i].astype(np.float64)
            y = matrix[:, j].astype(np.float64)
            sx, sy = x.std(), y.std()
            r = 0.0 if sx < 1e-12 or sy < 1e-12 else float(np.corrcoef(x, y)[0, 1])
            out[i,j] = out[j,i] = r
    return out


def run_video(path: Path, max_frames: int, stride: int, resize_w: int, raw_threshold: float, tolerance_scale: float):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f'could not open video: {path}')
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    source_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    source_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    source_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    receiver_names = list(SPECS)
    cached: Dict[str, np.ndarray] = {}
    wake_rows: List[List[int]] = []
    raw_changed: List[int] = []
    any_changed: List[int] = []
    active_counts: List[int] = []
    delta_mae: List[float] = []
    dist_rows: List[List[float]] = []

    prev_gray = None
    decoded = 0
    used = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        decoded += 1
        if (decoded-1) % stride:
            continue
        if max_frames and used >= max_frames:
            break
        h, w = frame.shape[:2]
        resize_h = max(1, int(round(h * resize_w / max(1, w))))
        g = gray01(frame, (resize_w, resize_h))
        outs = receiver_outputs(g, prev_gray)

        if prev_gray is None:
            mae = 0.0
            raw = 1
        else:
            mae = float(np.mean(np.abs(g-prev_gray)))
            raw = int(mae > raw_threshold)
        delta_mae.append(mae)
        raw_changed.append(raw)

        row=[]
        drow=[]
        for name in receiver_names:
            y = outs[name]
            if name not in cached:
                wake = 1
                d = float('inf')
                cached[name] = y.copy()
            else:
                d = output_distance(y, cached[name])
                wake = int(d > SPECS[name].tolerance * tolerance_scale)
                if wake:
                    cached[name] = y.copy()
            row.append(wake)
            drow.append(d)
        wake_rows.append(row)
        dist_rows.append(drow)
        any_changed.append(int(any(row)))
        active_counts.append(int(sum(row)))
        prev_gray = g
        used += 1

    cap.release()
    W = np.asarray(wake_rows, dtype=np.uint8)
    if W.size == 0:
        raise RuntimeError('no frames decoded')
    W_ss = W[1:] if len(W) > 1 else W
    raw_ss = np.asarray(raw_changed[1:] if len(raw_changed)>1 else raw_changed, dtype=np.float64)
    any_ss = np.asarray(any_changed[1:] if len(any_changed)>1 else any_changed, dtype=np.float64)
    active_ss = np.asarray(active_counts[1:] if len(active_counts)>1 else active_counts, dtype=np.float64)

    local_fraction = float(active_ss.mean()/len(receiver_names))
    any_rate = float(any_ss.mean())
    rates = {name: float(W_ss[:,i].mean()) for i,name in enumerate(receiver_names)}
    phi = pairwise_phi(W_ss)
    summary = {
        'source': str(path),
        'sha256': sha256_file(path),
        'source_bytes': path.stat().st_size,
        'source_frames_declared': source_frames,
        'frames_used': int(used),
        'stride': int(stride),
        'fps': fps,
        'source_width': source_w,
        'source_height': source_h,
        'analysis_width': resize_w,
        'raw_threshold_mae': raw_threshold,
        'raw_change_rate': float(raw_ss.mean()),
        'any_receiver_change_rate': any_rate,
        'mean_receivers_woken_per_step': float(active_ss.mean()),
        'fraction_receivers_woken_per_step': local_fraction,
        'oracle_local_work_fraction_equal_cost': local_fraction,
        'global_or_work_fraction_equal_cost': any_rate,
        'global_or_vs_local_ratio_equal_cost': float(any_rate / max(local_fraction, 1e-12)),
        'always_on_vs_local_ratio_equal_cost': float(1.0 / max(local_fraction, 1e-12)),
        'receiver_wake_rates': rates,
        'mean_frame_mae': float(np.mean(delta_mae[1:] if len(delta_mae)>1 else delta_mae)),
        'receiver_names': receiver_names,
        'receiver_tolerances': {k: SPECS[k].tolerance * tolerance_scale for k in receiver_names},
        'tolerance_scale': tolerance_scale,
        'phi_correlation': phi.tolist(),
    }
    return summary, W, np.asarray(dist_rows, dtype=np.float64)


def print_summary(s: dict):
    print('\nCC0-A — INVALIDATION SPARSITY CENSUS')
    print('='*72)
    print(f"source                    : {s['source']}")
    print(f"frames used               : {s['frames_used']}  stride={s['stride']}")
    print(f"raw input change rate     : {s['raw_change_rate']:.4f}")
    print(f"ANY receiver change rate  : {s['any_receiver_change_rate']:.4f}")
    print(f"mean receivers woken/step : {s['mean_receivers_woken_per_step']:.3f} / {len(s['receiver_names'])}")
    print(f"fraction woken/step       : {s['fraction_receivers_woken_per_step']:.4f}")
    print(f"global-OR/local work ratio : {s['global_or_vs_local_ratio_equal_cost']:.2f}x  (equal receiver costs; oracle opportunity only)")
    print(f"always/local work ratio    : {s['always_on_vs_local_ratio_equal_cost']:.2f}x  (NOT a runtime speedup)")
    print('\nreceiver wake rates:')
    for k,v in sorted(s['receiver_wake_rates'].items(), key=lambda kv: kv[1]):
        print(f"  {k:18s} {v:.4f}   tol={s['receiver_tolerances'][k]:.3f}")
    print('\nInterpretation gate: opportunity exists only if raw/global change is high')
    print('while many individual receiver wake rates and the mean active fraction are low.')


def main():
    ap=argparse.ArgumentParser(description='CC0-A receiver invalidation sparsity census')
    ap.add_argument('video', type=Path)
    ap.add_argument('--max-frames', type=int, default=0, help='0 = all')
    ap.add_argument('--stride', type=int, default=1)
    ap.add_argument('--resize-width', type=int, default=192)
    ap.add_argument('--raw-threshold', type=float, default=0.0005, help='frame MAE threshold in [0,1]')
    ap.add_argument('--tolerance-scale', type=float, default=0.35)
    ap.add_argument('--out-prefix', type=Path, default=None)
    ap.add_argument('--sweep-scales', type=str, default='', help='comma-separated tolerance scales; if set, run a census sweep and print CSV')
    args=ap.parse_args()
    if args.sweep_scales:
        scales=[float(x.strip()) for x in args.sweep_scales.split(',') if x.strip()]
        print('video,scale,raw_change,any_receiver,local_fraction,global_or_vs_local,always_vs_local')
        for scale in scales:
            s,_,_=run_video(args.video,args.max_frames,args.stride,args.resize_width,args.raw_threshold,scale)
            print(f"{args.video.name},{scale:g},{s['raw_change_rate']:.6f},{s['any_receiver_change_rate']:.6f},{s['fraction_receivers_woken_per_step']:.6f},{s['global_or_vs_local_ratio_equal_cost']:.6f},{s['always_on_vs_local_ratio_equal_cost']:.6f}")
        return
    s,W,D=run_video(args.video,args.max_frames,args.stride,args.resize_width,args.raw_threshold,args.tolerance_scale)
    print_summary(s)
    if args.out_prefix:
        p=args.out_prefix
        p.parent.mkdir(parents=True, exist_ok=True)
        p.with_suffix('.json').write_text(json.dumps(s, indent=2)+'\n', encoding='utf-8')
        with p.with_suffix('.csv').open('w', newline='', encoding='utf-8') as f:
            wr=csv.writer(f)
            wr.writerow(['frame']+s['receiver_names'])
            for i,row in enumerate(W.tolist()):
                wr.writerow([i]+row)
        np.save(p.with_name(p.name+'_distances.npy'), D)
        print(f"wrote {p.with_suffix('.json')}")
        print(f"wrote {p.with_suffix('.csv')}")


if __name__=='__main__':
    main()
