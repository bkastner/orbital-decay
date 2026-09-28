
import json
from pathlib import Path
from datetime import datetime, timezone
import pytest
# Import the functions we want to test
from src.formatter import generate_geojson

EXAMPLE_PATH = Path(__file__).parent / "decays_example.geojson"


@pytest.fixture
def example():
    """The known-good pipeline output."""
    with open(EXAMPLE_PATH) as f:
        return json.load(f)


@pytest.fixture
def example_events(example):
    """Rebuilds the formatter's input events from the example output."""
    return [
        {
            "catalog_id": feature["properties"]["catalog_id"],
            "name": feature["properties"]["satellite_name"],
            "altitudes": feature["properties"]["elevation"],
            "timestamps": feature["properties"]["timestamps"],
            "trajectory": feature["geometry"]["coordinates"],
        }
        for feature in example["features"]
    ]


def test_generate_geojson_matches_example(example, example_events):
    """
    Feeds the example's underlying data back through the formatter and ensures
    the output matches the known-good file (ignoring the generation timestamp).
    """
    result = json.loads(generate_geojson(example_events))

    result.pop("updated")
    example.pop("updated")
    assert result == example


def test_generate_geojson_collection_structure(example_events):
    """
    Ensures the top level is a FeatureCollection with one feature per event,
    in input order.
    """
    result = json.loads(generate_geojson(example_events))

    assert set(result.keys()) == {"updated", "type", "features"}
    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) == len(example_events)
    assert [f["properties"]["catalog_id"] for f in result["features"]] == \
        [e["catalog_id"] for e in example_events]


def test_generate_geojson_maps_event_fields():
    """
    Ensures each event field lands in the right place in the feature, using
    small hand-written values instead of the example file.
    """
    event = {
        "catalog_id": 12345,
        "name": "TEST-SAT",
        "altitudes": [100500.0, 99800.0],
        "timestamps": ["2026-01-01T00:00:00Z", "2026-01-01T00:01:00Z"],
        "trajectory": [[10.0, 20.0], [11.0, 21.0]],
    }

    result = json.loads(generate_geojson([event]))

    assert result["features"] == [{
        "type": "Feature",
        "properties": {
            "catalog_id": 12345,
            "satellite_name": "TEST-SAT",
            "elevation": [100500.0, 99800.0],
            "timestamps": ["2026-01-01T00:00:00Z", "2026-01-01T00:01:00Z"],
            "type": "trajectory",
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [[10.0, 20.0], [11.0, 21.0]],
        },
    }]


def test_generate_geojson_updated_timestamp(mocker):
    """
    Ensures the 'updated' field is the current UTC time in ISO format.
    """
    mock_datetime = mocker.patch("src.formatter.datetime")
    mock_datetime.now.return_value = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)

    result = json.loads(generate_geojson([]))

    mock_datetime.now.assert_called_once_with(timezone.utc)
    assert result["updated"] == "2026-09-28T12:00:00+00:00"


def test_generate_geojson_empty_input():
    """
    Ensures no decays still produces a valid, empty FeatureCollection.
    """
    result = json.loads(generate_geojson([]))

    assert result["type"] == "FeatureCollection"
    assert result["features"] == []
