from __future__ import annotations

import sys
import json
import re
import csv
import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

import large_cap_observation_pool as observation_pool
from large_cap_observation_pool import build_observation_records, tencent_symbol


def _candidate(code: str, name: str, layer: str, segment: str, source: str) -> dict[str, str]:
    return {
        "代码": code,
        "标的": name,
        "主层级": layer,
        "细分": segment,
        "来源网站": source,
        "当前等级": "L0/L1",
        "第一变量": "订单",
        "样本角色": "细分候选/组内补漏",
        "下一步回源": "回源年报",
        "证伪点": "收入无法验证",
    }


def test_build_observation_records_keeps_hard_boundary_and_missing_quotes() -> None:
    candidates = [
        _candidate("000001", "硬门槛样本", "计算芯片", "ASIC", "东方财富"),
        _candidate("000002", "边界样本", "高速互联", "CPO", "同花顺"),
        _candidate("000003", "低市值样本", "应用平台", "办公", "东方财富"),
        _candidate("000004", "市值缺失样本", "数据层", "AI语料", "同花顺"),
    ]
    quotes = {
        "000001": {"market_cap_yi": 100.0, "quote_time": "20260710161500"},
        "000002": {"market_cap_yi": 95.0, "quote_time": "20260710161500"},
        "000003": {"market_cap_yi": 89.9, "quote_time": "20260710161500"},
    }

    records = build_observation_records(candidates, quotes, as_of_date="2026-07-10")

    by_code = {record["代码"]: record for record in records}
    assert set(by_code) == {"000001", "000002", "000004"}
    assert by_code["000001"]["观察状态"] == "强制观察"
    assert by_code["000001"]["总市值(亿元)"] == "100.00"
    assert by_code["000002"]["观察状态"] == "边界复核"
    assert by_code["000004"]["观察状态"] == "市值待补"


def test_build_observation_records_merges_duplicate_candidate_routes() -> None:
    candidates = [
        _candidate("600001", "合并样本", "高速互联", "光模块", "东方财富"),
        _candidate("600001", "合并样本", "先进封装", "封装基板", "同花顺"),
    ]
    quotes = {"600001": {"market_cap_yi": 150.0, "quote_time": "20260710161500"}}

    records = build_observation_records(candidates, quotes, as_of_date="2026-07-10")

    assert len(records) == 1
    assert records[0]["主层级"] == "先进封装、高速互联"
    assert records[0]["来源网站"] == "东方财富、同花顺"
    assert records[0]["来源条数"] == "2"


def test_build_observation_records_does_not_turn_missing_codes_into_a_fake_stock() -> None:
    candidates = [
        _candidate("", "无代码样本甲", "终端与具身智能", "机器人", "韭研公社"),
        _candidate("", "无代码样本乙", "应用平台", "AI应用", "韭研公社"),
    ]

    records = build_observation_records(candidates, {}, as_of_date="2026-07-10")

    assert records == []


def test_tencent_symbol_uses_the_correct_exchange_prefix() -> None:
    assert tencent_symbol("600001") == "sh600001"
    assert tencent_symbol("000001") == "sz000001"
    assert tencent_symbol("830001") == "bj830001"
    assert tencent_symbol("920001") == "bj920001"


def test_parse_sina_market_rows_converts_market_cap_to_yi() -> None:
    raw = (
        '[{"code":"600001","name":"全市场样本","mktcap":1234567.89,'
        '"ticktime":"15:00:00"}]'
    )

    assert hasattr(observation_pool, "parse_sina_market_rows")
    rows = observation_pool.parse_sina_market_rows(raw)

    assert rows == [
        {
            "代码": "600001",
            "标的": "全市场样本",
            "总市值(亿元)": 123.456789,
            "快照时间": "15:00:00",
        }
    ]


def test_full_market_audit_keeps_unrouted_large_caps_visible() -> None:
    candidates = [
        _candidate("600001", "已路由样本", "计算芯片", "ASIC", "东方财富"),
    ]
    market_rows = [
        {"代码": "600001", "标的": "已路由样本", "总市值(亿元)": 120.0, "快照时间": "15:00:00"},
        {"代码": "600002", "标的": "待路由百亿样本", "总市值(亿元)": 100.0, "快照时间": "15:00:00"},
        {"代码": "600003", "标的": "边界待路由样本", "总市值(亿元)": 95.0, "快照时间": "15:00:00"},
        {"代码": "600004", "标的": "低于复核带样本", "总市值(亿元)": 89.9, "快照时间": "15:00:00"},
    ]

    assert hasattr(observation_pool, "build_full_market_audit_records")
    records = observation_pool.build_full_market_audit_records(
        candidates,
        market_rows,
        as_of_date="2026-07-10",
    )

    by_code = {record["代码"]: record for record in records}
    assert set(by_code) == {"600001", "600002", "600003"}
    assert by_code["600001"]["AI路由状态"] == "已路由AI候选"
    assert by_code["600001"]["观察状态"] == "强制观察"
    assert by_code["600002"]["AI路由状态"] == "待路由审计"
    assert by_code["600002"]["观察状态"] == "强制审计"
    assert by_code["600003"]["观察状态"] == "边界待路由"


