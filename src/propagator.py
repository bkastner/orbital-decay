"""
Compute satellite propagation over the next week to determine if it will decay and re-enter in that time.
"""

import os
import numpy
from skyfield.api import EarthSatellite, Loader
from skyfield.toposlib import wgs84
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone

from functools import partial

def _build_time_window():
    data_dir = os.path.join(os.path.dirname(__file__), 'static', 'skyfield_data')
    load = Loader(data_dir)
    ts = load.timescale()

    now = datetime.now(timezone.utc)
    return ts.utc(now.year, now.month, now.day, hours=[h * 0.5 for h in range(336)])

def _detect_decay_worker(satrec, timescale):
    satellite = EarthSatellite.from_satrec(satrec, timescale)

    geocentric = satellite.at(timescale)
    geodetic = wgs84.geographic_position_of(geocentric)

    elevations = geodetic.elevation.km

    decay_indices = numpy.where(elevations < 105.0)[0]

    if len(decay_indices) == 0:
        return None

    decay_idx = decay_indices[0]

    return {
        "catalog_id": satellite.model.satnum,
        "decay_time": timescale[decay_idx].utc_iso(),
        "latitude": geodetic.latitude.degrees[decay_idx],
        "longitude": geodetic.longitude.degrees[decay_idx]
    }



def orchestrator(satellite_records):
    time_arr = _build_time_window()
    worker = partial(_detect_decay_worker, timescale=time_arr)

    decayed_satellites = []

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        # executor.map distributes the workload and preserves the order of results
        results = executor.map(worker, satellite_records)

        # Filter out the None values where no decay was detected
        for event in results:
            if event is not None:
                decayed_satellites.append(event)

    return decayed_satellites











