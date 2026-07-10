from __future__ import annotations

import sys
from pathlib import Path

import pytest


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

import luna_http_client
from luna_http_client import BaseUrlConfigurationError, resolve_base_url


def test_cli_base_url_takes_precedence_over_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUNA_STOCK_MCP_URL", "http://env.example:8765")

    assert resolve_base_url("http://cli.example:8765") == "http://cli.example:8765"


def test_environment_supplies_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUNA_STOCK_MCP_URL", "http://env.example:8765/")

    assert resolve_base_url(None) == "http://env.example:8765"


def test_missing_base_url_fails_instead_of_using_a_private_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LUNA_STOCK_MCP_URL", raising=False)

    with pytest.raises(BaseUrlConfigurationError, match="LUNA_STOCK_MCP_URL"):
        resolve_base_url(None)


def test_public_client_source_contains_no_private_endpoint() -> None:
    source = (TOOL_ROOT / "luna_http_client.py").read_text(encoding="utf-8")

    assert "192.168.1.123" not in source


def test_cross_source_validation_forwards_subject_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    sentinel = object()

    def fake_call_tool(
        name: str,
        arguments: dict[str, object],
        base_url: str | None = None,
    ) -> object:
        captured.update(name=name, arguments=arguments, base_url=base_url)
        return sentinel

    monkeypatch.setattr(luna_http_client, "call_tool", fake_call_tool)

    result = luna_http_client.validate_cross_source(
        "multi_period_kline",
        sources=["tencent", "tdx", "thsdk"],
        validation_arguments={"symbol": "600519", "period": "weekly", "count": 5},
        base_url="http://example.test",
    )

    assert result is sentinel
    assert captured == {
        "name": "validate_cross_source",
        "arguments": {
            "symbol": "600519",
            "period": "weekly",
            "count": 5,
            "capability": "multi_period_kline",
            "sources": ["tencent", "tdx", "thsdk"],
        },
        "base_url": "http://example.test",
    }
