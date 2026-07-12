from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

import large_cap_routing as routing


def _audit_row(
    code: str,
    name: str,
    *,
    observation_status: str = "强制审计",
    routing_status: str = "待路由审计",
) -> dict[str, str]:
    return {
        "代码": code,
        "标的": name,
        "市值快照日期": "2026-07-10",
        "快照时间": "15:00:00",
        "总市值(亿元)": "120.00",
        "市值来源": "新浪财经全市场市值清单",
        "市值状态": ">=100亿元",
        "观察状态": observation_status,
        "AI路由状态": routing_status,
        "边界复核": "否",
        "主层级": "待路由审计",
        "细分": "待路由审计",
        "来源网站": "新浪全市场市值清单",
        "来源条数": "0",
        "当前等级": "L0待路由",
        "第一变量": "先判定是否属于AI产业链，再确定第一变量",
        "样本角色": "全市场待路由审计",
        "下一步回源": "年报、公告、IR和产品页核对主营业务与AI关系",
        "证伪点": "主营业务与AI产业链无实质关系，标记为非AI并保留审计记录",
    }


def test_parse_sina_company_profile_extracts_business_and_company_type() -> None:
    html = """
    <table><tr><td>机构类型：</td><td>国有商业银行</td></tr></table>
    <div>公司简介：示例公司。主营业务：商业银行业务，提供全面的商业银行产品与服务。</div>
    """

    profile = routing.parse_sina_company_profile(html)

    assert profile == {
        "公司类型": "国有商业银行",
        "主营业务": "商业银行业务，提供全面的商业银行产品与服务。",
    }


def test_classify_route_marks_direct_ai_chain_business_as_related() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "研发、生产和销售半导体芯片、人工智能计算平台及服务器产品。",
        }
    )

    assert conclusion["路由结论"] == "AI产业链相关"
    assert conclusion["建议主层级"] == "计算芯片/整机系统"
    assert conclusion["当前等级"] == "L0"


def test_classify_route_marks_clear_non_ai_main_business_as_non_ai() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "国有商业银行",
            "主营业务": "商业银行业务，提供全面的商业银行产品与服务。",
        }
    )

    assert conclusion["路由结论"] == "非AI"
    assert conclusion["建议主层级"] == "非AI"


def test_classify_route_does_not_treat_incidental_information_wording_as_ai_business() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "茅台酒产品的生产与销售，食品、包装材料的生产与销售，信息产业相关产品的研制和开发。",
        }
    )

    assert conclusion["路由结论"] == "非AI"
    assert conclusion["建议细分"] == "食品饮料"


def test_classify_route_keeps_generic_materials_in_information_insufficient() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "生产和销售化工材料及工业气体。",
        }
    )

    assert conclusion["路由结论"] == "信息不足"
    assert "年报" in conclusion["下一步动作"]


def test_classify_route_does_not_treat_photovoltaic_silicon_wafers_as_ai_chip_materials() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "单晶硅棒、硅片、电池和组件的研发、生产和销售，为光伏电站提供产品和系统解决方案。",
        }
    )

    assert conclusion["路由结论"] == "信息不足"


def test_classify_route_places_integrated_circuit_equipment_in_semiconductor_equipment_layer() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "集成电路专用设备的研发、生产和销售。",
        }
    )

    assert conclusion["路由结论"] == "AI产业链相关"
    assert conclusion["建议主层级"] == "芯片制造与材料"


def test_classify_route_places_optical_passive_components_in_high_speed_interconnect() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "光无源器件的研发设计、高精密制造与销售业务。",
        }
    )

    assert conclusion["路由结论"] == "AI产业链相关"
    assert conclusion["建议主层级"] == "高速互联"


def test_classify_route_places_optical_chips_in_high_speed_interconnect() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "光芯片的研发、设计、生产与销售。",
        }
    )

    assert conclusion["路由结论"] == "AI产业链相关"
    assert conclusion["建议主层级"] == "高速互联"


def test_classify_route_places_electronic_copper_foil_in_high_speed_materials() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "高精度电子铜箔的研发、制造和销售。",
        }
    )

    assert conclusion["路由结论"] == "AI产业链相关"
    assert conclusion["建议主层级"] == "高速互联"


def test_classify_route_keeps_quantum_communication_out_of_ai_high_speed_chain() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "量子通信产品的研发、生产、销售及技术服务，为光纤量子保密通信网络提供产品。",
        }
    )

    assert conclusion["路由结论"] == "信息不足"


def test_classify_route_marks_explicit_drug_business_as_non_ai() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "创新型药物的研究、开发、生产以及商业化。",
        }
    )

    assert conclusion["路由结论"] == "非AI"
    assert conclusion["建议细分"] == "制药与医药流通"


def test_classify_route_marks_explicit_energy_extraction_as_non_ai() -> None:
    conclusion = routing.classify_route(
        {
            "公司类型": "股份有限公司",
            "主营业务": "原油及天然气的勘探、开发、生产、输送和销售。",
        }
    )

    assert conclusion["路由结论"] == "非AI"
    assert conclusion["建议细分"] == "传统能源开采"


