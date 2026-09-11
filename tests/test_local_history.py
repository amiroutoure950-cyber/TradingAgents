import pytest

from local_app import (
    clear_analysis_history,
    get_analysis_history,
    save_analysis_history,
)


def test_analysis_history_persists_completed_analysis(tmp_path, monkeypatch):
    monkeypatch.setenv("FOREX_AGENT_HISTORY_DB", str(tmp_path / "history.sqlite3"))
    clear_analysis_history()

    saved = save_analysis_history(
        {
            "symbol": "EURUSD=X",
            "date": "2026-09-10",
            "asset_type": "forex",
            "analysts": ["market", "news"],
            "decision": "HOLD",
            "reports": {"market_report": "Trend neutral"},
        }
    )

    history = get_analysis_history()
    assert len(history) == 1
    assert history[0]["id"] == saved["id"]
    assert history[0]["decision"] == "HOLD"
    assert history[0]["reports"]["market_report"] == "Trend neutral"


def test_analysis_history_can_be_deleted(tmp_path, monkeypatch):
    monkeypatch.setenv("FOREX_AGENT_HISTORY_DB", str(tmp_path / "history.sqlite3"))
    clear_analysis_history()
    saved = save_analysis_history(
        {"symbol": "GBPUSD=X", "date": "2026-09-10", "decision": "BUY", "reports": {}}
    )

    assert clear_analysis_history(saved["id"]) is True
    assert get_analysis_history() == []
    assert clear_analysis_history(saved["id"]) is False
