from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check_weekly_completion.py"
WEEK = "2026-07-03"
REGISTRY_COLUMNS = [
    "schema_version",
    "l4_id",
    "l1",
    "l2",
    "l3",
    "l4",
    "canonical_topic",
    "research_coordinate",
    "wiki_path",
]


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
动作评级：`持有`

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


def base_topic_row(
    topic_path: Path,
    evidence_path: Path,
    topic_name: str = "AI产业链 - GPU",
    l4_id: str = "AI-L4-0001",
) -> dict[str, str]:
    return {
        "schema_version": "1",
        "l4_id": l4_id,
        "l1": "上游底层算力与芯片层",
        "l2": "计算芯片主链",
        "l3": "GPU",
        "l4": topic_name,
        "canonical_topic": topic_name,
        "sample_id": "",
        "parent_l4_id": "",
        "market": "",
        "ticker": "",
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


def base_stock_row(
    stock_path: Path,
    evidence_path: Path,
    topic_name: str = "AI产业链 - GPU",
    parent_l4_id: str = "AI-L4-0001",
) -> dict[str, str]:
    return {
        "schema_version": "1",
        "l4_id": "",
        "l1": "上游底层算力与芯片层",
        "l2": "计算芯片主链",
        "l3": "GPU",
        "l4": topic_name,
        "canonical_topic": topic_name,
        "sample_id": "CN-A-688256",
        "parent_l4_id": parent_l4_id,
        "market": "A股",
        "ticker": "688256",
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


def write_registry(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTRY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def full_registry_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index in range(1, 338):
        if index == 1:
            canonical_topic = "AI产业链 - GPU"
            l1 = "上游底层算力与芯片层"
            l2 = "计算芯片主链"
            l3 = "GPU"
        elif index in {330, 331}:
            canonical_topic = "人形机器人"
            l1 = "全球映射与海外变量传导层" if index == 330 else "终端、机器人与具身智能层"
            l2 = "海外终端与具身主链" if index == 330 else "机器人链"
            l3 = "人形机器人"
        else:
            canonical_topic = f"AI产业链 - 测试细分 {index:04d}"
            l1 = "终端、机器人与具身智能层"
            l2 = "机器人链"
            l3 = f"测试细分 {index:04d}"
        rows.append(
            {
                "schema_version": "1",
                "l4_id": f"AI-L4-{index:04d}",
                "l1": l1,
                "l2": l2,
                "l3": l3,
                "l4": canonical_topic,
                "canonical_topic": canonical_topic,
                "research_coordinate": f"{l1} -> {l2} -> {l3}",
                "wiki_path": f"topics/{canonical_topic}.md",
            }
        )
    return rows


def topic_rows_from_registry(
    registry_rows: list[dict[str, str]],
    topic_path: Path,
    evidence_path: Path,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for registry_row in registry_rows:
        row = base_topic_row(
            topic_path,
            evidence_path,
            registry_row["canonical_topic"],
            registry_row["l4_id"],
        )
        for column in ("schema_version", "l1", "l2", "l3", "l4", "canonical_topic"):
            row[column] = registry_row[column]
        rows.append(row)
    return rows


def run_checker(
    tmp_path: Path,
    mode: str,
    rows: list[dict[str, str]],
    formal_text: str = "已完成",
    explicit_confidence_terms: bool = False,
    coverage: str = "scoped",
    registry_rows: list[dict[str, str]] | None = None,
    min_stock_rows: int = 1,
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
    if registry_rows is not None:
        write_registry(project_root / "00_总控台" / "AI产业链L4注册表.csv", registry_rows)

    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--mode",
            mode,
            "--coverage",
            coverage,
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
            "--min-stock-rows",
            str(min_stock_rows),
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
            "scoped",
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


def test_full_accepts_two_ids_with_the_same_canonical_topic(tmp_path: Path) -> None:
    registry_rows = full_registry_rows()
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    write_text(evidence_path, "# evidence")
    topic_rows = topic_rows_from_registry(registry_rows, topic_path, evidence_path)
    stock_row = base_stock_row(stock_path, evidence_path, parent_l4_id="AI-L4-0001")

    result = run_checker(
        tmp_path,
        "stage",
        [*topic_rows, stock_row],
        formal_text="未完成",
        coverage="full",
        registry_rows=registry_rows,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_full_fails_when_registry_does_not_have_337_rows(tmp_path: Path) -> None:
    registry_rows = full_registry_rows()[:-1]
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    write_text(evidence_path, "# evidence")
    topic_rows = topic_rows_from_registry(registry_rows, topic_path, evidence_path)
    stock_row = base_stock_row(stock_path, evidence_path, parent_l4_id="AI-L4-0001")

    result = run_checker(
        tmp_path,
        "stage",
        [*topic_rows, stock_row],
        formal_text="未完成",
        coverage="full",
        registry_rows=registry_rows,
    )

    assert result.returncode == 1
    assert "L4 注册表必须恰好包含 337 行" in result.stdout


def test_full_fails_when_registry_l4_id_is_duplicated(tmp_path: Path) -> None:
    registry_rows = full_registry_rows()
    registry_rows[-1]["l4_id"] = registry_rows[0]["l4_id"]
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    write_text(evidence_path, "# evidence")
    topic_rows = topic_rows_from_registry(registry_rows, topic_path, evidence_path)
    stock_row = base_stock_row(stock_path, evidence_path, parent_l4_id="AI-L4-0001")

    result = run_checker(
        tmp_path,
        "stage",
        [*topic_rows, stock_row],
        formal_text="未完成",
        coverage="full",
        registry_rows=registry_rows,
    )

    assert result.returncode == 1
    assert "L4 注册表 l4_id 必须唯一" in result.stdout


def test_full_fails_when_topic_l4_id_is_missing(tmp_path: Path) -> None:
    registry_rows = full_registry_rows()
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    write_text(evidence_path, "# evidence")
    topic_rows = topic_rows_from_registry(registry_rows, topic_path, evidence_path)[:-1]
    stock_row = base_stock_row(stock_path, evidence_path, parent_l4_id="AI-L4-0001")

    result = run_checker(
        tmp_path,
        "stage",
        [*topic_rows, stock_row],
        formal_text="未完成",
        coverage="full",
        registry_rows=registry_rows,
    )

    assert result.returncode == 1
    assert "full 覆盖缺少 l4_id: AI-L4-0337" in result.stdout


def test_full_fails_when_topic_l4_id_is_duplicated(tmp_path: Path) -> None:
    registry_rows = full_registry_rows()
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    write_text(evidence_path, "# evidence")
    topic_rows = topic_rows_from_registry(registry_rows, topic_path, evidence_path)
    topic_rows[-1]["l4_id"] = topic_rows[0]["l4_id"]
    stock_row = base_stock_row(stock_path, evidence_path, parent_l4_id="AI-L4-0001")

    result = run_checker(
        tmp_path,
        "stage",
        [*topic_rows, stock_row],
        formal_text="未完成",
        coverage="full",
        registry_rows=registry_rows,
    )

    assert result.returncode == 1
    assert "topic l4_id 重复: AI-L4-0001" in result.stdout


def test_full_fails_when_topic_l4_id_is_unknown(tmp_path: Path) -> None:
    registry_rows = full_registry_rows()
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    write_text(evidence_path, "# evidence")
    topic_rows = topic_rows_from_registry(registry_rows, topic_path, evidence_path)
    topic_rows[-1]["l4_id"] = "AI-L4-9999"
    stock_row = base_stock_row(stock_path, evidence_path, parent_l4_id="AI-L4-0001")

    result = run_checker(
        tmp_path,
        "stage",
        [*topic_rows, stock_row],
        formal_text="未完成",
        coverage="full",
        registry_rows=registry_rows,
    )

    assert result.returncode == 1
    assert "topic 含未知 l4_id: AI-L4-9999" in result.stdout


def test_full_fails_when_stock_parent_l4_id_is_unknown(tmp_path: Path) -> None:
    registry_rows = full_registry_rows()
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    write_text(evidence_path, "# evidence")
    topic_rows = topic_rows_from_registry(registry_rows, topic_path, evidence_path)
    stock_row = base_stock_row(stock_path, evidence_path, parent_l4_id="AI-L4-9999")

    result = run_checker(
        tmp_path,
        "stage",
        [*topic_rows, stock_row],
        formal_text="未完成",
        coverage="full",
        registry_rows=registry_rows,
    )

    assert result.returncode == 1
    assert "stock parent_l4_id 不在 L4 注册表中: AI-L4-9999" in result.stdout


def test_formal_fails_when_topic_has_no_stock_roles(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    write_text(evidence_path, "# evidence")
    topic_row = base_topic_row(topic_path, evidence_path)

    result = run_checker(
        tmp_path,
        "formal",
        [topic_row],
        min_stock_rows=0,
    )

    assert result.returncode == 1
    assert "parent_l4_id 关联的 stock 样本角色不完整" in result.stdout


def test_formal_aggregates_stock_roles_by_parent_l4_id(tmp_path: Path) -> None:
    evidence_path = tmp_path / "project" / "03_结果层" / "source.md"
    topic_path = tmp_path / "wiki" / "topics" / "AI产业链 - GPU.md"
    stock_path = tmp_path / "wiki" / "entities" / "stocks" / "寒武纪.md"
    write_text(evidence_path, "# evidence")
    first_topic = base_topic_row(topic_path, evidence_path, "人形机器人", "AI-L4-0001")
    second_topic = base_topic_row(topic_path, evidence_path, "人形机器人", "AI-L4-0002")
    stock_rows: list[dict[str, str]] = []
    for index, role in enumerate(("全球锚", "A股承接锚", "弹性/反证样本"), start=1):
        row = base_stock_row(stock_path, evidence_path, "人形机器人", "AI-L4-0001")
        row["name"] = f"测试样本{index}"
        row["sample_id"] = f"SAMPLE-{index:04d}"
        row["sample_role"] = role
        stock_rows.append(row)

    result = run_checker(
        tmp_path,
        "formal",
        [first_topic, second_topic, *stock_rows],
    )

    assert result.returncode == 1
    assert "AI-L4-0002" in result.stdout
    assert "parent_l4_id 关联的 stock 样本角色不完整" in result.stdout
