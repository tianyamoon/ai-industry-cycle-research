from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "build_weekly_stage.py"
MANIFEST_COLUMNS = [
    "kind", "name", "status", "wiki_path", "wiki_sync_status", "wiki_skip_reason",
    "score", "action", "has_industry_logic", "has_valuation_funds",
    "has_technical_structure", "has_score_reason", "has_evidence_source", "has_history",
    "has_next_trigger", "pending_reason", "sample_reason", "evidence_path",
    "sample_confidence", "confidence_reason", "is_a_qualified", "a_gap_reason",
    "has_global_anchor", "has_ashare_anchor", "has_elasticity_or_counterexample",
    "parent_topic", "sample_role", "blocker_type", "has_davis_path",
    "technical_source", "technical_tool", "technical_arguments",
    "technical_structured_ready", "technical_actual_source", "technical_fallback_used",
    "technical_confidence", "technical_warnings", "technical_cross_source_validated",
    "technical_cross_source_ok",
]
REGISTRY_COLUMNS = [
    "schema_version", "l4_id", "l1", "l2", "l3", "l4", "canonical_topic",
    "research_coordinate", "wiki_path",
]


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def make_registry_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index in range(1, 338):
        if index == 1:
            l1, l2, l3, topic = "芯片层", "存储链", "HBM", "AI产业链 - HBM"
        elif index == 2:
            l1, l2, l3, topic = "芯片层", "晶圆制造与工艺", "晶圆制造设备", "AI产业链 - 晶圆制造设备"
        elif index in {330, 331}:
            l1 = "全球映射" if index == 330 else "终端层"
            l2, l3, topic = "机器人", "人形机器人", "人形机器人"
        else:
            l1, l2, l3, topic = "测试层", "测试分支", f"细分{index:04d}", f"主题{index:04d}"
        rows.append(
            {
                "schema_version": "1",
                "l4_id": f"AI-L4-{index:04d}",
                "l1": l1,
                "l2": l2,
                "l3": l3,
                "l4": topic,
                "canonical_topic": topic,
                "research_coordinate": f"{l1} -> {l2} -> {l3}",
                "wiki_path": f"topics/{topic}.md",
            }
        )
    return rows


def baseline_topic(name: str, score: int = 50) -> dict[str, str]:
    return {
        "kind": "topic", "name": name, "status": "已评分",
        "wiki_path": f"topics/{name}.md", "wiki_sync_status": "无需同步",
        "wiki_skip_reason": "测试不写 Wiki", "score": str(score), "action": "减持",
        "has_industry_logic": "是", "has_valuation_funds": "是",
        "has_technical_structure": "是", "has_score_reason": "是",
        "has_evidence_source": "是", "has_history": "是", "has_next_trigger": "是",
        "pending_reason": "", "sample_reason": "测试样本", "evidence_path": "old.md",
        "sample_confidence": "B", "confidence_reason": "旧口径", "is_a_qualified": "否",
        "a_gap_reason": "技术待核", "has_global_anchor": "是", "has_ashare_anchor": "是",
        "has_elasticity_or_counterexample": "是", "parent_topic": name,
        "sample_role": "细分评分主体", "blocker_type": "技术待核", "has_davis_path": "是",
        "technical_source": "项目代理技术", "technical_tool": "旧脚本",
        "technical_arguments": "旧参数", "technical_structured_ready": "否",
        "technical_actual_source": "项目代理技术", "technical_fallback_used": "否",
        "technical_confidence": "low", "technical_warnings": "技术待核",
        "technical_cross_source_validated": "否", "technical_cross_source_ok": "否",
    }


