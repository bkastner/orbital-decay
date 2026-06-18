"""
src/celestrak_client.py
"""
import io
import urllib3
import logging
from sgp4 import omm
from typing import Generator, Iterable, Any

MEAN_MOTION_THRESHOLD = 14

logger = logging.getLogger(__name__)

class CelestrakClient:
    """
    Class that retrieves data from celestrak.org
    """
    def __init__(self, endpoint_url: str="https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv", local_file: str | None =None) -> None:
        """
        Initialize a CelestrakClient object.

        Args:
            endpoint_url: The URL to retrieve the CSV data from.
            local_file: An optional local CSV file to use instead of hitting the URL.  Used during testing to respect
            celestrak.org's strict usage limits.
        """
        # Establish low-overhead HTTP connection pooling
        self.http = urllib3.PoolManager(num_pools=5, maxsize=10)
        self.endpoint_url = endpoint_url
        self.local_file = local_file

    def get_active_catalog(self) -> Generator[dict[str, Any], None, None]:
        """
        Fetches the active catalog from the network and yields parsed Satrec objects.
        If self.local_file is present, then load data from it instead of Celestrak.

        Streams the response to maintain a minimal memory footprint.

        Returns:
            Streams the parsed satellite record dictionaries.
        """

        if self.local_file is None:
            logger.info(f"Fetching OMM CSV stream from: {self.endpoint_url}")

            response = self.http.request('GET', self.endpoint_url, preload_content=False)

            if response.status != 200:
                raise ConnectionError(f"Celestrak HTTP Error: {response.status}")

            text_stream = (line.decode('utf-8') for line in response)

            yield from self.parse_omm_stream(text_stream)

            response.release_conn()
        else:
            with io.open(self.local_file, 'r') as local_data:
                text_stream = (line for line in local_data)
                yield from self.parse_omm_stream(text_stream)

    def parse_omm_stream(self, text_stream: Iterable[str]) -> Generator[dict[str, Any], None, None]:
        """
        Consumes an iterable of CSV lines representing satellites, filters for satellites in LEO, and yields Satrec models.

        Isolated from network I/O for deterministic unit testing.

        Args:
            text_stream: A list of strings, each item is a row from the downloaded CSV file

        Returns:
            A generator of parsed Satrec objects
        """
        for fields in omm.parse_csv(text_stream):
            # Filter: Only process objects in Low Earth Orbit (>= 14 orbits per day)
            # This throws out high-altitude objects (like GEO/MEO) that are nowhere near decaying.
            if float(fields['MEAN_MOTION']) < MEAN_MOTION_THRESHOLD:
                continue
            # Filter out satellites with negative BSTAR (actively maneuvering)
            if float(fields['BSTAR']) < 0:
                continue

            yield fields