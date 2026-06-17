"""
src/download_data.py

Pre-download Skyfield data to a local directory for later incorporation into a container.
"""

import os
from skyfield.api import Loader


def download_timescale_data() -> None:
    """
    Downloads IERS Earth rotation and leap second data required by Skyfield.
    This script is executed during the Docker build process so the data is
    baked directly into the container image.
    """
    # 1. Resolve the absolute path to src/static/skyfield_data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'static', 'skyfield_data')
    os.makedirs(data_dir, exist_ok=True)

    print(f"Downloading Skyfield timescale files to: {data_dir}")

    load = Loader(data_dir)
    load.timescale(builtin=False)

    print("Download complete. Files are ready for containerization.")

if __name__ == "__main__":
    download_timescale_data()