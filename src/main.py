"""
src/main.py

Entry point for orbital decay predictor app.
"""
import os
import argparse
import logging
from celestrak_client import CelestrakClient
from propagator import orchestrator
from formatter import generate_geojson

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Orbital Decay Predictor Pipeline")
    parser.add_argument(
        '--local-file',
        type=str,
        help="Path to a local CSV file to bypass CelesTrak network requests."
    )
    args = parser.parse_args()

    logger.info("Initializing Celestrak Client...")
    client = CelestrakClient(local_file=args.local_file)

    logger.info("Fetching active satellite catalog...")
    try:
        sat_stream = client.get_active_catalog()
        satellite_records = list(sat_stream)
    except Exception as e:
        logger.error(f"Data ingestion failure: {e}")
        return

    logger.info(f"Filtered to {len(satellite_records)} LEO satellites. Starting CPU propagation engine...")

    with_trajectory, immediate_decays = orchestrator(satellite_records)

    logger.info("Propagation complete.")
    logger.info(f"Detected {len(with_trajectory)} impending re-entries with map trajectories.")
    logger.info(f"Detected {len(immediate_decays)} immediate re-entries (Point data).")

    logger.info("Formatting results into 3D GeoJSON FeatureCollection...")
    geojson_output = generate_geojson(with_trajectory, immediate_decays)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.abspath(os.path.join(base_dir, '..', 'web'))
    os.makedirs(web_dir, exist_ok=True)

    output_path = os.path.join(web_dir, 'decays.geojson')

    with open(output_path, 'w') as f:
        f.write(geojson_output)

    logger.info(f"Success! Data payload written to: {output_path}")

if __name__ == "__main__":
    main()