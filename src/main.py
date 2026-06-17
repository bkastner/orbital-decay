"""
src/main.py

Entry point for orbital decay predictor app.
"""
import os
import boto3
import argparse
import logging
import sys

from botocore.exceptions import NoCredentialsError
from celestrak_client import CelestrakClient
from propagator import orchestrator
from formatter import generate_geojson
from sgp4.api import accelerated

CACHE_CONTROL_TIMEOUT_SEC = 3600 # 1 hour

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def upload_geojson_to_s3(file_path: str) -> None:
    bucket_name = os.getenv('S3_BUCKET_NAME')

    if not bucket_name:
        logger.error("S3_BUCKET_NAME environment variable not found. Skipping S3 upload.")
        return

    s3_client = boto3.client('s3')

    logger.info(f"Uploading {file_path} to s3://{bucket_name}/decays.geojson...")

    try:
        s3_client.upload_file(
            file_path,
            bucket_name,
            'decays.geojson',
            ExtraArgs={
                'ContentType': 'application/geo+json',
                'CacheControl': f'public, max-age={CACHE_CONTROL_TIMEOUT_SEC}'
            }
        )
        logger.info("Successfully uploaded to S3!") 
    except NoCredentialsError:
        logger.error("Error: AWS credentials not found. Cannot upload to S3.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred during S3 upload: {e}")
        sys.exit(1)

def main() -> None:
    parser = argparse.ArgumentParser(description="Orbital Decay Predictor Pipeline")
    parser.add_argument(
        '--local-file',
        type=str,
        help="Path to a local CSV file to bypass CelesTrak network requests."
    )
    args = parser.parse_args()

    # Check if SGP4 is using the C++ implementation
    if accelerated:
        logger.info('SGP4 is using the accelerated C++ implementation')
    else:
        logger.info('SGP4 is using the slow Python implementation, performance will be greatly reduced.')

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

    with_trajectory = orchestrator(satellite_records)

    logger.info("Propagation complete.")
    logger.info(f"Detected {len(with_trajectory)} impending re-entries.")

    logger.info("Formatting results into 3D GeoJSON FeatureCollection...")
    geojson_output = generate_geojson(with_trajectory)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.abspath(os.path.join(base_dir, '..', 'web'))
    os.makedirs(web_dir, exist_ok=True)

    output_path = os.path.join(web_dir, 'decays.geojson')

    with open(output_path, 'w') as f:
        f.write(geojson_output)

    logger.info(f"Success! Data payload written to: {output_path}")

    upload_geojson_to_s3(output_path)

if __name__ == "__main__":
    main()