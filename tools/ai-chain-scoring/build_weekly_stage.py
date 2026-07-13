from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from path_config import RootResolutionError, resolve_configured_root


SCHEMA_VERSION = "1"
REGISTRY_COLUMNS = [
    "schema_version", "l4_id", "l1", "l2", "l3", "l4", "canonical_topic",
    "research_coordinate", "wiki_path",
]
LEGACY_COLUMNS = [
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
MANIFEST_COLUMNS = [
    "schema_version", "l4_id", "l1", "l2", "l3", "l4", "canonical_topic",
    "sample_id", "parent_l4_id", "market", "ticker", *LEGACY_COLUMNS,
]


def normalize(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().strip("`").replace("／", "/"))


def coordinate(row: dict[str, str]) -> str:
    return " -> ".join(normalize(row.get(key)) for key in ("l1", "l2", "l3"))


def read_csv(path: Path, required_columns: list[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV 没有表头: {path}")
        missing = [name for name in required_columns if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV 缺少列 {', '.join(missing)}: {path}")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def parse_markdown_tables(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    index = 0
    while index + 1 < len(lines):
        header_line = lines[index].strip()
        separator = lines[index + 1].strip()
        if not (header_line.startswith("|") and header_line.endswith("|")):
            index += 1
            continue
        if not re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", separator):
            index += 1
            continue
        headers = [cell.strip() for cell in header_line.strip("|").split("|")]
        index += 2
        while index < len(lines):
            line = lines[index].strip()
            if not (line.startswith("|") and line.endswith("|")):
                break
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            cells.extend([""] * (len(headers) - len(cells)))
            rows.append(dict(zip(headers, cells)))
            index += 1
    return rows


def load_confidence_rows(path: Path) -> dict[str, dict[str, str]]:
    rows = parse_markdown_tables(path)
    required = {"L1", "L2", "L3", "L4", "当前可信度", "阻塞类型", "升级动作"}
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        if not required.issubset(row):
            continue
        key = " -> ".join(normalize(row.get(name)) for name in ("L1", "L2", "L3"))
        if not key.strip(" ->"):
            continue
        if key in result:
            raise ValueError(f"可信度表研究坐标重复: {key}")
        result[key] = {key: normalize(value) for key, value in row.items()}
    if not result:
        raise ValueError(f"未在可信度表找到 L4 台账: {path}")
    return result


def truthy(value: str) -> str:
    return "是" if normalize(value) in {"是", "已补", "通过", "A"} else "否"


def score_action(score: int) -> str:
    if score >= 55:
        return "持有"
    if score >= 40:
        return "减持"
    return "卖出"


def matches(rule: dict[str, object], registry_row: dict[str, str]) -> bool:
    match = rule.get("match", {})
    if not isinstance(match, dict):
        raise ValueError("增量规则 match 必须是对象")
    return all(normalize(registry_row.get(str(key))) == normalize(str(value)) for key, value in match.items())


def apply_deltas(registry_row: dict[str, str], rules: list[dict[str, object]]) -> tuple[int, int, int, list[str]]:
    evidence_delta = valuation_delta = technical_delta = 0
    reasons: list[str] = []
    for rule in rules:
        if not matches(rule, registry_row):
            continue
        evidence_delta += int(rule.get("evidence_delta", 0))
        valuation_delta += int(rule.get("valuation_funds_delta", 0))
        technical_delta += int(rule.get("technical_delta", 0))
        reason = normalize(str(rule.get("reason", "")))
        if reason:
            reasons.append(reason)
    return evidence_delta, valuation_delta, technical_delta, reasons


def apply_technical_overrides(
    row: dict[str, str], registry_row: dict[str, str], rules: list[dict[str, object]]
) -> None:
    for rule in rules:
        if not matches(rule, registry_row):
            continue
        override = rule.get("technical_override", {})
        if not isinstance(override, dict):
            raise ValueError("technical_override 必须是对象")
        for key, value in override.items():
            if key.startswith("technical_"):
                row[key] = str(value)


def baseline_topics(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if normalize(row.get("kind")) == "topic":
            grouped[normalize(row.get("name"))].append(row)
    return grouped


def default_technical(row: dict[str, str]) -> None:
    values = {
        "technical_source": "项目代理技术",
        "technical_tool": "项目代理技术",
        "technical_arguments": "既有评分基线技术段落",
        "technical_structured_ready": "否",
        "technical_actual_source": "项目代理技术",
        "technical_fallback_used": "否",
        "technical_confidence": "low",
        "technical_warnings": "技术直连未复核",
        "technical_cross_source_validated": "否",
        "technical_cross_source_ok": "否",
    }
    for key, value in values.items():
        if not normalize(row.get(key)):
            row[key] = value


def defer_existing_wiki_sync(row: dict[str, str]) -> None:
    if normalize(row.get("wiki_sync_status")) != "已同步":
        return
    row["wiki_sync_status"] = "待同步"
    row["wiki_skip_reason"] = "本轮 AI 研究仓已生成评分，canonical Wiki 尚未回写本周评分与评分历史。"


def confidence_fields(confidence: dict[str, str], registry_row: dict[str, str]) -> dict[str, str]:
    current = normalize(confidence.get("当前可信度")) or "C"
    industry = normalize(confidence.get("产业逻辑证据"))
    valuation = normalize(confidence.get("估值资金证据"))
    technical = normalize(confidence.get("技术结构证据"))
    blocker = normalize(confidence.get("阻塞类型"))
    upgrade = normalize(confidence.get("升级动作"))
    formal = normalize(confidence.get("正式A门槛")) == "通过"
    return {
        "sample_confidence": current,
        "confidence_reason": f"升级总表：产业逻辑={industry}；估值资金={valuation}；技术={technical}。",
        "is_a_qualified": "是" if formal else "否",
        "a_gap_reason": "已通过当前升级总表正式 A 门槛。" if formal else f"{blocker}；升级动作：{upgrade}",
        "blocker_type": blocker if not formal else "无",
        "has_global_anchor": truthy(confidence.get("全球锚", "")),
        "has_ashare_anchor": truthy(confidence.get("A股锚", "")),
        "has_elasticity_or_counterexample": truthy(confidence.get("弹性/反证", "")),
        "has_davis_path": truthy(confidence.get("戴维斯路径", "")),
        "sample_reason": "全球锚={0}；A股承接锚={1}；弹性/反证样本={2}。".format(
            normalize(confidence.get("全球锚")),
            normalize(confidence.get("A股锚")),
            normalize(confidence.get("弹性/反证")),
        ),
    }


def build_rows(
    registry_rows: list[dict[str, str]],
    baseline_rows: list[dict[str, str]],
    confidence_by_coordinate: dict[str, dict[str, str]],
    config: dict[str, object],
) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    rules = config.get("rules", [])
    if not isinstance(rules, list):
        raise ValueError("delta 配置 rules 必须是数组")
    topic_queues = baseline_topics(baseline_rows)
    rows: list[dict[str, str]] = []
    changes: list[dict[str, object]] = []
    registry_by_id = {row["l4_id"]: row for row in registry_rows}
    ids_by_topic: dict[str, list[str]] = defaultdict(list)

    for registry_row in registry_rows:
        topic = normalize(registry_row.get("canonical_topic"))
        queue = topic_queues.get(topic, [])
        if not queue:
            raise ValueError(f"旧基线缺少 topic: {topic}")
        base = queue.pop(0).copy()
        confidence = confidence_by_coordinate.get(coordinate(registry_row))
        if confidence is None:
            raise ValueError(f"可信度总表缺少坐标: {coordinate(registry_row)}")
        evidence_delta, valuation_delta, technical_delta, reasons = apply_deltas(registry_row, rules)
        base_score = int(float(base.get("score") or 0))
        score = max(0, min(100, base_score + evidence_delta + valuation_delta + technical_delta))
        row = {key: "" for key in MANIFEST_COLUMNS}
        row.update(base)
        row.update({
            "schema_version": SCHEMA_VERSION,
            "l4_id": registry_row["l4_id"],
            "l1": registry_row["l1"],
            "l2": registry_row["l2"],
            "l3": registry_row["l3"],
            "l4": registry_row["l4"],
            "canonical_topic": registry_row["canonical_topic"],
            "sample_id": "",
            "parent_l4_id": "",
            "market": "",
            "ticker": "",
            "name": registry_row["canonical_topic"],
            "parent_topic": registry_row["canonical_topic"],
            "score": str(score),
            "action": score_action(score),
            "evidence_path": str(config.get("evidence_path", "")),
            "pending_reason": "本轮行情跨源可比较源不足，仅作为阶段技术与资金代理。",
        })
        row.update(confidence_fields(confidence, registry_row))
        apply_technical_overrides(row, registry_row, rules)
        default_technical(row)
        defer_existing_wiki_sync(row)
        rows.append(row)
        ids_by_topic[topic].append(registry_row["l4_id"])
        if score != base_score:
            changes.append({
                "l4_id": registry_row["l4_id"], "name": registry_row["canonical_topic"],
                "before": base_score, "after": score, "evidence_delta": evidence_delta,
                "valuation_delta": valuation_delta, "technical_delta": technical_delta,
                "reason": "；".join(reasons),
            })

    if any(queue for queue in topic_queues.values()):
        unexpected = [name for name, queue in topic_queues.items() if queue]
        raise ValueError("旧基线存在未映射 topic: " + "、".join(unexpected[:20]))

    overrides = config.get("stock_overrides", [])
    if not isinstance(overrides, list):
        raise ValueError("delta 配置 stock_overrides 必须是数组")
    overrides_by_name = {normalize(str(item.get("name", ""))): item for item in overrides if isinstance(item, dict)}
    stock_counters: Counter[str] = Counter()
    for base in baseline_rows:
        if normalize(base.get("kind")) != "stock":
            continue
        parent_topic = normalize(base.get("parent_topic"))
        parent_ids = ids_by_topic.get(parent_topic)
        if not parent_ids:
            raise ValueError(f"旧基线 stock 找不到父 topic: {parent_topic}")
        override = overrides_by_name.get(normalize(base.get("name")), {})
        parent_l4_id = normalize(str(override.get("parent_l4_id", parent_ids[0])))
        if parent_l4_id not in registry_by_id:
            raise ValueError(f"stock override 指向未知 parent_l4_id: {parent_l4_id}")
        parent = registry_by_id[parent_l4_id]
        stock_counters[parent_l4_id] += 1
        row = {key: "" for key in MANIFEST_COLUMNS}
        row.update(base)
        row.update({
            "schema_version": SCHEMA_VERSION,
            "l4_id": "",
            "l1": parent["l1"], "l2": parent["l2"], "l3": parent["l3"],
            "l4": parent["l4"], "canonical_topic": parent["canonical_topic"],
            "sample_id": f"{parent_l4_id}-S-{stock_counters[parent_l4_id]:03d}",
            "parent_l4_id": parent_l4_id,
            "market": normalize(base.get("market")),
            "ticker": normalize(base.get("ticker")),
            "parent_topic": parent["canonical_topic"],
            "evidence_path": str(config.get("evidence_path", "")),
            "pending_reason": "本轮未新增逐股跨源技术复核，沿用基线并保持阶段口径。",
        })
        if override:
            for key in ("score", "sample_role", "action", "sample_reason", "blocker_type"):
                if key in override:
                    row[key] = str(override[key])
            if "score" in override and "action" not in override:
                row["action"] = score_action(int(override["score"]))
        default_technical(row)
        defer_existing_wiki_sync(row)
        rows.append(row)
    return rows, changes


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def summarize(rows: list[dict[str, str]], field: str) -> list[list[object]]:
    topics = [row for row in rows if row["kind"] == "topic"]
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in topics:
        groups[row[field]].append(row)
    result: list[list[object]] = []
    for key in sorted(groups):
        group = groups[key]
        average = sum(int(row["score"]) for row in group) / len(group)
        confidence = Counter(row["sample_confidence"] for row in group)
        result.append([key, len(group), f"{average:.1f}", "/".join(f"{name}{count}" for name, count in sorted(confidence.items()))])
    return result


def write_report(path: Path, rows: list[dict[str, str]], changes: list[dict[str, object]], config: dict[str, object]) -> None:
    topics = [row for row in rows if row["kind"] == "topic"]
    stocks = [row for row in rows if row["kind"] == "stock"]
    confidence_counts = Counter(row["sample_confidence"] for row in topics)
    formal_ready = sum(row["is_a_qualified"] == "是" for row in topics)
    changed_rows = [
        [item["l4_id"], item["name"], item["before"], item["after"],
         f"{item['evidence_delta']:+d}/{item['valuation_delta']:+d}/{item['technical_delta']:+d}", item["reason"]]
        for item in changes
    ]
    as_of = str(config.get("as_of", ""))
    content = f"""任务类型：`阶段基线`
本次范围：`337 个 L4、396 个既有样本；截至 {as_of} 的行情、消息与公告增量`
完成情况：`已完成阶段基线；formal FAIL，未形成正式周更`

# AI产业链周评分_{as_of}_阶段基线

## 一句话结论

截至 `{as_of}`，AI 链并非同步上行：服务器与先进封装仍有相对强度，存储、高速互联、供配电与液冷进入退潮/高位审计；晶圆制造设备承接 `2026-07-08` 局部补证上修。行情跨源均为“可比较源不足”，因此本轮只调整阶段评分，不升级正式 A。

## 样本可信度分布

`A={confidence_counts.get('A', 0)} / B={confidence_counts.get('B', 0)} / C={confidence_counts.get('C', 0)}`。

## 正式 A 门槛

当前升级总表满足正式 A 的 L4 为 `{formal_ready}/337`；本轮 12 个行情组的 cross-source 均为 `insufficient_sources`，不能成为新增正式 A 技术证据。

## 样本可信度 A 缺口摘要

`333` 个非 A L4 仍以一级来源/连续变量、估值资金连续口径、技术直连与三类样本角色为主要阻塞；本轮只把阻塞显式保留，不以行情反弹替代经营验证。

## L1 汇总

{markdown_table(['L1', 'L4数', '平均分', '可信度分布'], summarize(rows, 'l1'))}

## L2 汇总

{markdown_table(['L2', 'L4数', '平均分', '可信度分布'], summarize(rows, 'l2'))}

## 覆盖矩阵

| 项目 | 数值 | 口径 |
|---|---:|---|
| 注册表 L4 | 337 | `l4_id` 与研究坐标均唯一 |
| 评分 topic | {len(topics)} | 全量覆盖，无按名称坍缩 |
| 既有样本 stock | {len(stocks)} | 样本以 `sample_id / parent_l4_id` 关联 |
| formal A | {formal_ready} | 不因本轮行情而新增 |

## 本周有变化的细分

{markdown_table(['L4_ID', '细分', '旧分', '新分', '产业/估值/技术', '变化理由'], changed_rows)}

## 产业逻辑层

- `服务器`：紫光股份 2026H1 业绩预告于 7 月 11 日披露，扣非仍高增，支持智算/国产化需求与毛利改善的方向性验证；收购结构与非经常收益限制加分幅度。
- `晶圆制造设备`：延续 7 月 8 日的样本锚点纠偏与经营兑现审计，`58 -> 64`；不扩散为整个制造材料链的无差别加分。
- 7 月 13 日盘后、官方披露日为 7 月 14 日的 PCB/CCL、光通信与存储业绩预告仅列入下轮待核，未提前进入本轮经营加分。

## 估值资金层

- 先进封装仍强但拥挤，评分仅反映阶段强度，动作不升级为追涨。
- 存储、高速互联、供配电和液冷的回撤属于估值/资金审计信号，不等同产业长期逻辑被证伪。
- PCB/CCL 是本轮外部行情参照，但当前注册表无对应 L4，已记为覆盖缺口，不伪造评分映射。

## 技术结构层

- 代表组行情截止 `{as_of}`；所有 12 组 `validate_cross_source` 均为 `insufficient_sources`，本轮技术层只能服务 stage。
- 服务器、先进封装为相对强度；存储、供配电、液冷与高速互联为减分方向；IDC 与应用维持观察。

## 机器检查

- 完成清单：本目录 `AI产业链周评分_{as_of}_完成清单.csv`
- stage/full：由同批次机器检查文件记录实际结果。
- formal/full：预期失败，失败原因以非 A L4、技术跨源不足与 Wiki 待同步状态为准。

## 评分历史

- `2026-07-03 | 全量阶段基线 | 旧评分基线`
- `2026-07-08 | 晶圆制造设备 | 58 -> 64 | 局部补证`
- `{as_of} | 全量阶段重评分 | 仅按可追溯增量调整；formal FAIL`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_audit(path: Path, rows: list[dict[str, str]], config: dict[str, object]) -> None:
    topics = [row for row in rows if row["kind"] == "topic"]
    counts = Counter(row["sample_confidence"] for row in topics)
    blockers = Counter(row["blocker_type"] for row in topics if row["sample_confidence"] != "A")
    formal_ready = sum(row["is_a_qualified"] == "是" for row in topics)
    as_of = str(config.get("as_of", ""))
    content = f"""# AI产业链样本可信度周审计_{as_of}

> 任务类型：阶段基线
> 数据截止：{as_of}

## 结论

`A={counts.get('A', 0)} / B={counts.get('B', 0)} / C={counts.get('C', 0)}`，正式 A `{formal_ready}/337`。本轮代表组 cross-source 均为 `insufficient_sources`，不改变正式 A 的技术判定。

## 阻塞摘要

{markdown_table(['阻塞类型', 'L4数'], [[name, count] for name, count in blockers.most_common()])}

## 机器口径

- L4 覆盖按稳定 `l4_id` 校验。
- 同名 canonical topic 不合并；stock 角色按 `parent_l4_id` 聚合。
- `technical_cross_source_ok=是` 只保留给字段级有至少两个可比较来源且一致的证据；本轮行情代理不满足。
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def resolve_path(raw: str, root: Path) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else root / path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic AI industry stage baseline.")
    parser.add_argument("--project-root")
    parser.add_argument("--registry", required=True)
    parser.add_argument("--baseline-manifest", required=True)
    parser.add_argument("--confidence-table", required=True)
    parser.add_argument("--delta-config", required=True)
    parser.add_argument("--manifest-output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--audit-output", required=True)
    args = parser.parse_args()
    try:
        root = resolve_configured_root(
            cli_value=args.project_root,
            env_name="AI_INDUSTRY_RESEARCH_ROOT",
            discovery_starts=(Path.cwd(), Path(__file__).resolve().parent),
            marker_paths=("AGENTS.md", "00_总控台"),
            label="AI research repository",
        )
        registry_rows = read_csv(resolve_path(args.registry, root), REGISTRY_COLUMNS)
        if len(registry_rows) != 337:
            raise ValueError(f"注册表必须为 337 行，当前为 {len(registry_rows)}")
        if len({normalize(row["l4_id"]) for row in registry_rows}) != 337:
            raise ValueError("注册表 l4_id 不唯一")
        baseline_rows = read_csv(resolve_path(args.baseline_manifest, root), LEGACY_COLUMNS)
        confidence = load_confidence_rows(resolve_path(args.confidence_table, root))
        config = json.loads(resolve_path(args.delta_config, root).read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("delta 配置根节点必须是对象")
        rows, changes = build_rows(registry_rows, baseline_rows, confidence, config)
        write_manifest(resolve_path(args.manifest_output, root), rows)
        write_report(resolve_path(args.report_output, root), rows, changes, config)
        write_audit(resolve_path(args.audit_output, root), rows, config)
    except (OSError, ValueError, json.JSONDecodeError, RootResolutionError) as exc:
        print("FAIL")
        print(f"- {exc}")
        return 1
    print("PASS")
    print(f"- topic={sum(row['kind'] == 'topic' for row in rows)} stock={sum(row['kind'] == 'stock' for row in rows)}")
    print(f"- changed_topics={len(changes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
