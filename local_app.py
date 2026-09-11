"""Local browser interface for the Forex TradingAgents research workflow."""

from __future__ import annotations

import datetime as dt
import json
import os
import threading
import uuid
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from cli.models import AnalystType, AssetType
from cli.utils import filter_analysts_for_asset_type
from tradingagents.dataflows.symbol_utils import is_yahoo_safe, normalize_symbol
from tradingagents.default_config import DEFAULT_CONFIG



BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
app = Flask(__name__, template_folder=str(BASE_DIR / "local_ui" / "templates"), static_folder=str(BASE_DIR / "local_ui" / "static"))
_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def validate_analysis_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a browser request before starting an agent run."""
    raw_symbol = str(payload.get("symbol", "")).strip()
    symbol = normalize_symbol(raw_symbol)
    if not raw_symbol or not is_yahoo_safe(symbol):
        raise ValueError("symbol must contain only valid market-symbol characters")

    analysis_date = str(payload.get("date", "")).strip()
    try:
        dt.datetime.strptime(analysis_date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("date must use YYYY-MM-DD format") from exc

    analysts = payload.get("analysts") or ["market", "news"]
    allowed = {analyst.value for analyst in AnalystType}
    if not isinstance(analysts, list) or not analysts or not set(analysts) <= allowed:
        raise ValueError("analysts must be a non-empty list of valid analyst names")

    asset_type = "forex" if symbol.endswith("=X") else "stock"
    if asset_type == "forex":
        selected = filter_analysts_for_asset_type(
            [AnalystType(value) for value in analysts], AssetType.FOREX
        )
        analysts = [analyst.value for analyst in selected]

    return {"symbol": symbol, "date": analysis_date, "asset_type": asset_type, "analysts": analysts}


def _run_job(job_id: str, payload: dict[str, Any]) -> None:
    try:
        with _jobs_lock:
            _jobs[job_id]["status"] = "running"
            _jobs[job_id]["message"] = "Initialisation des analystes…"

        # Import the heavy LangGraph/LLM stack only when a run is requested so
        # the local shell and request-validation endpoints remain lightweight.
        from tradingagents.graph.trading_graph import TradingAgentsGraph

        config = DEFAULT_CONFIG.copy()
        config["output_language"] = "French"
        graph = TradingAgentsGraph(
            selected_analysts=tuple(payload["analysts"]),
            debug=False,
            config=config,
        )
        with _jobs_lock:
            _jobs[job_id]["message"] = "Analyse macroéconomique et technique en cours…"
        state, decision = graph.propagate(
            payload["symbol"], payload["date"], asset_type=payload["asset_type"]
        )
        reports = {
            key: state.get(key, "")
            for key in (
                "market_report",
                "news_report",
                "sentiment_report",
                "investment_plan",
                "trader_investment_plan",
                "final_trade_decision",
            )
        }
        with _jobs_lock:
            _jobs[job_id].update(
                status="completed",
                message="Analyse terminée",
                decision=decision,
                reports=reports,
            )
    except Exception as exc:
        with _jobs_lock:
            _jobs[job_id].update(status="failed", message=str(exc))


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/analyze")
def analyze():
    try:
        payload = validate_analysis_request(request.get_json(silent=True) or {})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    job_id = uuid.uuid4().hex
    with _jobs_lock:
        _jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "message": "Analyse en attente…",
            "payload": payload,
        }
    threading.Thread(target=_run_job, args=(job_id, payload), daemon=True).start()
    return jsonify({"job_id": job_id, "payload": payload}), 202


@app.get("/api/jobs/<job_id>")
def job_status(job_id: str):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if job is None:
        return jsonify({"error": "job not found"}), 404
    return jsonify(job)


def main() -> None:
    """Start the loopback-only local UI server."""
    app.run(host="127.0.0.1", port=int(os.getenv("FOREX_AGENT_PORT", "8765")), debug=False)


if __name__ == "__main__":
    main()
