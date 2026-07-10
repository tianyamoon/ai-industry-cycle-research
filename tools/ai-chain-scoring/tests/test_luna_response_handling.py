from __future__ import annotations

import pytest
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from luna_http_client import build_technical_audit_fields, parse_tool_call_response, require_usable_result


def test_parse_tool_call_response_prefers_structured_content_and_meta() -> None:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{"type": "text", "text": "{\"legacy\": true}"}],
            "structuredContent": {
                "ok": True,
                "data": {"value": 1},
                "meta": {
                    "actual_source": "thsdk",
                    "fallback_used": False,
                    "confidence": "high",
                    "warnings": [],
                },
            },
            "isError": False,
        },
    }

    result = parse_tool_call_response(payload)

    assert result.ok is True
    assert result.is_error is False
    assert result.structured_content["data"]["value"] == 1
    assert result.meta["actual_source"] == "thsdk"
    assert result.content_text == "{\"legacy\": true}"


def test_require_usable_result_rejects_error_payload() -> None:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{"type": "text", "text": "bad"}],
            "structuredContent": {"ok": False},
            "isError": True,
        },
    }

    result = parse_tool_call_response(payload)

    with pytest.raises(RuntimeError):
        require_usable_result(result)


def test_build_technical_audit_fields_tracks_meta_and_cross_source_status() -> None:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{"type": "text", "text": "legacy"}],
            "structuredContent": {
                "ok": True,
                "data": {"value": 1},
                "meta": {
                    "actual_source": "thsdk",
                    "fallback_used": False,
                    "confidence": "high",
                    "warnings": [],
                },
            },
            "isError": False,
        },
    }
    validate_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "structuredContent": {"ok": True, "results": []},
            "isError": False,
        },
    }

    result = parse_tool_call_response(payload)
    cross_source_result = parse_tool_call_response(validate_payload)

    audit_fields = build_technical_audit_fields(
        result,
        tool_name="get_kline",
        arguments={"symbol": "600519", "period": "weekly", "count": 10},
        cross_source_result=cross_source_result,
    )

    assert audit_fields["technical_tool"] == "get_kline"
    assert audit_fields["technical_structured_ready"] == "是"
    assert audit_fields["technical_actual_source"] == "thsdk"
    assert audit_fields["technical_fallback_used"] == "否"
    assert audit_fields["technical_confidence"] == "high"
    assert audit_fields["technical_warnings"] == "无"
    assert audit_fields["technical_cross_source_validated"] == "是"
    assert audit_fields["technical_cross_source_ok"] == "是"
