# Note 012 — CC0-A2 webcam GUI

**Status:** instrument ready for a real external-stream census. No webcam result is claimed until an actual run is saved.

## Run it

Windows shortcut:

```bat
run_cc0a_webcam.bat
```

or directly:

```bat
python3.13 experiments\cc0a_webcam_gui.py
```

If camera 0 is not the desired device:

```bat
python3.13 experiments\cc0a_webcam_gui.py --camera 1
```

Headless plumbing check:

```bat
python3.13 experiments\cc0a_webcam_gui.py --self-test
```

## What the window shows

The GUI is a live wrapper around the same receiver/caching logic as `cc0a_invalidation_census.py`.

It shows:

```text
camera preview
raw input change rate
ANY receiver invalid rate
receiver-slot invalid fraction
GLOBAL-OR / oracle-local opportunity ratio
per-receiver current WAKE/valid state
per-receiver wake rate
distance / tolerance for each receiver
```

A receiver wakes only when its dense current output has moved outside the tolerance region around its last accepted cached consequence.

The first frame is acquisition and is excluded from steady-state rates.

## Controls

- `Camera` chooses OpenCV camera index.
- `Tolerance scale` multiplies the fixed receiver tolerances from CC0-A1.
- `Raw MAE threshold` controls whether the raw image counts as changed.
- `Analysis width` controls the dense oracle analysis resolution.
- `Record webcam video` optionally stores an MJPG AVI alongside the receipt.
- `Reset session` clears caches and all statistics.
- `Save receipt` writes JSON, text, and a per-frame CSV invalidation/distance trace.

Settings lock while the camera is running so a saved receipt cannot silently mix different tolerance regimes.

## Output

Default output directory:

```text
results/cc0a_webcam_runs/
```

A saved session produces:

```text
cc0a_webcam_YYYYMMDD_HHMMSS.txt
cc0a_webcam_YYYYMMDD_HHMMSS.json
cc0a_webcam_YYYYMMDD_HHMMSS_invalidation.csv
```

and, when video recording is enabled:

```text
cc0a_webcam_YYYYMMDD_HHMMSS.avi
```

The CSV contains the full oracle wake matrix plus receiver distances, so a run can be attacked offline instead of surviving only as a GUI screenshot.

## Suggested first real run

Do not optimize the scene to make sparsity look good. A useful first run is deliberately messy:

1. Sit normally in front of the webcam for roughly a minute.
2. Move one hand on the left, then right.
3. Move toward/away from the camera.
4. Walk partly out of frame and back.
5. Change room lighting if easy.
6. Include several seconds where nothing intentional happens.

Use tolerance scale `0.35` first so it directly connects to the CC0-A1 middle receipt. Then repeat with at least `0.15` and `0.75` as a tolerance attack.

Do not compare ratios across runs unless the receiver definitions, analysis width, camera, and scene protocol are recorded.

## Stop line

The GUI prints an opportunity ratio, not speed.

The dense oracle still evaluates every receiver every frame. We have not yet paid for:

```text
cheap change guard
candidate discovery
routing
metadata
queueing
memory traffic
teacher refresh
wall-clock sparse execution
```

Therefore:

> **CC0-A2 asks whether receiver-relative invalidation sparsity survives a real camera stream. It does not yet ask whether the sparsity can be exploited cheaply.**

Only a positive real-stream receipt justifies CC0-B.