def test_full_market_audit_keeps_candidate_quotes_missing_from_sina() -> None:
    candidates = [
        _candidate("689009", "候选补充样本", "终端与具身智能", "机器人", "东方财富"),
    ]
    supplemental_rows = [
        {
            "代码": "689009",
            "标的": "候选补充样本",
            "总市值(亿元)": 120.0,
            "快照时间": "15:00:00",
            "市值来源": "腾讯行情候选补充",
        }
    ]

    assert "supplemental_market_rows" in inspect.signature(
        observation_pool.build_full_market_audit_records
    ).parameters
    records = observation_pool.build_full_market_audit_records(
        candidates,
        [],
        supplemental_market_rows=supplemental_rows,
        as_of_date="2026-07-10",
    )

    assert len(records) == 1
    assert records[0]["代码"] == "689009"
    assert records[0]["观察状态"] == "强制观察"
    assert records[0]["市值来源"] == "腾讯行情候选补充"


def test_fetch_sina_market_rows_stops_after_the_boundary_page(monkeypatch) -> None:
    payloads = {
        1: [
            {"code": "600001", "name": "第一只", "mktcap": 1500000, "ticktime": "15:00:00"},
            {"code": "600002", "name": "第二只", "mktcap": 1100000, "ticktime": "15:00:00"},
        ],
        2: [
            {"code": "600003", "name": "边界只", "mktcap": 950000, "ticktime": "15:00:00"},
            {"code": "600004", "name": "低于边界", "mktcap": 890000, "ticktime": "15:00:00"},
        ],
    }
    requested_pages: list[int] = []

    def fake_run(command, **_kwargs):
        matched = re.search(r"[?&]page=(\d+)", command[-1])
        assert matched
        page = int(matched.group(1))
        requested_pages.append(page)
        return SimpleNamespace(returncode=0, stdout=json.dumps(payloads[page]), stderr="")

    monkeypatch.setattr(observation_pool.subprocess, "run", fake_run)

    assert hasattr(observation_pool, "fetch_sina_market_rows")
    rows = observation_pool.fetch_sina_market_rows(
        page_size=1000,
        timeout_seconds=1,
        minimum_yi=90.0,
    )

    assert requested_pages == [1, 2]
    assert [row["代码"] for row in rows] == ["600001", "600002", "600003"]


def test_fetch_sina_market_rows_refuses_to_silently_stop_before_the_boundary(monkeypatch) -> None:
    def fake_run(_command, **_kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                [
                    {"code": "600001", "name": "仍高于边界", "mktcap": 1500000, "ticktime": "15:00:00"},
                ]
            ),
            stderr="",
        )

    monkeypatch.setattr(observation_pool.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="before reaching the market-cap boundary"):
        observation_pool.fetch_sina_market_rows(
            page_size=1000,
            timeout_seconds=1,
            minimum_yi=90.0,
            max_pages=1,
        )


def test_main_writes_full_market_audit_outputs(monkeypatch, tmp_path: Path) -> None:
    input_path = tmp_path / "candidates.csv"
    with input_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_candidate("600001", "已路由样本", "计算芯片", "ASIC", "东方财富").keys())
        writer.writeheader()
        writer.writerow(_candidate("600001", "已路由样本", "计算芯片", "ASIC", "东方财富"))

    monkeypatch.setattr(
        observation_pool,
        "fetch_tencent_quotes",
        lambda *_args, **_kwargs: {"600001": {"market_cap_yi": 120.0, "quote_time": "20260710150000"}},
    )
    monkeypatch.setattr(
        observation_pool,
        "fetch_sina_market_rows",
        lambda **_kwargs: [
            {"代码": "600001", "标的": "已路由样本", "总市值(亿元)": 120.0, "快照时间": "15:00:00"},
            {"代码": "600002", "标的": "待路由样本", "总市值(亿元)": 101.0, "快照时间": "15:00:00"},
        ],
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "large_cap_observation_pool.py",
            "--repo-root",
            str(tmp_path),
            "--input",
            "candidates.csv",
            "--output",
            "observation.csv",
            "--summary",
            "observation.json",
            "--market-audit-output",
            "market-audit.csv",
            "--market-audit-summary",
            "market-audit.json",
            "--as-of-date",
            "2026-07-10",
        ],
    )

    assert observation_pool.main() == 0

    with (tmp_path / "market-audit.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        audit_rows = list(csv.DictReader(handle))
    audit_by_code = {row["代码"]: row for row in audit_rows}
    assert audit_by_code["600001"]["观察状态"] == "强制观察"
    assert audit_by_code["600002"]["AI路由状态"] == "待路由审计"

    audit_summary = json.loads((tmp_path / "market-audit.json").read_text(encoding="utf-8"))
    assert audit_summary["hard_threshold_count"] == 2
    assert audit_summary["unrouted_hard_count"] == 1


def test_main_keeps_legacy_summary_output_without_market_audit(monkeypatch, tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "candidates.csv"
    with input_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_candidate("600001", "已路由样本", "计算芯片", "ASIC", "东方财富").keys())
        writer.writeheader()
        writer.writerow(_candidate("600001", "已路由样本", "计算芯片", "ASIC", "东方财富"))
        writer.writerow(_candidate("", "待补代码线索", "终端与具身智能", "机器人", "韭研公社"))

    monkeypatch.setattr(
        observation_pool,
        "fetch_tencent_quotes",
        lambda *_args, **_kwargs: {"600001": {"market_cap_yi": 120.0, "quote_time": "20260710150000"}},
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "large_cap_observation_pool.py",
            "--repo-root",
            str(tmp_path),
            "--input",
            "candidates.csv",
            "--output",
            "observation.csv",
            "--summary",
            "observation.json",
            "--as-of-date",
            "2026-07-10",
        ],
    )

    assert observation_pool.main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["strong_observation_count"] == 1
    assert output["unresolved_candidate_row_count"] == 1