def test_build_routing_records_keeps_all_rows_and_never_silently_drops_unresolved() -> None:
    rows = [
        _audit_row("600001", "芯片样本"),
        _audit_row("600002", "银行样本"),
        _audit_row("600003", "材料样本"),
        _audit_row("600004", "既有AI样本", observation_status="强制观察", routing_status="已路由AI候选"),
    ]
    profiles = {
        "600001": {"公司类型": "股份有限公司", "主营业务": "半导体芯片和服务器产品研发销售。"},
        "600002": {"公司类型": "商业银行", "主营业务": "商业银行业务。"},
        "600003": {"公司类型": "股份有限公司", "主营业务": "生产和销售化工材料。"},
    }

    records = routing.build_routing_records(rows, profiles, as_of_date="2026-07-12")

    by_code = {record["代码"]: record for record in records}
    assert set(by_code) == {"600001", "600002", "600003", "600004"}
    assert by_code["600001"]["路由结论"] == "AI产业链相关"
    assert by_code["600002"]["路由结论"] == "非AI"
    assert by_code["600003"]["路由结论"] == "信息不足"
    assert by_code["600004"]["路由结论"] == "AI产业链相关"
    assert by_code["600003"]["审计状态"] == "待补证"


def test_load_profile_cache_reuses_saved_company_business_evidence(tmp_path: Path) -> None:
    cache_path = tmp_path / "routing-cache.csv"
    cached_row = _audit_row("600001", "芯片样本")
    cached_row.update(
        {
            "路由结论": "AI产业链相关",
            "审计状态": "已初筛",
            "建议主层级": "计算芯片/整机系统",
            "建议细分": "半导体芯片",
            "业务证据等级": "B",
            "业务证据来源": "http://example.test/600001",
            "业务证据抓取日期": "2026-07-12",
            "公司类型": "股份有限公司",
            "主营业务": "半导体芯片研发销售。",
            "判定理由": "示例",
            "下一步动作": "回源年报",
        }
    )
    with cache_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=routing.OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerow(cached_row)

    profiles = routing.load_profile_cache(cache_path)

    assert profiles == {
        "600001": {
            "公司类型": "股份有限公司",
            "主营业务": "半导体芯片研发销售。",
            "抓取状态": "已从快照复用",
            "证据链接": "http://example.test/600001",
        }
    }


def test_build_expanded_observation_records_promotes_routed_ai_and_keeps_boundary() -> None:
    rows = [
        _audit_row("600001", "新芯片样本"),
        _audit_row("600002", "新边界样本", observation_status="边界待路由"),
        _audit_row("600003", "非AI样本"),
        _audit_row("600004", "既有AI样本", observation_status="强制观察", routing_status="已路由AI候选"),
    ]
    profiles = {
        "600001": {"公司类型": "股份有限公司", "主营业务": "半导体芯片研发销售。"},
        "600002": {"公司类型": "股份有限公司", "主营业务": "光模块研发销售。"},
        "600003": {"公司类型": "商业银行", "主营业务": "商业银行业务。"},
    }
    routed = routing.build_routing_records(rows, profiles, as_of_date="2026-07-12")

    records = routing.build_expanded_observation_records(routed)

    by_code = {record["代码"]: record for record in records}
    assert set(by_code) == {"600001", "600002", "600004"}
    assert by_code["600001"]["观察状态"] == "强制观察"
    assert by_code["600001"]["主层级"] == "计算芯片/整机系统"
    assert by_code["600001"]["当前等级"] == "L0"
    assert by_code["600002"]["观察状态"] == "边界复核"
    assert by_code["600004"]["来源网站"] == "既有AI候选宇宙"


def test_main_writes_all_input_rows_with_summary(monkeypatch, tmp_path: Path) -> None:
    input_path = tmp_path / "market-audit.csv"
    with input_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=routing.INPUT_FIELDS)
        writer.writeheader()
        writer.writerow(_audit_row("600001", "芯片样本"))
        writer.writerow(_audit_row("600002", "银行样本"))

    monkeypatch.setattr(
        routing,
        "fetch_sina_company_profiles",
        lambda *_args, **_kwargs: {
            "600001": {"公司类型": "股份有限公司", "主营业务": "半导体芯片研发销售。"},
            "600002": {"公司类型": "商业银行", "主营业务": "商业银行业务。"},
        },
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "large_cap_routing.py",
            "--repo-root",
            str(tmp_path),
            "--input",
            "market-audit.csv",
            "--output",
            "market-routing.csv",
            "--summary",
            "market-routing.json",
            "--as-of-date",
            "2026-07-12",
        ],
    )

    assert routing.main() == 0

    with (tmp_path / "market-routing.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        records = list(csv.DictReader(handle))
    assert len(records) == 2
    assert {record["路由结论"] for record in records} == {"AI产业链相关", "非AI"}

    summary = json.loads((tmp_path / "market-routing.json").read_text(encoding="utf-8"))
    assert summary["input_row_count"] == 2
    assert summary["hard_pending_count"] == 2
    assert summary["unresolved_count"] == 0
