# CLAUDE.md

## Commands
```bash
cd src && python main.py                                    # run pipeline (hits Celestrak)
cd src && python main.py --local-file tests/test_data.csv   # skip network
python -m pytest tests/                                     # run tests (from repo root)
cd src && docker build -t orbital-decay .                   # build image
pip install -r requirements-dev.txt                         # dev deps
```
**Serve the frontend locally** — copy the pipeline's output GeoJSON (path printed
at the end of the run when `S3_BUCKET_NAME` is unset) into `web/`, then serve:
```bash
cp <pipeline-output>.geojson web/decays.geojson
cd web && python -m http.server 8000
```

Celestrak has strict rate limits — prefer `--local-file` during development.

## Architecture

Three pipeline stages, orchestrated by `main.py`, which uploads the result to
S3 (`decays.geojson`, bucket from `S3_BUCKET_NAME`; skipped → temp file if unset).

1. **`celestrak_client.py`** — Fetches the active satellite catalog (OMM CSV),
   parses via `sgp4.omm.parse_csv`, filters to LEO (and non-negative BSTAR).
2. **`propagator.py`** — Propagates each satellite minute-by-minute over a 7-day
   window (Skyfield `EarthSatellite`, parallelized via `ProcessPoolExecutor`,
   `WORKER_COUNT` env var). Returns the last 15 min of trajectory for any object
   that drops below the Kármán line.
3. **`formatter.py`** — Serializes decay trajectories to a Mapbox-compatible
   GeoJSON `FeatureCollection` (elevation, timestamps, catalog ID in properties).

- **`web/`** — static Mapbox GL JS frontend; fetches `decays.geojson`, renders
  each re-entry as a clickable arc.
- **`src/static/skyfield_data/`** — pre-downloaded IERS data (`finals2000A.all`),
  baked into the image by `download_data.py`. Do not delete.

## Key constants

| Constant | File | Value | Meaning |
|---|---|---|---|
| `MEAN_MOTION_THRESHOLD` | `celestrak_client.py` | 14 | Minimum orbits/day to be considered LEO |
| `KARMAN_LINE_KM` | `propagator.py` | 100 | Altitude threshold for re-entry detection |
| `MINUTES_IN_WEEK` | `propagator.py` | 10080 | Propagation window length |

## Testing
Uses `pytest-mock` (`mocker`). `_detect_decay_worker` and `parse_omm_stream` are
I/O-decoupled for deterministic unit tests. Never make real HTTP calls or load
real Skyfield data — mock `Loader` and `omm.parse_csv` (see existing tests).

## Rules
- Branch names must start with `claude/`. Never merge into `main`.
- Never read, access, display, or reference any `.env` file or `.env.*` file.