"""
src/formatter.py

Format the result as mapbox-compatible json
"""
import json
from datetime import datetime
from datetime import timezone

def generate_geojson(with_trajectory):
    """
    Converts a list of satellite decay trajectories into a valid GeoJSON FeatureCollection.
    Structures the data specifically for Mapbox GL JS 'line-z-offset' elevated lines.
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
