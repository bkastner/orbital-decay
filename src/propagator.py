"""
Compute satellite propagation over the next week to determine if it will decay and re-enter in that time.
"""

import os
import numpy
from skyfield.api import EarthSatellite, Loader
from skyfield.timelib import Timescale, Time
from skyfield.toposlib import wgs84
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import partial
from tqdm import tqdm
from typing import Any


def _build_time_window() -> tuple[Timescale, Time]:
    data_dir = os.path.join(os.path.dirname(__file__), 'static', 'skyfield_data')
    load = Loader(data_dir)
    ts = load.timescale()

    now = datetime.now(timezone.utc)
    return ts, ts.utc(now.year, now.month, now.day, minute=range(10080))

def _detect_decay_worker(omm_dict: dict[str, Any], time_scale: Timescale, time_array: Time) -> dict[str, Any] | None:

    satellite = EarthSatellite.from_omm(time_scale, omm_dict)

    geocentric = satellite.at(time_array)
    geodetic = wgs84.geographic_position_of(geocentric)

    elevations = geodetic.elevation.km

    decay_indices = numpy.where(elevations < 100.0)[0] # Below Karman line

    if len(decay_indices) == 0:
        return None

    # We want the last coordinate to be the one immediately after decay
    first_decay_idx = decay_indices[0]
    slice_index = first_decay_idx + 1
    start_index = max(0,first_decay_idx-15)

    lons = geodetic.longitude.degrees[start_index:slice_index]
    lats = geodetic.latitude.degrees[start_index:slice_index]
    alts = geodetic.elevation.m[start_index:slice_index]
    times = time_array[start_index:slice_index].utc_iso()

    lons_rad = numpy.deg2rad(lons)
    unwrapped_lons_rad = numpy.unwrap(lons_rad)
    unwrapped_lons = numpy.rad2deg(unwrapped_lons_rad)

    trajectory_coords = [[float(lon), float(lat)] for lon, lat in zip(unwrapped_lons, lats)]

    return {
        "catalog_id": satellite.model.satnum,
        "name": satellite.name,
        "trajectory": trajectory_coords,
        "altitudes": [float(a) for a in alts],
        "timestamps": times,
    }



def orchestrator(satellite_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    time_scale, time_arr = _build_time_window()
    worker = partial(_detect_decay_worker, time_scale=time_scale, time_array=time_arr)

    decayed_satellites_with_trajectory = []

    is_cloud = "AWS_EXECUTION_ENV" in os.environ

    pbar = tqdm('Propagating trajectories', total=len(satellite_records), unit=' satellite', disable=is_cloud)
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        for event in executor.map(worker, satellite_records, chunksize=100):
            pbar.update()
            if event is not None:
                if len(event['trajectory']) > 1:
                    decayed_satellites_with_trajectory.append(event)

    pbar.close()

    return decayed_satellites_with_trajectory











