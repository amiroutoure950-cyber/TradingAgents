"""Forex-specific agent guidance and data-role helpers."""

from tradingagents.agents.utils.agent_utils import get_language_instruction


FOREX_ANALYST_CONTEXT = """You are analyzing a foreign-exchange pair, not an equity.
Focus on relative macroeconomics: central-bank policy differentials, inflation,
employment, growth, yield spreads, risk sentiment, commodities, and geopolitical
catalysts. Do not discuss company earnings, balance sheets, insider transactions,
or equity valuation. Quote the pair orientation explicitly: a bullish EURUSD
view means EUR strength and/or USD weakness. Separate spot price evidence from
macro interpretation, identify event risk, and state invalidation conditions.
"""


def forex_context(asset_type: str) -> str:
    """Return specialist context for forex runs while preserving other modes."""
    return FOREX_ANALYST_CONTEXT if asset_type == "forex" else ""
