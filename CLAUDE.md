# CLAUDE.md


## Commands

**Run the pipeline locally:**
```bash
cd src && python main.py
# Use a local CSV file to skip Celestrak network requests:
cd src && python main.py --local-file /path/to/data.csv
```

**Run tests (from repo root):**
```bash
python -m pytest tests/
# Single test file:
python -m pytest tests/test_propagator.py
# Single test:
python -m pytest tests/test_propagator.py::test_detect_decay_worker_finds_decay
```

**Serve the frontend locally:**
```bash
# First run the pipeline and copy the output geojson:
cp /tmp/tmpXXXXXX.geojson web/decays.geojson
cd web && python -m http.server 8000
```

**Build Docker image:**
```bash
cd src && docker build -t orbital-decay .
```

**Install dev dependencies:**
```bash
pip install -r requirements-dev.txt
```

## Architecture

The pipeline runs in three stages, each in its own module:

1. **`celestrak_client.py`** — Fetches the active satellite catalog from Celestrak as a streaming CSV (OMM format), parses it with `sgp4.omm.parse_csv`, and filters to LEO objects (≥14 mean motion orbits/day) with non-negative BSTAR. Supports `--local-file` to skip network calls during testing.

2. **`propagator.py`** — Takes the filtered satellite records and propagates each one minute-by-minute over a 7-day window using Skyfield's `EarthSatellite`. Uses `ProcessPoolExecutor` for parallelism (controlled by `WORKER_COUNT` env var). If any satellite's altitude drops below the Kármán line (100 km), the last 15 minutes of trajectory coordinates are returned. Longitude values are unwrapped (via `numpy.unwrap`) to avoid antimeridian discontinuities in LineString rendering.

3. **`formatter.py`** — Serializes the list of decay trajectories into a GeoJSON `FeatureCollection` compatible with Mapbox GL JS. Elevation (in metres), timestamps, and catalog ID are stored in feature properties alongside the 2D coordinate LineString.

**`main.py`** orchestrates these three stages, then uploads the resulting GeoJSON to S3 (`decays.geojson`). The S3 bucket name comes from the `S3_BUCKET_NAME` environment variable; if absent, the upload is skipped and the file is written to a temp path.

**`web/`**:  static Mapbox GL JS frontend that fetches `decays.geojson` (served from CloudFront/S3 in prod) and renders each re-entry trajectory as an arc with a popup on click

**`src/static/skyfield_data/`** holds pre-downloaded IERS Earth rotation data (`finals2000A.all`) that Skyfield needs for accurate timescales. This is baked into the Docker image via `download_data.py` at build time — do not delete it.

## Key constants

| Constant | File | Value | Meaning |
|---|---|---|---|
| `MEAN_MOTION_THRESHOLD` | `celestrak_client.py` | 14 | Minimum orbits/day to be considered LEO |
| `KARMAN_LINE_KM` | `propagator.py` | 100 | Altitude threshold for re-entry detection |
| `MINUTES_IN_WEEK` | `propagator.py` | 10080 | Propagation window length |

## Testing notes

Tests use `pytest-mock` (`mocker` fixture). The `_detect_decay_worker` and `parse_omm_stream` functions are intentionally decoupled from I/O so they can be unit tested deterministically. Do not make real HTTP calls or load real Skyfield data in tests — mock `Loader` and `omm.parse_csv` as the existing tests demonstrate. The Celestrak API has strict rate limits; use `--local-file` instead of hitting the network during development.
Local data for testing with --local-file is in tests/test_data.csv

## Development rules
Branch names must start with claude/
Never merge a branch into main

## Security Rules

- Never read, access, display, or reference the contents of any `.env` file or files ending in `.env.*` (e.g. `.env.local`, `.env.production`)