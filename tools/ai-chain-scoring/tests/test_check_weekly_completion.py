from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_weekly_completion.py"
WEEK = "2026-07-03"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_mapping(project_root: Path, topic_name: str) -> None:
    content = f"""# mapping

| 规范主卡 | 类型 | 研究坐标 |
|---|---|---|
| {topic_name} | 细分 | 上游底层算力与芯片层 -> 计算芯片主链 -> GPU |
"""
    write_text(project_root / "00_总控台" / "trade-system题材主卡映射表.md", content)


def write_report(
    path: Path,
    formal_text: str = "已完成",
    explicit_confidence_terms: bool = False,
) -> None:
    formal_gate_heading = "正式 A 门槛" if explicit_confidence_terms else "正式A门槛"
    gap_heading = "样本可信度 A 缺口摘要" if explicit_confidence_terms else "A级缺口摘要"
    content = f"""# 报告

任务类型：`正式周更`
本次范围：`测试范围`
完成情况：`{formal_text}`

## 样本可信度分布

- `A / B / C`

## {formal_gate_heading}

- `formal 校验`

## {gap_heading}

- `待补`

## 覆盖矩阵

| L1 | L2 | L3 | L4 | 题材卡 | 个股样本 | 状态 | 待补原因 |
|---|---|---|---|---|---|---|---|
| 上游底层算力与芯片层 | 计算芯片主链 | GPU | AI产业链 - GPU | AI产业链 - GPU.md | 寒武纪 | 已评分 | - |

## 本周已评分细分

- `AI产业链 - GPU`

## 本周待补细分

- `无`

## 本周仅观察细分

- `无`

## 本周未纳入个股样本

- `无`

## 产业逻辑层

- `已写`

## 估值资金层

- `已写`

## 技术结构层

- `已写`

## 机器检查

- `待运行`

## 评分历史

- `{WEEK} | 测试`
"""
    write_text(path, content)


def write_topic_page(path: Path) -> None:
    content = f"""# 题材卡

## 本周评分

> 周次：`{WEEK}`
> 评分：`70/100`
> 动作评级：`持有`
> 样本可信度：`A`

## 评分历史

- `{WEEK} | 70/100 | 持有 | 测试`
"""
    write_text(path, content)


def write_stock_page(path: Path) -> None:
    content = f"""# 个股卡

## 本周个股评分

> 周次：`{WEEK}`
> 评分：`66/100`
> 动作评级：`持有`
> 角色：`A股承接锚`

## 评分历史

- `{WEEK} | 66/100 | 持有 | 测试`
"""
    write_text(path, content)


def base_topic_row(topic_path: Path, evidence_path: Path, topic_name: str = "AI产业链 - GPU") -> dict[str, str]:
    return {
        "kind": "topic",
        "name": topic_name,
        "status": "已评分",
        "wiki_path": str(topic_path),
        "wiki_sync_status": "已同步",
        "wiki_skip_reason": "",
        "score": "70",
        "action": "持有",
        "has_industry_logic": "是",
        "has_valuation_funds": "是",
        "has_technical_structure": "是",
        "has_score_reason": "是",
        "has_evidence_source": "是",
        "has_history": "是",
        "has_next_trigger": "是",
        "pending_reason": "",
        "sample_reason": "全球锚+A股承接锚+弹性/反证样本齐备",
        "evidence_path": str(evidence_path),
        "sample_confidence": "A",
        "confidence_reason": "",
        "is_a_qualified": "是",
        "a_gap_reason": "",
        "has_global_anchor": "是",
        "has_ashare_anchor": "是",
        "has_elasticity_or_counterexample": "是",
        "parent_topic": topic_name,
        "sample_role": "细分评分主体",
        "blocker_type": "",
        "has_davis_path": "是",
        "technical_source": "Luna Stock MCP",
        "technical_tool": "get_kline",
        "technical_arguments": "{\"symbol\":\"600519\",\"period\":\"weekly\",\"count\":60}",
        "technical_structured_ready": "是",
        "technical_actual_source": "thsdk",
        "technical_fallback_used": "否",
        "technical_confidence": "high",
        "technical_warnings": "无",
        "technical_cross_source_validated": "是",
        "technical_cross_source_ok": "是",
    }


