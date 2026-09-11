import pytest

from local_app import validate_analysis_request


def test_validate_forex_request_normalizes_pair_and_defaults_analysts():
    request = validate_analysis_request({"symbol": "eurusd", "date": "2026-09-10"})

    assert request["symbol"] == "EURUSD=X"
    assert request["asset_type"] == "forex"
    assert request["analysts"] == ["market", "news"]


def test_validate_request_rejects_unknown_symbol_and_bad_date():
    with pytest.raises(ValueError, match="symbol"):
        validate_analysis_request({"symbol": "not a pair", "date": "2026-09-10"})

    with pytest.raises(ValueError, match="date"):
        validate_analysis_request({"symbol": "EURUSD", "date": "10/09/2026"})
