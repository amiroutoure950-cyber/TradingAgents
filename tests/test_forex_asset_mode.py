"""Forex mode behavior: canonical symbols, analyst selection, and prompts."""

from cli.models import AnalystType, AssetType
from cli.utils import detect_asset_type, filter_analysts_for_asset_type
from tradingagents.dataflows.symbol_utils import normalize_symbol


def test_major_and_minor_pairs_are_classified_as_forex():
    assert detect_asset_type("EURUSD") == AssetType.FOREX
    assert detect_asset_type("GBPJPY") == AssetType.FOREX
    assert detect_asset_type("AUDNZD") == AssetType.FOREX


def test_forex_symbols_normalize_to_yahoo_spot_pairs():
    assert normalize_symbol("EURUSD") == "EURUSD=X"
    assert normalize_symbol("gbpjpy") == "GBPJPY=X"


def test_forex_mode_excludes_equity_fundamentals():
    selected = filter_analysts_for_asset_type(
        list(AnalystType), AssetType.FOREX
    )
    assert AnalystType.FUNDAMENTALS not in selected
    assert AnalystType.MARKET in selected
    assert AnalystType.NEWS in selected


def test_forex_mode_is_distinct_from_stock_and_crypto():
    assert detect_asset_type("AAPL") == AssetType.STOCK
    assert detect_asset_type("BTCUSD") == AssetType.CRYPTO
    assert detect_asset_type("USDCHF") == AssetType.FOREX