def base_stock_row(stock_path: Path, evidence_path: Path, topic_name: str = "AI产业链 - GPU") -> dict[str, str]:
    return {
        "kind": "stock",
        "name": "寒武纪",
        "status": "已评分",
        "wiki_path": str(stock_path),
        "wiki_sync_status": "已同步",
        "wiki_skip_reason": "",
        "score": "66",
        "action": "持有",
        "has_industry_logic": "是",
        "has_valuation_funds": "是",
        "has_technical_structure": "是",
        "has_score_reason": "是",
        "has_evidence_source": "是",
        "has_history": "是",
        "has_next_trigger": "是",
        "pending_reason": "",
        "sample_reason": "来自 GPU 主题，当前充当 A股承接锚",
        "evidence_path": str(evidence_path),
        "sample_confidence": "A",
        "confidence_reason": "",
        "is_a_qualified": "是",
        "a_gap_reason": "",
        "has_global_anchor": "否",
        "has_ashare_anchor": "是",
        "has_elasticity_or_counterexample": "否",
        "parent_topic": topic_name,
        "sample_role": "A股承接锚",
        "blocker_type": "",
        "has_davis_path": "是",
        "technical_source": "Luna Stock MCP",
        "technical_tool": "get_stock_detail",
        "technical_arguments": "{\"symbol\":\"688256\"}",
        "technical_structured_ready": "是",
        "technical_actual_source": "thsdk",
        "technical_fallback_used": "否",
        "technical_confidence": "high",
        "technical_warnings": "无",
        "technical_cross_source_validated": "是",
        "technical_cross_source_ok": "是",
    }


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_checker(
    tmp_path: Path,
    mode: str,
    rows: list[dict[str, str]],
    formal_text: str = "已完成",
    explicit_confidence_terms: bool = False,
) -> subprocess.CompletedProcess[str]:
    project_root = tmp_path / "project"
    wiki_root = tmp_path / "wiki"
    report_path = project_root / "03_结果层" / "report.md"
    manifest_path = project_root / "03_结果层" / "manifest.csv"
    topic_path = wiki_root / "topics" / "AI产业链 - GPU.md"
    stock_path = wiki_root / "entities" / "stocks" / "寒武纪.md"

    write_mapping(project_root, "AI产业链 - GPU")
    write_report(
        report_path,
        formal_text=formal_text,
        explicit_confidence_terms=explicit_confidence_terms,
    )
    write_topic_page(topic_path)
    write_stock_page(stock_path)
    write_manifest(manifest_path, rows)

    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--mode",
            mode,
            "--coverage",
            "full",
            "--week",
            WEEK,
            "--report",
            str(report_path),
            "--manifest",
            str(manifest_path),
            "--project-root",
            str(project_root),
            "--wiki-root",
            str(wiki_root),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_formal_fails_when_topic_confidence_is_not_a(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    write_text(evidence_path, "# evidence")
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    topic_row = base_topic_row(topic_path, evidence_path)
    topic_row["sample_confidence"] = "B"
    topic_row["confidence_reason"] = "仍缺正式一级来源闭环"
    topic_row["is_a_qualified"] = "否"
    topic_row["a_gap_reason"] = "需补一级来源、戴维斯路径与技术直连"
    topic_row["blocker_type"] = "一级来源缺口；技术直连未复核"
    stock_row = base_stock_row(stock_path, evidence_path)
    result = run_checker(tmp_path, "formal", [topic_row, stock_row])
    assert result.returncode == 1
    assert "sample_confidence 必须为 A" in result.stdout


def test_stage_accepts_explicit_confidence_terms(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    write_text(evidence_path, "# evidence")
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    topic_row = base_topic_row(topic_path, evidence_path)
    stock_row = base_stock_row(stock_path, evidence_path)

    result = run_checker(
        tmp_path,
        "stage",
        [topic_row, stock_row],
        formal_text="未完成",
        explicit_confidence_terms=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_formal_fails_when_anchor_role_is_missing(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    write_text(evidence_path, "# evidence")
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    topic_row = base_topic_row(topic_path, evidence_path)
    topic_row["has_elasticity_or_counterexample"] = "否"
    topic_row["is_a_qualified"] = "否"
    topic_row["confidence_reason"] = "当前缺弹性/反证样本角色"
    topic_row["a_gap_reason"] = "补齐弹性/反证样本并复核技术源"
    topic_row["blocker_type"] = "样本角色缺口"
    stock_row = base_stock_row(stock_path, evidence_path)
    result = run_checker(tmp_path, "formal", [topic_row, stock_row])
    assert result.returncode == 1
    assert "缺弹性/反证样本" in result.stdout


def test_stock_row_missing_parent_topic_or_sample_role_fails(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    write_text(evidence_path, "# evidence")
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    topic_row = base_topic_row(topic_path, evidence_path)
    topic_row["is_a_qualified"] = "否"
    topic_row["confidence_reason"] = "当前作为阶段样本"
    topic_row["a_gap_reason"] = "技术直连待补"
    topic_row["blocker_type"] = "技术直连未复核"
    stock_row = base_stock_row(stock_path, evidence_path)
    stock_row["parent_topic"] = ""
    stock_row["sample_role"] = ""
    stock_row["sample_confidence"] = "C"
    stock_row["confidence_reason"] = "仅作观察样本"
    stock_row["is_a_qualified"] = "否"
    stock_row["a_gap_reason"] = "缺 parent_topic 与 sample_role"
    stock_row["blocker_type"] = "样本链路缺口"
    result = run_checker(tmp_path, "stage", [topic_row, stock_row], formal_text="未完成")
    assert result.returncode == 1
    assert "stock 行必须填写 parent_topic" in result.stdout
    assert "stock 行必须填写 sample_role" in result.stdout


def test_stage_fails_when_non_a_row_lacks_confidence_reason_or_blocker(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    write_text(evidence_path, "# evidence")
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    topic_row = base_topic_row(topic_path, evidence_path)
    topic_row["sample_confidence"] = "C"
    topic_row["is_a_qualified"] = "否"
    topic_row["a_gap_reason"] = ""
    topic_row["confidence_reason"] = ""
    topic_row["blocker_type"] = ""
    stock_row = base_stock_row(stock_path, evidence_path)
    result = run_checker(tmp_path, "stage", [topic_row, stock_row], formal_text="未完成")
    assert result.returncode == 1
    assert "必须填写 confidence_reason" in result.stdout
    assert "必须填写 blocker_type" in result.stdout


def test_formal_fails_when_luna_audit_fields_do_not_meet_a_threshold(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    write_text(evidence_path, "# evidence")
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    topic_row = base_topic_row(topic_path, evidence_path)
    topic_row["technical_fallback_used"] = "是"
    topic_row["technical_confidence"] = "medium"
    topic_row["technical_warnings"] = "fallback triggered"
    topic_row["technical_cross_source_validated"] = "否"
    topic_row["technical_cross_source_ok"] = "否"
    stock_row = base_stock_row(stock_path, evidence_path)
    result = run_checker(tmp_path, "formal", [topic_row, stock_row])
    assert result.returncode == 1
    assert "technical_fallback_used 必须为 否" in result.stdout
    assert "technical_confidence 必须达到高可信" in result.stdout
    assert "technical_cross_source_ok 必须为 是" in result.stdout


def test_relative_paths_work_when_called_outside_the_repository(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    wiki_root = tmp_path / "wiki"
    outside_cwd = tmp_path / "outside"
    outside_cwd.mkdir()
    report_path = project_root / "03_结果层" / "report.md"
    manifest_path = project_root / "03_结果层" / "manifest.csv"
    evidence_path = project_root / "03_结果层" / "source.md"
    topic_path = wiki_root / "topics" / "AI产业链 - GPU.md"
    stock_path = wiki_root / "entities" / "stocks" / "寒武纪.md"

    write_mapping(project_root, "AI产业链 - GPU")
    write_report(report_path, formal_text="未完成")
    write_text(evidence_path, "# evidence")
    write_topic_page(topic_path)
    write_stock_page(stock_path)
    topic_row = base_topic_row(topic_path, evidence_path)
    stock_row = base_stock_row(stock_path, evidence_path)
    topic_row["wiki_path"] = "topics/AI产业链 - GPU.md"
    stock_row["wiki_path"] = "entities/stocks/寒武纪.md"
    topic_row["evidence_path"] = "03_结果层/source.md"
    stock_row["evidence_path"] = "03_结果层/source.md"
    write_manifest(manifest_path, [topic_row, stock_row])

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--mode",
            "stage",
            "--coverage",
            "full",
            "--week",
            WEEK,
            "--report",
            "03_结果层/report.md",
            "--manifest",
            "03_结果层/manifest.csv",
            "--project-root",
            str(project_root),
            "--wiki-root",
            str(wiki_root),
        ],
        cwd=outside_cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_stage_allows_explicit_wiki_skip_when_no_canonical_page(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    write_text(evidence_path, "# evidence")
    topic_row = base_topic_row(
        tmp_path / "wiki" / "topics" / "missing-topic.md",
        evidence_path,
    )
    stock_row = base_stock_row(
        tmp_path / "wiki" / "entities" / "stocks" / "missing-stock.md",
        evidence_path,
    )
    for row in (topic_row, stock_row):
        row["wiki_sync_status"] = "无需同步"
        row["wiki_skip_reason"] = "AI 仓状态表已覆盖；Wiki 无现有 canonical 页面"

    result = run_checker(tmp_path, "stage", [topic_row, stock_row], formal_text="未完成")

    assert result.returncode == 0, result.stdout + result.stderr


def test_wiki_skip_requires_a_reason(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    write_text(evidence_path, "# evidence")
    topic_row = base_topic_row(
        tmp_path / "wiki" / "topics" / "missing-topic.md",
        evidence_path,
    )
    stock_row = base_stock_row(
        tmp_path / "wiki" / "entities" / "stocks" / "missing-stock.md",
        evidence_path,
    )
    topic_row["wiki_sync_status"] = "无需同步"
    topic_row["wiki_skip_reason"] = ""
    stock_row["wiki_sync_status"] = "无需同步"
    stock_row["wiki_skip_reason"] = "AI 仓状态表已覆盖；Wiki 无现有 canonical 页面"

    result = run_checker(tmp_path, "stage", [topic_row, stock_row], formal_text="未完成")

    assert result.returncode == 1
    assert "wiki_skip_reason" in result.stdout


def test_formal_rejects_pending_wiki_sync(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    write_text(evidence_path, "# evidence")
    topic_row = base_topic_row(
        tmp_path / "wiki" / "topics" / "missing-topic.md",
        evidence_path,
    )
    stock_row = base_stock_row(
        tmp_path / "wiki" / "entities" / "stocks" / "missing-stock.md",
        evidence_path,
    )
    for row in (topic_row, stock_row):
        row["wiki_sync_status"] = "待同步"
        row["wiki_skip_reason"] = "等待人工建立 canonical 页面"

    result = run_checker(tmp_path, "formal", [topic_row, stock_row])

    assert result.returncode == 1
    assert "formal 模式不允许 wiki_sync_status=待同步" in result.stdout
