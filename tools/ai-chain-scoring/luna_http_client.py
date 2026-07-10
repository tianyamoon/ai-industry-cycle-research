from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


class BaseUrlConfigurationError(RuntimeError):
    """Raised when the Luna HTTP bridge has not been configured."""


def resolve_base_url(cli_value: str | None) -> str:
    raw = cli_value or os.environ.get("LUNA_STOCK_MCP_URL")
    if not raw:
        raise BaseUrlConfigurationError(
            "Luna Stock MCP URL is not configured. Pass --base-url or set LUNA_STOCK_MCP_URL."
        )
    return raw.rstrip("/")


@dataclass
class LunaToolResult:
    ok: bool
    is_error: bool
    structured_content: Any
    content_text: str
    meta: dict[str, Any]
    raw: dict[str, Any]


def _warnings_to_text(warnings: Any) -> str:
    if warnings in (None, "", [], ()):
        return "无"
    if isinstance(warnings, list):
        return " | ".join(str(item) for item in warnings) or "无"
    return str(warnings)


def _join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def _http_get_json(base_url: str, path: str) -> dict[str, Any]:
    url = _join_url(base_url, path)
    with request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_post_json(base_url: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = _join_url(base_url, path)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def list_tools(base_url: str | None = None) -> dict[str, Any]:
    return _http_get_json(resolve_base_url(base_url), "/tools/list")


def parse_tool_call_response(payload: dict[str, Any]) -> LunaToolResult:
    result = payload.get("result") or {}
    content = result.get("content") or []
    content_text = ""
    if content and isinstance(content, list):
        first = content[0] or {}
        content_text = str(first.get("text") or "")

    structured = result.get("structuredContent")
    meta: dict[str, Any] = {}
    if isinstance(structured, dict) and isinstance(structured.get("meta"), dict):
        meta = structured["meta"]
    elif isinstance(result.get("meta"), dict):
        meta = result["meta"]

    is_error = bool(result.get("isError"))
    ok = not is_error
    if isinstance(structured, dict) and "ok" in structured:
        ok = ok and bool(structured.get("ok"))

    return LunaToolResult(
        ok=ok,
        is_error=is_error,
        structured_content=structured,
        content_text=content_text,
        meta=meta,
        raw=payload,
    )


def call_tool(
    name: str,
    arguments: dict[str, Any] | None = None,
    base_url: str | None = None,
) -> LunaToolResult:
    payload = _http_post_json(
        resolve_base_url(base_url),
        "/tools/call",
        {"name": name, "arguments": arguments or {}},
    )
    return parse_tool_call_response(payload)


def validate_cross_source(
    capability: str,
    sources: list[str] | None = None,
    validation_arguments: dict[str, Any] | None = None,
    base_url: str | None = None,
) -> LunaToolResult:
    arguments: dict[str, Any] = dict(validation_arguments or {})
    arguments["capability"] = capability
    if sources:
        arguments["sources"] = sources
    return call_tool("validate_cross_source", arguments, base_url=base_url)


def require_usable_result(result: LunaToolResult) -> None:
    if result.is_error:
        raise RuntimeError("Luna tool call returned isError=true")
    if not result.ok:
        raise RuntimeError("Luna tool call returned ok=false")


def load_arguments(arguments_json: str, arguments_file: str | None = None) -> dict[str, Any]:
    if arguments_file:
        return json.loads(Path(arguments_file).read_text(encoding="utf-8-sig"))
    return json.loads(arguments_json)


def build_technical_audit_fields(
    result: LunaToolResult,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    cross_source_result: LunaToolResult | None = None,
) -> dict[str, str]:
    structured_ready = result.structured_content not in (None, "", [])
    cross_source_ok = False
    if cross_source_result is not None:
        cross_source_ok = cross_source_result.ok and not cross_source_result.is_error
        if isinstance(cross_source_result.structured_content, dict) and "ok" in cross_source_result.structured_content:
            cross_source_ok = cross_source_ok and bool(cross_source_result.structured_content.get("ok"))

    return {
        "technical_tool": tool_name,
        "technical_arguments": json.dumps(arguments or {}, ensure_ascii=False, sort_keys=True),
        "technical_structured_ready": "是" if structured_ready else "否",
        "technical_actual_source": str(result.meta.get("actual_source") or "待补"),
        "technical_fallback_used": "是" if bool(result.meta.get("fallback_used")) else "否",
        "technical_confidence": str(result.meta.get("confidence") or "待补"),
        "technical_warnings": _warnings_to_text(result.meta.get("warnings")),
        "technical_cross_source_validated": "是" if cross_source_result is not None else "否",
        "technical_cross_source_ok": "是" if cross_source_ok else "否",
    }


def print_summary(result: LunaToolResult) -> None:
    summary = {
        "ok": result.ok,
        "is_error": result.is_error,
        "structured_content": result.structured_content,
        "content_text": result.content_text,
        "meta": result.meta,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="HTTP client for Luna Stock MCP.")
    parser.add_argument("--base-url")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-tools", help="GET /tools/list")

    call_parser = subparsers.add_parser("call", help="POST /tools/call")
    call_parser.add_argument("tool_name")
    call_parser.add_argument("--arguments", default="{}", help="JSON string for tool arguments")
    call_parser.add_argument("--arguments-file", help="Path to a UTF-8 JSON file for tool arguments")
    call_parser.add_argument("--require-usable", action="store_true")

    audit_parser = subparsers.add_parser("audit-tech", help="Call a Luna tool and print audit fields")
    audit_parser.add_argument("tool_name")
    audit_parser.add_argument("--arguments", default="{}", help="JSON string for tool arguments")
    audit_parser.add_argument("--arguments-file", help="Path to a UTF-8 JSON file for tool arguments")
    audit_parser.add_argument("--validate-capability", help="Optional capability for validate_cross_source")
    audit_parser.add_argument("--sources", nargs="*")
    audit_parser.add_argument("--require-usable", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Call validate_cross_source")
    validate_parser.add_argument("capability")
    validate_parser.add_argument("--sources", nargs="*")
    validate_parser.add_argument("--require-usable", action="store_true")

    args = parser.parse_args()

    try:
        base_url = resolve_base_url(args.base_url)
        if args.command == "list-tools":
            print(json.dumps(list_tools(base_url), ensure_ascii=False, indent=2))
            return 0

        if args.command == "call":
            arguments = load_arguments(args.arguments, args.arguments_file)
            result = call_tool(args.tool_name, arguments, base_url=base_url)
            if args.require_usable:
                require_usable_result(result)
            print_summary(result)
            return 0

        if args.command == "audit-tech":
            arguments = load_arguments(args.arguments, args.arguments_file)
            result = call_tool(args.tool_name, arguments, base_url=base_url)
            if args.require_usable:
                require_usable_result(result)

            cross_source_result = None
            if args.validate_capability:
                cross_source_result = validate_cross_source(
                    args.validate_capability,
                    sources=args.sources,
                    validation_arguments=arguments,
                    base_url=base_url,
                )

            print(
                json.dumps(
                    build_technical_audit_fields(
                        result,
                        tool_name=args.tool_name,
                        arguments=arguments,
                        cross_source_result=cross_source_result,
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0

        if args.command == "validate":
            result = validate_cross_source(args.capability, sources=args.sources, base_url=base_url)
            if args.require_usable:
                require_usable_result(result)
            print_summary(result)
            return 0
    except error.HTTPError as exc:
        print(f"HTTPError {exc.code}: {exc.reason}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
