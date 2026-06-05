"""
src/celestrak_client.py
"""
import urllib3
import logging
from sgp4 import omm
from sgp4.api import Satrec

logger = logging.getLogger(__name__)

class CelestrakClient:
    def __init__(self, endpoint_url="https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv"):
        # Establish low-overhead HTTP connection pooling
        self.http = urllib3.PoolManager(num_pools=5, maxsize=10)
        self.endpoint_url = endpoint_url

    def get_active_catalog(self):
        """
        Fetches the active catalog from the network and yields parsed Satrec objects.
        Streams the response to maintain a minimal memory footprint.
        """
        logger.info(f"Fetching OMM CSV stream from: {self.endpoint_url}")

        response = self.http.request('GET', self.endpoint_url, preload_content=False)

        if response.status != 200:
            raise ConnectionError(f"Celestrak HTTP Error: {response.status}")

        text_stream = (line.decode('utf-8') for line in response)

        yield from self.parse_omm_stream(text_stream)

        response.release_conn()

    def parse_omm_stream(self, text_stream):
        """
        Consumes an iterable of CSV strings, filters for LEO, and yields Satrec models.
        Isolated from network I/O for deterministic unit testing.
        """
        for fields in omm.parse_csv(text_stream):
            # Filter: Only process objects in Low Earth Orbit (>= 14 orbits per day)
            # This throws out high-altitude objects (like GEO/MEO) that are nowhere near decaying.
            if float(fields['MEAN_MOTION']) < 14.0:
                continue

            satellite = Satrec()
            omm.initialize(satellite, fields)
            yield satellite