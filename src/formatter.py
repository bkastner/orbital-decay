"""
src/formatter.py

Format the result as mapbox-compatible json
"""
import json
from datetime import datetime
from datetime import timezone
from typing import Any

def generate_geojson(with_trajectory: list[dict[str, Any]]) -> str:
    """
    Serializes a list of satellite decay trajectories into a valid GeoJSON FeatureCollection.

    Args:
        with_trajectory: List of satellites.

    Returns:
        A serialized GeoJSON string.
    """
    features = []

    for event in with_trajectory:
        feature = {
            "type": "Feature",
            "properties": {
                "catalog_id": event["catalog_id"],
                "satellite_name": event["name"],
                "elevation": event["altitudes"],
                "timestamps": event["timestamps"],
                "type": "trajectory"
            },
            "geometry": {
                "type": "LineString",
                "coordinates": event["trajectory"]
            }
        }
        features.append(feature)


    feature_collection = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "type": "FeatureCollection",
        "features": features
    }

    return json.dumps(feature_collection, indent=2)
