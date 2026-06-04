
import numpy as np
from unittest.mock import MagicMock
from datetime import datetime, timezone

# Import the functions we want to test
from src.propagator import _build_time_window, _detect_decay_worker, orchestrator


def test_build_time_window(mocker):
    """
    Ensures our timescale builder requests exactly 336 discrete 30-minute
    steps without making actual network calls.
    """
    # Mock the Loader so it doesn't try to look for or download real files
    mock_loader = mocker.patch("src.propagator.Loader")
    mock_ts = mock_loader.return_value.timescale.return_value

    # Mock datetime to return a static, predictable time
    mock_datetime = mocker.patch("src.propagator.datetime")
    mock_datetime.now.return_value = datetime(2026, 6, 2, 12, 0, 0, tzinfo=timezone.utc)

    _build_time_window()

    # Verify the UTC method was called with the right year/month/day
    mock_ts.utc.assert_called_once()
    args, kwargs = mock_ts.utc.call_args
    assert args == (2026, 6, 2)

    # Verify we requested exactly 336 steps
    assert len(kwargs['hours']) == 336
    assert kwargs['hours'][0] == 0.0  # T+0 hours
    assert kwargs['hours'][1] == 0.5  # T+0.5 hours


def test_detect_decay_worker_finds_decay(mocker):
    """
    Simulates a satellite dropping below 105 km and ensures the correct
    dictionary is returned.
    """
    # Mock the dependencies
    mock_from_satrec = mocker.patch("src.propagator.EarthSatellite.from_satrec")
    mock_wgs84 = mocker.patch("src.propagator.wgs84.geographic_position_of")

    # Construct fake geodetic data where elevation drops below 105km at index 1
    mock_geodetic = MagicMock()
    mock_geodetic.elevation.km = np.array([150.0, 100.0, 90.0])
    mock_geodetic.latitude.degrees = np.array([45.0, 46.0, 47.0])
    mock_geodetic.longitude.degrees = np.array([-104.0, -105.0, -106.0])

    mock_wgs84.return_value = mock_geodetic

    # Create a fake timescale array
    mock_timescale = [MagicMock(), MagicMock(), MagicMock()]
    mock_timescale[1].utc_iso.return_value = "2026-06-02T13:00:00Z"

    # Create a fake satrec with a catalog ID
    fake_satrec = MagicMock()
    # We also need to mock the satellite model inside from_satrec so it returns the ID
    mock_from_satrec.return_value.model.satnum = 99999

    # Execute the function
    result = _detect_decay_worker(fake_satrec, mock_timescale)

    # Assertions
    assert result is not None
    assert result["catalog_id"] == 99999
    assert result["decay_time"] == "2026-06-02T13:00:00Z"
    assert result["latitude"] == 46.0  # Should grab the value at index 1
    assert result["longitude"] == -105.0


def test_detect_decay_worker_no_decay(mocker):
    """
    Simulates a stable orbit > 105 km and ensures None is returned.
    """
    mocker.patch("src.propagator.EarthSatellite.from_satrec")
    mock_wgs84 = mocker.patch("src.propagator.wgs84.geographic_position_of")

    # Array where elevation NEVER drops below 105km
    mock_geodetic = MagicMock()
    mock_geodetic.elevation.km = np.array([400.0, 399.0, 398.0])
    mock_wgs84.return_value = mock_geodetic

    result = _detect_decay_worker(MagicMock(), [MagicMock(), MagicMock(), MagicMock()])

    assert result is None


def test_orchestrator_filters_results(mocker):
    """
    Ensures the multiprocessing orchestrator properly removes None values
    and returns a flat list of actual decay events.
    """
    mock_executor = mocker.patch("src.propagator.ProcessPoolExecutor")

    # Simulate executor.map() returning a mix of decay dictionaries and None values
    fake_map_results = [
        {"catalog_id": 1},
        None,
        {"catalog_id": 2},
        None
    ]

    # Set up the context manager mock logic
    mock_executor.return_value.__enter__.return_value.map.return_value = fake_map_results

    # Mock the time window to avoid executing actual timescale logic
    mocker.patch("src.propagator._build_time_window")

    # Execute
    results = orchestrator(["fake_sat_1", "fake_sat_2", "fake_sat_3", "fake_sat_4"])

    # Assert it filtered out the None values and kept only the dicts
    assert len(results) == 2
    assert results[0]["catalog_id"] == 1
    assert results[1]["catalog_id"] == 2