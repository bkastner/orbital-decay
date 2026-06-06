import pytest
from unittest.mock import MagicMock
from src.celestrak_client import CelestrakClient

def test_parse_omm_stream_filters_num_orbits(mocker):
    mock_csv_parser = mocker.patch('src.celestrak_client.omm.parse_csv')
    mocker.patch('src.celestrak_client.Satrec')

    mock_omm_initialize = mocker.patch('src.celestrak_client.omm.initialize')

    mock_csv_parser.return_value = [
        {'MEAN_MOTION': '14.1'},  # Keep
        {'MEAN_MOTION': '14.0'},  # Keep
        {'MEAN_MOTION': '13.9'}   # Drop
        ]

    result = list(CelestrakClient().parse_omm_stream(MagicMock()))
    assert len(result) == 2
    assert mock_omm_initialize.call_count == 2


def test_get_active_catalog_success(mocker):
    client = CelestrakClient()
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__iter__.return_value = [b"line1\nline2\n"]

    mocker.patch.object(client.http, 'request', return_value=mock_response)
    mocker.patch.object(client, 'parse_omm_stream', return_value=['success'])

    response = list(client.get_active_catalog())
    assert response == ['success']

def test_get_active_catalog_fail(mocker):
    client = CelestrakClient()
    mock_response = MagicMock()
    mock_response.status = 500

    mocker.patch.object(client.http, 'request', return_value=mock_response)

    with pytest.raises(ConnectionError):
        list(client.get_active_catalog())