def write_confidence_table(path: Path, registry_rows: list[dict[str, str]]) -> None:
    lines = [
        "# confidence",
        "| L1 | L2 | L3 | L4 | 当前可信度 | 产业逻辑证据 | 估值资金证据 | 戴维斯路径 | 技术结构证据 | 全球锚 | A股锚 | 弹性/反证 | 正式A门槛 | 阻塞类型 | 升级动作 | 最后审计周次 | 题材卡 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in registry_rows:
        lines.append(
            "| {l1} | {l2} | {l3} | {l4} | B | 一级来源待补 | 估值待补 | 已补 | 项目代理技术 | 全球锚 | A股锚 | 反证锚 | 未通过 | 技术直连未复核 | 补技术 | 2026-07-03 | {l4}.md |".format(**row)
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_builder(tmp_path: Path, output_name: str) -> tuple[subprocess.CompletedProcess[str], Path, Path, Path]:
    registry_rows = make_registry_rows()
    registry_path = tmp_path / "registry.csv"
    baseline_path = tmp_path / "baseline.csv"
    confidence_path = tmp_path / "confidence.md"
    delta_path = tmp_path / "deltas.json"
    output_dir = tmp_path / output_name
    write_csv(registry_path, REGISTRY_COLUMNS, registry_rows)
    baseline_rows = [baseline_topic(row["l4"]) for row in registry_rows]
    baseline_rows[0]["wiki_sync_status"] = "已同步"
    baseline_rows[0]["wiki_skip_reason"] = ""
    write_csv(baseline_path, MANIFEST_COLUMNS, baseline_rows)
    write_confidence_table(confidence_path, registry_rows)
    delta_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "as_of": "2026-07-13",
                "formal_A_technical_evidence_ready": False,
                "evidence_path": "evidence.md",
                "rules": [
                    {"match": {"l2": "存储链"}, "technical_delta": -2, "reason": "存储组级回撤"},
                    {
                        "match": {"l4_id": "AI-L4-0002"}, "evidence_delta": 3, "technical_delta": 3,
                        "reason": "设备局部补证",
                        "technical_override": {"technical_source": "Luna Stock MCP", "technical_cross_source_ok": "否"},
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    manifest_path = output_dir / "manifest.csv"
    report_path = output_dir / "report.md"
    audit_path = output_dir / "audit.md"
    result = subprocess.run(
        [
            sys.executable, str(SCRIPT_PATH), "--registry", str(registry_path),
            "--baseline-manifest", str(baseline_path), "--confidence-table", str(confidence_path),
            "--delta-config", str(delta_path), "--manifest-output", str(manifest_path),
            "--report-output", str(report_path), "--audit-output", str(audit_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result, manifest_path, report_path, audit_path


def test_stage_builder_generates_337_stable_topics_and_deterministic_outputs(tmp_path: Path) -> None:
    first, manifest_path, report_path, audit_path = run_builder(tmp_path, "first")
    assert first.returncode == 0, first.stdout + first.stderr
    first_manifest = manifest_path.read_bytes()
    first_report = report_path.read_bytes()
    first_audit = audit_path.read_bytes()

    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    topics = [row for row in rows if row["kind"] == "topic"]
    assert len(topics) == 337
    assert len({row["l4_id"] for row in topics}) == 337
    assert [row["l4_id"] for row in topics if row["name"] == "人形机器人"] == ["AI-L4-0330", "AI-L4-0331"]
    assert next(row for row in topics if row["l4_id"] == "AI-L4-0001")["score"] == "48"
    first_topic = next(row for row in topics if row["l4_id"] == "AI-L4-0001")
    assert first_topic["wiki_sync_status"] == "待同步"
    assert "未回写" in first_topic["wiki_skip_reason"]
    equipment = next(row for row in topics if row["l4_id"] == "AI-L4-0002")
    assert equipment["score"] == "56"
    assert equipment["action"] == "持有"
    assert equipment["technical_source"] == "Luna Stock MCP"
    assert equipment["technical_cross_source_ok"] == "否"
    assert "阶段基线" in report_path.read_text(encoding="utf-8")
    assert "正式 A 门槛" in report_path.read_text(encoding="utf-8")
    assert "A=0" in audit_path.read_text(encoding="utf-8")

    second, second_manifest, second_report, second_audit = run_builder(tmp_path, "second")
    assert second.returncode == 0, second.stdout + second.stderr
    assert first_manifest == second_manifest.read_bytes()
    assert first_report == second_report.read_bytes()
    assert first_audit == second_audit.read_bytes()
