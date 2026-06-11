"""
src/formatter.py

Format the result as mapbox-compatible json
"""
import json

def generate_geojson(with_trajectory, immediate_decays):
    """
    Converts a list of satellite decay trajectories into a valid GeoJSON FeatureCollection.
    Structures the data specifically for Mapbox GL JS 'line-z-offset' elevated lines.
    """
    features = []

    # 1. Handle the trajectory lines (LineString)
    for event in with_trajectory:
        feature = {
            "type": "Feature",
            "properties": {
                "catalog_id": event["catalog_id"],
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

    # 2. Handle the immediate decays (Point)
    for event in immediate_decays:
        feature = {
            "type": "Feature",
            "properties": {
                "catalog_id": event["catalog_id"],
                "elevation": event["altitudes"][0],  # Grab the single float
                "timestamp": event["timestamps"][0],  # Grab the single string
                "type": "immediate_decay"
            },
            "geometry": {
                "type": "Point",
                "coordinates": event["trajectory"][0]  # Flatten from [[lon, lat]] to [lon, lat]
            }
        }
        features.append(feature)

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    return json.dumps(feature_collection, indent=2)
