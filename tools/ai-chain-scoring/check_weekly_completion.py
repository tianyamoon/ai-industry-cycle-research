from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from path_config import RootResolutionError, resolve_configured_root, resolve_repo_path


ACTIONS = {"买入", "增持", "持有", "减持", "卖出"}
STATUSES = {"已评分", "待补评分", "仅观察", "未纳入本周样本"}
TRUTHY = {"是", "true", "True", "TRUE", "1", "yes", "Y", "已补", "已追加", "通过"}
MISSING = {"", "-", "无", "待补", "待核", "不适用", "NA", "N/A"}
CONFIDENCE_VALUES = {"A", "B", "C", "待核", "待定"}
FORMAL_TECH_SOURCES = {"Luna Stock MCP", "项目技术数据源"}
REQUIRED_SAMPLE_ROLES = {"全球锚", "A股承接锚", "弹性/反证样本"}
HIGH_CONFIDENCE_VALUES = {"high", "a", "高"}
WIKI_SYNC_STATUSES = {"已同步", "无需同步", "待同步"}
EXPECTED_FULL_L4_COUNT = 337
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
L4_ID_PATTERN = re.compile(r"^AI-L4-\d{4,}$")

REQUIRED_MANIFEST_COLUMNS = [
    "schema_version",
    "l4_id",
    "l1",
    "l2",
    "l3",
    "l4",
    "canonical_topic",
    "sample_id",
    "parent_l4_id",
    "market",
    "ticker",
    "kind",
    "name",
    "status",
    "wiki_path",
    "wiki_sync_status",
    "wiki_skip_reason",
    "score",
    "action",
    "has_industry_logic",
    "has_valuation_funds",
    "has_technical_structure",
    "has_score_reason",
    "has_evidence_source",
    "has_history",
    "has_next_trigger",
    "pending_reason",
    "sample_reason",
    "evidence_path",
    "sample_confidence",
    "confidence_reason",
    "is_a_qualified",
    "a_gap_reason",
    "has_global_anchor",
    "has_ashare_anchor",
    "has_elasticity_or_counterexample",
    "parent_topic",
    "sample_role",
    "blocker_type",
    "has_davis_path",
    "technical_source",
    "technical_tool",
    "technical_arguments",
    "technical_structured_ready",
    "technical_actual_source",
    "technical_fallback_used",
    "technical_confidence",
    "technical_warnings",
    "technical_cross_source_validated",
    "technical_cross_source_ok",
]

