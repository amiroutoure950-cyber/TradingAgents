import os

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.llm_clients.api_key_env import get_api_key_env
from tradingagents.llm_clients.openai_client import OPENAI_COMPATIBLE_PROVIDERS, OpenAIClient


def test_atessa_provider_uses_hermes_key_and_endpoint():
    assert get_api_key_env("atessa") == "HERMES_CUSTOM_ATESSA_API_KEY"
    spec = OPENAI_COMPATIBLE_PROVIDERS["atessa"]
    assert spec.base_url == "https://atessa.top/v1"


def test_atessa_astra_model_is_configured_for_local_ui(monkeypatch):
    monkeypatch.setenv("HERMES_CUSTOM_ATESSA_API_KEY", "test-key")
    client = OpenAIClient("gpt-6-astra", provider="atessa")
    llm = client.get_llm()
    assert str(llm.openai_api_base).rstrip("/") == "https://atessa.top/v1"
    assert DEFAULT_CONFIG["llm_provider"] in {"openai", "atessa"}