COMMON_REPORT_MARKERS = [
    "任务类型",
    "本次范围",
    "完成情况",
    "覆盖矩阵",
    "产业逻辑层",
    "估值资金层",
    "技术结构层",
    "机器检查",
    "评分历史",
]
STAGE_REPORT_MARKER_ALIASES = [
    ("样本可信度分布",),
    ("正式 A 门槛", "正式A门槛"),
    ("样本可信度 A 缺口摘要", "A级缺口摘要"),
]
FORMAL_REPORT_MARKERS = [
    "本周已评分细分",
    "本周待补细分",
    "本周仅观察细分",
    "本周未纳入个股样本",
]
NON_FORMAL_MARKERS = [
    "阶段基线",
    "未完成",
    "formal FAIL",
    "未通过正式A门槛",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def normalize(value: str) -> str:
    value = value.strip().strip("`").strip()
    value = value.replace("／", "/")
    value = re.sub(r"\s+", " ", value)
    return value


def is_truthy(value: str) -> bool:
    return normalize(value) in TRUTHY


def is_missing(value: str) -> bool:
    return normalize(value) in MISSING


def has_text(value: str) -> bool:
    return bool(value.strip())


def is_high_confidence(value: str) -> bool:
    return normalize(value).lower() in HIGH_CONFIDENCE_VALUES


def resolve_path(raw: str, root: Path) -> Path | None:
    raw = raw.strip().strip("`").strip()
    if is_missing(raw):
        return None
    path = Path(raw)
    if path.is_absolute():
        return path
    return root / path


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("完成清单没有表头")
        missing = [col for col in REQUIRED_MANIFEST_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError("完成清单缺少列: " + ", ".join(missing))
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def load_registry(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("L4 注册表没有表头")
        missing = [column for column in REGISTRY_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError("L4 注册表缺少列: " + ", ".join(missing))
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def format_values(values: set[str] | list[str]) -> str:
    ordered = sorted(values)
    preview = "、".join(ordered[:20])
    if len(ordered) > 20:
        preview += f" 等 {len(ordered)} 项"
    return preview


def validate_full_registry(
    registry_path: Path,
    errors: list[str],
) -> set[str] | None:
    if not registry_path.exists():
        errors.append(f"L4 注册表不存在: {registry_path}")
        return None
    try:
        rows = load_registry(registry_path)
    except ValueError as exc:
        errors.append(str(exc))
        return None

    if len(rows) != EXPECTED_FULL_L4_COUNT:
        errors.append(f"L4 注册表必须恰好包含 337 行: 当前 {len(rows)} 行")

    l4_ids = [normalize(row.get("l4_id", "")) for row in rows]
    blank_ids = [index for index, l4_id in enumerate(l4_ids, start=2) if is_missing(l4_id)]
    if blank_ids:
        errors.append(f"L4 注册表 l4_id 不能为空: 第 {format_values([str(item) for item in blank_ids])} 行")
    duplicate_ids = {l4_id for l4_id, count in Counter(l4_ids).items() if l4_id and count > 1}
    if duplicate_ids:
        errors.append(f"L4 注册表 l4_id 必须唯一: {format_values(duplicate_ids)}")
    invalid_ids = {l4_id for l4_id in l4_ids if l4_id and not L4_ID_PATTERN.fullmatch(l4_id)}
    if invalid_ids:
        errors.append(f"L4 注册表 l4_id 格式非法: {format_values(invalid_ids)}")

    coordinates = [normalize(row.get("research_coordinate", "")) for row in rows]
    blank_coordinates = [index for index, value in enumerate(coordinates, start=2) if is_missing(value)]
    if blank_coordinates:
        errors.append(
            f"L4 注册表 research_coordinate 不能为空: 第 "
            f"{format_values([str(item) for item in blank_coordinates])} 行"
        )
    duplicate_coordinates = {
        coordinate for coordinate, count in Counter(coordinates).items() if coordinate and count > 1
    }
    if duplicate_coordinates:
        errors.append(f"L4 注册表 research_coordinate 必须唯一: {format_values(duplicate_coordinates)}")

    return {l4_id for l4_id in l4_ids if not is_missing(l4_id)}


def validate_manifest_identities(
    topic_rows: list[dict[str, str]],
    stock_rows: list[dict[str, str]],
    registry_ids: set[str] | None,
    coverage: str,
    errors: list[str],
) -> set[str]:
    topic_ids = [normalize(row.get("l4_id", "")) for row in topic_rows]
    topic_id_set = {l4_id for l4_id in topic_ids if not is_missing(l4_id)}
    duplicate_topic_ids = {
        l4_id for l4_id, count in Counter(topic_ids).items() if l4_id and count > 1
    }
    if duplicate_topic_ids:
        errors.append(f"topic l4_id 重复: {format_values(duplicate_topic_ids)}")

    if coverage == "full" and registry_ids is not None:
        missing_ids = registry_ids - topic_id_set
        unknown_ids = topic_id_set - registry_ids
        if missing_ids:
            errors.append(f"full 覆盖缺少 l4_id: {format_values(missing_ids)}")
        if unknown_ids:
            errors.append(f"topic 含未知 l4_id: {format_values(unknown_ids)}")

    sample_ids = [normalize(row.get("sample_id", "")) for row in stock_rows]
    duplicate_sample_ids = {
        sample_id for sample_id, count in Counter(sample_ids).items() if sample_id and count > 1
    }
    if duplicate_sample_ids:
        errors.append(f"stock sample_id 重复: {format_values(duplicate_sample_ids)}")

    return registry_ids if coverage == "full" and registry_ids is not None else topic_id_set


def validate_report(args: argparse.Namespace, errors: list[str]) -> str:
    report_path = resolve_repo_path(args.report, Path(args.project_root))
    if not report_path.exists():
        errors.append(f"结果层报告不存在: {report_path}")
        return ""
    text = read_text(report_path)
    for marker in COMMON_REPORT_MARKERS:
        if marker not in text:
            errors.append(f"报告缺少必备章节或字段: {marker}")
    if args.mode == "stage":
        for aliases in STAGE_REPORT_MARKER_ALIASES:
            if not any(marker in text for marker in aliases):
                errors.append(f"阶段产物缺少必备章节或字段: {aliases[0]}")
    if args.mode == "formal":
        for marker in FORMAL_REPORT_MARKERS:
            if marker not in text:
                errors.append(f"正式周更报告缺少必备章节或字段: {marker}")
        for marker in NON_FORMAL_MARKERS:
            if marker in text:
                errors.append(f"正式周更报告不能包含非正式完成标记: {marker}")
        if not any(action in text for action in ACTIONS):
            errors.append("正式周更报告没有出现动作评级")
    return text


def validate_manifest(args: argparse.Namespace, errors: list[str], warnings: list[str]) -> None:
    project_root = Path(args.project_root)
    wiki_root = Path(args.wiki_root)
    manifest_path = resolve_repo_path(args.manifest, project_root)
    if not manifest_path.exists():
        errors.append(f"完成清单不存在: {manifest_path}")
        return
    try:
        rows = load_manifest(manifest_path)
    except ValueError as exc:
        errors.append(str(exc))
        return

    if not rows:
        errors.append("完成清单没有任何行")
        return

    topic_rows = [row for row in rows if normalize(row.get("kind", "")) == "topic"]
    stock_rows = [row for row in rows if normalize(row.get("kind", "")) == "stock"]
    if len(topic_rows) < args.min_topic_rows:
        errors.append(f"题材清单行数不足: {len(topic_rows)} < {args.min_topic_rows}")
    if len(stock_rows) < args.min_stock_rows:
        errors.append(f"个股清单行数不足: {len(stock_rows)} < {args.min_stock_rows}")

    registry_ids: set[str] | None = None
    if args.coverage == "full":
        registry_path = resolve_repo_path(args.registry, project_root)
        registry_ids = validate_full_registry(registry_path, errors)
    valid_parent_ids = validate_manifest_identities(
        topic_rows,
        stock_rows,
        registry_ids,
        args.coverage,
        errors,
    )

    topic_roles: dict[str, set[str]] = defaultdict(set)
    for index, row in enumerate(rows, start=2):
        kind = normalize(row.get("kind", ""))
        name = normalize(row.get("name", ""))
        status = normalize(row.get("status", ""))
        prefix = f"完成清单第{index}行"

        if kind not in {"topic", "stock"}:
            errors.append(f"{prefix}: kind 必须是 topic 或 stock")
            continue
        if not name:
            errors.append(f"{prefix}: name 不能为空")
            continue
        if status not in STATUSES:
            errors.append(f"{prefix} {name}: status 非法: {status}")
            continue
        if is_missing(row.get("schema_version", "")):
            errors.append(f"{prefix} {name}: schema_version 不能为空")
        validate_wiki_sync(
            row,
            index,
            kind,
            name,
            wiki_root,
            args.week,
            args.mode,
            errors,
        )
        if is_missing(row.get("sample_reason", "")):
            errors.append(f"{prefix} {name}: sample_reason 不能为空")

        confidence = normalize(row.get("sample_confidence", ""))
        if confidence not in CONFIDENCE_VALUES:
            errors.append(f"{prefix} {name}: sample_confidence 非法: {confidence}")

        if kind == "topic":
            if is_missing(row.get("l4_id", "")):
                errors.append(f"{prefix} {name}: topic 行必须填写 l4_id")
        if kind == "stock":
            parent_topic = normalize(row.get("parent_topic", ""))
            parent_l4_id = normalize(row.get("parent_l4_id", ""))
            sample_id = normalize(row.get("sample_id", ""))
            sample_role = normalize(row.get("sample_role", ""))
            if is_missing(parent_topic):
                errors.append(f"{prefix} {name}: stock 行必须填写 parent_topic")
            if is_missing(parent_l4_id):
                errors.append(f"{prefix} {name}: stock 行必须填写 parent_l4_id")
            elif parent_l4_id not in valid_parent_ids:
                errors.append(f"{prefix} {name}: stock parent_l4_id 不在 L4 注册表中: {parent_l4_id}")
            if is_missing(sample_id):
                errors.append(f"{prefix} {name}: stock 行必须填写 sample_id")
            if is_missing(sample_role):
                errors.append(f"{prefix} {name}: stock 行必须填写 sample_role")
            else:
                topic_roles[parent_l4_id].add(sample_role)

        if status == "已评分":
            validate_scored_row(
                row,
                index,
                kind,
                name,
                project_root,
                errors,
                warnings,
            )
        else:
            if is_missing(row.get("pending_reason", "")):
                errors.append(f"{prefix} {name}: 非已评分状态必须填写 pending_reason")
            if normalize(row.get("action", "")) in {"买入", "增持"}:
                errors.append(f"{prefix} {name}: 未评分或观察对象不得给强动作评级")

        validate_confidence_fields(row, index, kind, name, args.mode, errors)

    if args.mode == "formal":
        validate_formal_requirements(topic_rows, stock_rows, topic_roles, errors)


def validate_confidence_fields(
    row: dict[str, str],
    index: int,
    kind: str,
    name: str,
    mode: str,
    errors: list[str],
) -> None:
    prefix = f"完成清单第{index}行 {name}"
    sample_confidence = normalize(row.get("sample_confidence", ""))
    is_a_qualified = is_truthy(row.get("is_a_qualified", ""))
    blocker_type = row.get("blocker_type", "")
    confidence_reason = row.get("confidence_reason", "")
    a_gap_reason = row.get("a_gap_reason", "")

    if kind == "topic":
        for col in ("has_global_anchor", "has_ashare_anchor", "has_elasticity_or_counterexample"):
            if is_missing(row.get(col, "")):
                errors.append(f"{prefix}: {col} 不能为空")

    if sample_confidence != "A" or not is_a_qualified or normalize(row.get("status", "")) != "已评分":
        if is_missing(confidence_reason):
            errors.append(f"{prefix}: 非正式A对象必须填写 confidence_reason")
        if is_missing(a_gap_reason):
            errors.append(f"{prefix}: 非正式A对象必须填写 a_gap_reason")
        if is_missing(blocker_type):
            errors.append(f"{prefix}: 非正式A对象必须填写 blocker_type")

    if is_missing(row.get("has_davis_path", "")):
        errors.append(f"{prefix}: has_davis_path 不能为空")
    if is_missing(row.get("technical_source", "")):
        errors.append(f"{prefix}: technical_source 不能为空")
    validate_technical_audit_fields(row, prefix, errors)

    if mode == "formal":
        if sample_confidence != "A":
            errors.append(f"{prefix}: formal 模式下 sample_confidence 必须为 A")
        if not is_a_qualified:
            errors.append(f"{prefix}: formal 模式下 is_a_qualified 必须为 是")


def validate_wiki_sync(
    row: dict[str, str],
    index: int,
    kind: str,
    name: str,
    wiki_root: Path,
    week: str,
    mode: str,
    errors: list[str],
) -> None:
    prefix = f"完成清单第{index}行 {name}"
    sync_status = normalize(row.get("wiki_sync_status", ""))
    skip_reason = row.get("wiki_skip_reason", "")

    if sync_status not in WIKI_SYNC_STATUSES:
        errors.append(f"{prefix}: wiki_sync_status 非法或为空: {sync_status}")
        return

    if sync_status in {"无需同步", "待同步"}:
        if is_missing(skip_reason):
            errors.append(f"{prefix}: {sync_status} 时必须填写 wiki_skip_reason")
        if sync_status == "待同步" and mode == "formal":
            errors.append(f"{prefix}: formal 模式不允许 wiki_sync_status=待同步")
        return

    wiki_path = resolve_path(row.get("wiki_path", ""), wiki_root)
    if wiki_path is None:
        errors.append(f"{prefix}: 已同步时 wiki_path 不能为空")
        return
    if not wiki_path.exists():
        errors.append(f"{prefix}: wiki_path 不存在: {wiki_path}")
        return

    if normalize(row.get("status", "")) != "已评分":
        return

    content = read_text(wiki_path)
    required_marker = "本周评分" if kind == "topic" else "本周个股评分"
    if required_marker not in content:
        errors.append(f"{prefix}: wiki 卡片缺少 {required_marker}")
    if "评分历史" not in content:
        errors.append(f"{prefix}: wiki 卡片缺少 评分历史")
    if week not in content:
        errors.append(f"{prefix}: wiki 卡片缺少本周日期 {week}")


def validate_technical_audit_fields(row: dict[str, str], prefix: str, errors: list[str]) -> None:
    required_non_blank = [
        "technical_tool",
        "technical_arguments",
        "technical_structured_ready",
        "technical_actual_source",
        "technical_fallback_used",
        "technical_confidence",
        "technical_warnings",
        "technical_cross_source_validated",
        "technical_cross_source_ok",
    ]
    for col in required_non_blank:
        if not has_text(row.get(col, "")):
            errors.append(f"{prefix}: {col} 不能为空")


def validate_scored_row(
    row: dict[str, str],
    index: int,
    kind: str,
    name: str,
    project_root: Path,
    errors: list[str],
    warnings: list[str],
) -> None:
    prefix = f"完成清单第{index}行 {name}"
    try:
        score = float(normalize(row.get("score", "")))
        if score < 0 or score > 100:
            errors.append(f"{prefix}: score 必须在 0-100")
    except ValueError:
        errors.append(f"{prefix}: 已评分行 score 必须是数字")

    action = normalize(row.get("action", ""))
    if action not in ACTIONS:
        errors.append(f"{prefix}: 已评分行 action 非法或为空")

    for col in [
        "has_industry_logic",
        "has_valuation_funds",
        "has_technical_structure",
        "has_score_reason",
        "has_evidence_source",
        "has_history",
        "has_next_trigger",
    ]:
        if not is_truthy(row.get(col, "")):
            errors.append(f"{prefix}: {col} 未通过")

    evidence_path = resolve_path(row.get("evidence_path", ""), project_root)
    if evidence_path is None:
        errors.append(f"{prefix}: 已评分行 evidence_path 不能为空")
    elif not evidence_path.exists():
        warnings.append(f"{prefix}: evidence_path 未找到，请确认是否为外部路径: {evidence_path}")


def validate_formal_requirements(
    topic_rows: list[dict[str, str]],
    stock_rows: list[dict[str, str]],
    topic_roles: dict[str, set[str]],
    errors: list[str],
) -> None:
    def validate_formal_technical_fields(row: dict[str, str], prefix: str) -> None:
        if not has_text(row.get("technical_tool", "")):
            errors.append(f"{prefix}: formal 模式下必须填写 technical_tool")
        if not has_text(row.get("technical_arguments", "")):
            errors.append(f"{prefix}: formal 模式下必须填写 technical_arguments")
        if not is_truthy(row.get("technical_structured_ready", "")):
            errors.append(f"{prefix}: formal 模式下必须确认 structuredContent 可用")
        if is_missing(row.get("technical_actual_source", "")):
            errors.append(f"{prefix}: formal 模式下必须填写 technical_actual_source")
        if is_truthy(row.get("technical_fallback_used", "")):
            errors.append(f"{prefix}: formal 模式下 technical_fallback_used 必须为 否")
        if not is_high_confidence(row.get("technical_confidence", "")):
            errors.append(f"{prefix}: formal 模式下 technical_confidence 必须达到高可信")
        if normalize(row.get("technical_warnings", "")) not in MISSING:
            errors.append(f"{prefix}: formal 模式下 technical_warnings 必须为空或无")
        if not is_truthy(row.get("technical_cross_source_validated", "")):
            errors.append(f"{prefix}: formal 模式下必须完成 technical_cross_source_validated")
        if not is_truthy(row.get("technical_cross_source_ok", "")):
            errors.append(f"{prefix}: formal 模式下 technical_cross_source_ok 必须为 是")

    for row in topic_rows:
        name = normalize(row.get("name", ""))
        l4_id = normalize(row.get("l4_id", ""))
        prefix = f"正式A门槛 {name} ({l4_id})"
        if normalize(row.get("status", "")) != "已评分":
            errors.append(f"{prefix}: formal 模式下 topic 状态必须为 已评分")
        if not is_truthy(row.get("has_global_anchor", "")):
            errors.append(f"{prefix}: 缺全球锚")
        if not is_truthy(row.get("has_ashare_anchor", "")):
            errors.append(f"{prefix}: 缺A股承接锚")
        if not is_truthy(row.get("has_elasticity_or_counterexample", "")):
            errors.append(f"{prefix}: 缺弹性/反证样本")
        if not is_truthy(row.get("has_davis_path", "")):
            errors.append(f"{prefix}: formal 模式下必须有戴维斯路径")
        if normalize(row.get("technical_source", "")) not in FORMAL_TECH_SOURCES:
            errors.append(f"{prefix}: formal 模式下 technical_source 必须来自 Luna Stock MCP 或项目技术数据源")
        validate_formal_technical_fields(row, prefix)

        roles = topic_roles.get(l4_id, set())
        missing_roles = sorted(REQUIRED_SAMPLE_ROLES - roles)
        if missing_roles:
            errors.append(
                f"{prefix}: parent_l4_id 关联的 stock 样本角色不完整: {'、'.join(missing_roles)}"
            )

    for row in stock_rows:
        name = normalize(row.get("name", ""))
        prefix = f"正式A门槛 stock {name}"
        if is_missing(row.get("parent_topic", "")):
            errors.append(f"{prefix}: formal 模式下 stock 行必须填写 parent_topic")
        if is_missing(row.get("parent_l4_id", "")):
            errors.append(f"{prefix}: formal 模式下 stock 行必须填写 parent_l4_id")
        if is_missing(row.get("sample_id", "")):
            errors.append(f"{prefix}: formal 模式下 stock 行必须填写 sample_id")
        if is_missing(row.get("sample_role", "")):
            errors.append(f"{prefix}: formal 模式下 stock 行必须填写 sample_role")
        if normalize(row.get("technical_source", "")) not in FORMAL_TECH_SOURCES:
            errors.append(f"{prefix}: formal 模式下 stock technical_source 必须来自 Luna Stock MCP 或项目技术数据源")
        validate_formal_technical_fields(row, prefix)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check AI industry weekly scoring completion gates.")
    parser.add_argument("--mode", choices=["formal", "stage"], default="formal")
    parser.add_argument("--coverage", choices=["full", "scoped"], default="full")
    parser.add_argument("--week", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--registry", default="00_总控台/AI产业链L4注册表.csv")
    parser.add_argument("--project-root")
    parser.add_argument("--wiki-root")
    parser.add_argument("--min-topic-rows", type=int, default=1)
    parser.add_argument("--min-stock-rows", type=int, default=1)
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    tool_root = Path(__file__).resolve().parent
    try:
        args.project_root = resolve_configured_root(
            cli_value=args.project_root,
            env_name="AI_INDUSTRY_RESEARCH_ROOT",
            discovery_starts=(Path.cwd(), tool_root),
            marker_paths=("AGENTS.md", "00_总控台"),
            label="AI research repository",
        )
        args.wiki_root = resolve_configured_root(
            cli_value=args.wiki_root,
            env_name="TRADE_SYSTEM_ROOT",
            discovery_starts=(Path.cwd(),),
            marker_paths=("topics", "entities/stocks"),
            label="trade-system wiki",
        )
    except RootResolutionError as exc:
        print(f"FAIL\n- {exc}")
        return 1
    validate_report(args, errors)
    validate_manifest(args, errors, warnings)

    if warnings:
        print("WARN")
        for item in warnings:
            print(f"- {item}")
    if errors:
        print("FAIL")
        for item in errors:
            print(f"- {item}")
        return 1
    print("PASS")
    if args.mode == "formal":
        print("- 正式周更报告、A门槛、完成清单、wiki 回写和历史留痕通过机器闸门")
    else:
        print("- 阶段基线通过机器闸门，但不代表已通过正式A门槛")
    return 0


if __name__ == "__main__":
    sys.exit(main())
