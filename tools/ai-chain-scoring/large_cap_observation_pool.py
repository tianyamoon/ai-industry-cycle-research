from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from path_config import resolve_configured_root, resolve_repo_path


DEFAULT_THRESHOLD_YI = 100.0
DEFAULT_BOUNDARY_LOW_YI = 90.0
DEFAULT_BOUNDARY_HIGH_YI = 110.0
SINA_MARKET_ENDPOINT = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
OUTPUT_FIELDS = (
    "代码",
    "标的",
    "市值快照日期",
    "快照时间",
    "总市值(亿元)",
    "市值状态",
    "观察状态",
    "边界复核",
    "主层级",
    "细分",
    "来源网站",
    "来源条数",
    "当前等级",
    "第一变量",
    "样本角色",
    "下一步回源",
    "证伪点",
)
FULL_MARKET_AUDIT_FIELDS = (
    "代码",
    "标的",
    "市值快照日期",
    "快照时间",
    "总市值(亿元)",
    "市值来源",
    "市值状态",
    "观察状态",
    "AI路由状态",
    "边界复核",
    "主层级",
    "细分",
    "来源网站",
    "来源条数",
    "当前等级",
    "第一变量",
    "样本角色",
    "下一步回源",
    "证伪点",
)


def tencent_symbol(code: str) -> str:
    normalized = code.zfill(6)
    if normalized.startswith("92"):
        return f"bj{normalized}"
    if normalized.startswith(("6", "9")):
        return f"sh{normalized}"
    if normalized.startswith(("4", "8")):
        return f"bj{normalized}"
    return f"sz{normalized}"


def _normalize_stock_code(raw: Any) -> str | None:
    code = str(raw or "").strip()
    if not re.fullmatch(r"\d{6}", code) or code == "000000":
        return None
    return code


def _unique_join(rows: Iterable[dict[str, str]], field: str) -> str:
    values = sorted({row.get(field, "").strip() for row in rows if row.get(field, "").strip()})
    return "、".join(values)


def _quote_cap(quote: dict[str, Any] | None) -> float | None:
    if not quote:
        return None
    value = quote.get("market_cap_yi")
    if value is None:
        return None
    return float(value)


def build_observation_records(
    candidates: Iterable[dict[str, str]],
    quotes: dict[str, dict[str, Any]],
    *,
    as_of_date: str,
    threshold_yi: float = DEFAULT_THRESHOLD_YI,
    boundary_low_yi: float = DEFAULT_BOUNDARY_LOW_YI,
    boundary_high_yi: float = DEFAULT_BOUNDARY_HIGH_YI,
) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for candidate in candidates:
        code = _normalize_stock_code(candidate.get("代码", ""))
        if code:
            grouped[code].append(candidate)

    records: list[dict[str, str]] = []
    for code, routes in grouped.items():
        quote = quotes.get(code)
        market_cap_yi = _quote_cap(quote)
        if market_cap_yi is None:
            observation_status = "市值待补"
            market_status = "未获取"
        elif market_cap_yi >= threshold_yi:
            observation_status = "强制观察"
            market_status = f">={threshold_yi:.0f}亿元"
        elif market_cap_yi >= boundary_low_yi:
            observation_status = "边界复核"
            market_status = f"{boundary_low_yi:.0f}-{threshold_yi:.0f}亿元"
        else:
            continue

        records.append(
            {
                "代码": code,
                "标的": routes[0].get("标的", "").strip(),
                "市值快照日期": as_of_date,
                "快照时间": "" if not quote else str(quote.get("quote_time", "")),
                "总市值(亿元)": "" if market_cap_yi is None else f"{market_cap_yi:.2f}",
                "市值状态": market_status,
                "观察状态": observation_status,
                "边界复核": "是"
                if market_cap_yi is not None and boundary_low_yi <= market_cap_yi < boundary_high_yi
                else "否",
                "主层级": _unique_join(routes, "主层级"),
                "细分": _unique_join(routes, "细分"),
                "来源网站": _unique_join(routes, "来源网站"),
                "来源条数": str(len(routes)),
                "当前等级": _unique_join(routes, "当前等级"),
                "第一变量": _unique_join(routes, "第一变量"),
                "样本角色": _unique_join(routes, "样本角色"),
                "下一步回源": _unique_join(routes, "下一步回源"),
                "证伪点": _unique_join(routes, "证伪点"),
            }
        )

    status_order = {"强制观察": 0, "边界复核": 1, "市值待补": 2}
    return sorted(
        records,
        key=lambda row: (
            status_order[row["观察状态"]],
            -float(row["总市值(亿元)"] or 0),
            row["代码"],
        ),
    )


def parse_tencent_quotes(raw: str) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    for line in raw.splitlines():
        matched = re.match(r'^v_[^=]+="(?P<payload>.*)";$', line)
        if not matched:
            continue
        parts = matched.group("payload").split("~")
        if len(parts) <= 45 or not re.fullmatch(r"\d{6}", parts[2]):
            continue
        try:
            market_cap_yi = float(parts[45])
        except ValueError:
            continue
        quotes[parts[2]] = {"market_cap_yi": market_cap_yi, "quote_time": parts[30]}
    return quotes


def parse_sina_market_rows(raw: str) -> list[dict[str, Any]]:
    payload = json.loads(raw)
    if not isinstance(payload, list):
        raise ValueError("Sina market response must be a JSON list")

    rows: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        code = _normalize_stock_code(item.get("code", ""))
        try:
            market_cap_yi = round(float(item["mktcap"]) / 10000, 6)
        except (KeyError, TypeError, ValueError):
            continue
        if not code or market_cap_yi < 0:
            continue
        rows.append(
            {
                "代码": code,
                "标的": str(item.get("name", "")).strip(),
                "总市值(亿元)": market_cap_yi,
                "快照时间": str(item.get("ticktime", "")).strip(),
            }
        )
    return rows


def build_full_market_audit_records(
    candidates: Iterable[dict[str, str]],
    market_rows: Iterable[dict[str, Any]],
    *,
    supplemental_market_rows: Iterable[dict[str, Any]] = (),
    as_of_date: str,
    threshold_yi: float = DEFAULT_THRESHOLD_YI,
    boundary_low_yi: float = DEFAULT_BOUNDARY_LOW_YI,
    boundary_high_yi: float = DEFAULT_BOUNDARY_HIGH_YI,
) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for candidate in candidates:
        code = _normalize_stock_code(candidate.get("代码", ""))
        if code:
            grouped[code].append(candidate)

    rows_by_code: dict[str, dict[str, Any]] = {}
    for market_row in market_rows:
        code = _normalize_stock_code(market_row.get("代码", ""))
        if code:
            rows_by_code[code] = market_row
    for market_row in supplemental_market_rows:
        code = _normalize_stock_code(market_row.get("代码", ""))
        if code:
            rows_by_code.setdefault(code, market_row)

    records: list[dict[str, str]] = []
    for market_row in rows_by_code.values():
        code = _normalize_stock_code(market_row.get("代码", ""))
        try:
            market_cap_yi = float(market_row["总市值(亿元)"])
        except (KeyError, TypeError, ValueError):
            continue
        if not code or market_cap_yi < boundary_low_yi:
            continue

        routes = grouped.get(code, [])
        hard_threshold = market_cap_yi >= threshold_yi
        if routes:
            observation_status = "强制观察" if hard_threshold else "边界复核"
            routing_status = "已路由AI候选"
            name = routes[0].get("标的", "").strip() or str(market_row.get("标的", "")).strip()
        else:
            observation_status = "强制审计" if hard_threshold else "边界待路由"
            routing_status = "待路由审计"
            name = str(market_row.get("标的", "")).strip()

        records.append(
            {
                "代码": code,
                "标的": name,
                "市值快照日期": as_of_date,
                "快照时间": str(market_row.get("快照时间", "")).strip(),
                "总市值(亿元)": f"{market_cap_yi:.2f}",
                "市值来源": str(market_row.get("市值来源", "新浪财经全市场市值清单")).strip(),
                "市值状态": f">={threshold_yi:.0f}亿元" if hard_threshold else f"{boundary_low_yi:.0f}-{threshold_yi:.0f}亿元",
                "观察状态": observation_status,
                "AI路由状态": routing_status,
                "边界复核": "是" if boundary_low_yi <= market_cap_yi < boundary_high_yi else "否",
                "主层级": _unique_join(routes, "主层级") if routes else "待路由审计",
                "细分": _unique_join(routes, "细分") if routes else "待路由审计",
                "来源网站": _unique_join(routes, "来源网站") if routes else "新浪全市场市值清单",
                "来源条数": str(len(routes)),
                "当前等级": _unique_join(routes, "当前等级") if routes else "L0待路由",
                "第一变量": _unique_join(routes, "第一变量") if routes else "先判定是否属于AI产业链，再确定第一变量",
                "样本角色": _unique_join(routes, "样本角色") if routes else "全市场待路由审计",
                "下一步回源": _unique_join(routes, "下一步回源") if routes else "年报、公告、IR和产品页核对主营业务与AI关系",
                "证伪点": _unique_join(routes, "证伪点") if routes else "主营业务与AI产业链无实质关系，标记为非AI并保留审计记录",
            }
        )

    return sorted(
        records,
        key=lambda row: (
            0 if row["观察状态"] in {"强制观察", "强制审计"} else 1,
            -float(row["总市值(亿元)"]),
            row["代码"],
        ),
    )


def fetch_tencent_quotes(codes: Iterable[str], *, batch_size: int, timeout_seconds: int) -> dict[str, dict[str, Any]]:
    normalized_codes = [normalized for code in codes if (normalized := _normalize_stock_code(code))]
    quotes: dict[str, dict[str, Any]] = {}
    for offset in range(0, len(normalized_codes), batch_size):
        symbols = ",".join(tencent_symbol(code) for code in normalized_codes[offset : offset + batch_size])
        result = subprocess.run(
            [
                "curl.exe",
                "--silent",
                "--show-error",
                "--location",
                "--max-time",
                str(timeout_seconds),
                f"https://qt.gtimg.cn/q={symbols}",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="gb18030",
            errors="replace",
        )
        if result.returncode != 0:
            raise RuntimeError(f"Tencent quote request failed for batch {offset // batch_size + 1}: {result.stderr.strip()}")
        quotes.update(parse_tencent_quotes(result.stdout))
    return quotes


def fetch_sina_market_rows(
    *,
    page_size: int,
    timeout_seconds: int,
    minimum_yi: float = DEFAULT_BOUNDARY_LOW_YI,
    max_pages: int | None = None,
) -> list[dict[str, Any]]:
    rows_by_code: dict[str, dict[str, Any]] = {}
    page = 1
    while True:
        if max_pages is not None and page > max_pages:
            raise RuntimeError(
                "Sina market pagination stopped before reaching the market-cap boundary; "
                "increase max_pages or remove the limit"
            )
        url = (
            f"{SINA_MARKET_ENDPOINT}?page={page}&num={page_size}&sort=mktcap&asc=0"
            "&node=hs_a&_s_r_a=page"
        )
        result = subprocess.run(
            [
                "curl.exe",
                "--silent",
                "--show-error",
                "--location",
                "--max-time",
                str(timeout_seconds),
                url,
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            raise RuntimeError(f"Sina market request failed for page {page}: {result.stderr.strip()}")

        page_rows = parse_sina_market_rows(result.stdout)
        for row in page_rows:
            if row["总市值(亿元)"] < minimum_yi:
                continue
            current = rows_by_code.get(row["代码"])
            if current is None or row["总市值(亿元)"] > current["总市值(亿元)"]:
                rows_by_code[row["代码"]] = row

        if not page_rows:
            break
        if page_rows[-1]["总市值(亿元)"] < minimum_yi:
            break
        page += 1

    return sorted(rows_by_code.values(), key=lambda row: (-row["总市值(亿元)"], row["代码"]))


def _write_csv(path: Path, records: list[dict[str, str]], *, fieldnames: tuple[str, ...] = OUTPUT_FIELDS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def _summary(
    records: list[dict[str, str]],
    candidate_count: int,
    quote_count: int,
    as_of_date: str,
    unresolved_candidate_row_count: int,
) -> dict[str, Any]:
    layer_counts: dict[str, int] = defaultdict(int)
    for record in records:
        for layer in record["主层级"].split("、"):
            if layer:
                layer_counts[layer] += 1
    return {
        "as_of_date": as_of_date,
        "candidate_code_count": candidate_count,
        "quote_code_count": quote_count,
        "unresolved_candidate_row_count": unresolved_candidate_row_count,
        "strong_observation_count": sum(record["观察状态"] == "强制观察" for record in records),
        "boundary_review_count": sum(record["观察状态"] == "边界复核" for record in records),
        "market_cap_pending_count": sum(record["观察状态"] == "市值待补" for record in records),
        "observation_pool_count": len(records),
        "coverage_note": "强制观察=总市值不低于100亿元；边界复核=90至100亿元；市值待补不得静默排除。",
        "layer_counts": dict(sorted(layer_counts.items())),
    }


def _full_market_audit_summary(records: list[dict[str, str]], as_of_date: str) -> dict[str, Any]:
    hard_records = [record for record in records if record["观察状态"] in {"强制观察", "强制审计"}]
    boundary_records = [record for record in records if record["观察状态"] in {"边界复核", "边界待路由"}]
    return {
        "as_of_date": as_of_date,
        "market_cap_source": "新浪财经全市场市值清单，腾讯行情补充新浪未覆盖的AI候选",
        "hard_threshold_count": len(hard_records),
        "routed_hard_count": sum(record["AI路由状态"] == "已路由AI候选" for record in hard_records),
        "unrouted_hard_count": sum(record["AI路由状态"] == "待路由审计" for record in hard_records),
        "boundary_review_count": len(boundary_records),
        "routed_boundary_count": sum(record["AI路由状态"] == "已路由AI候选" for record in boundary_records),
        "unrouted_boundary_count": sum(record["AI路由状态"] == "待路由审计" for record in boundary_records),
        "candidate_quote_supplement_count": sum(record["市值来源"] == "腾讯行情候选补充" for record in records),
        "audit_record_count": len(records),
        "coverage_note": "全市场中总市值不低于100亿元的A股必须给出AI路由结果；未在AI候选池的标的保留为待路由审计，不得静默遗漏。",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 AI 全产业链百亿市值强制观察池")
    parser.add_argument("--repo-root", help="AI 研究仓根目录；默认按 CLI > 环境变量 > 仓库标记发现")
    parser.add_argument("--input", required=True, help="候选样本 CSV，相对路径基于研究仓根目录")
    parser.add_argument("--output", required=True, help="观察池 CSV，相对路径基于研究仓根目录")
    parser.add_argument("--summary", required=True, help="观察池汇总 JSON，相对路径基于研究仓根目录")
    parser.add_argument("--market-audit-output", help="全市场百亿市值审计 CSV，相对路径基于研究仓根目录")
    parser.add_argument("--market-audit-summary", help="全市场百亿市值审计汇总 JSON，相对路径基于研究仓根目录")
    parser.add_argument("--as-of-date", required=True, help="市值快照日期 YYYY-MM-DD")
    parser.add_argument("--threshold-yi", type=float, default=DEFAULT_THRESHOLD_YI)
    parser.add_argument("--boundary-low-yi", type=float, default=DEFAULT_BOUNDARY_LOW_YI)
    parser.add_argument("--boundary-high-yi", type=float, default=DEFAULT_BOUNDARY_HIGH_YI)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--market-page-size", type=int, default=1000)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    args = parser.parse_args()
    if bool(args.market_audit_output) != bool(args.market_audit_summary):
        parser.error("--market-audit-output and --market-audit-summary must be provided together")

    repository_root = resolve_configured_root(
        cli_value=args.repo_root,
        env_name="AI_INDUSTRY_RESEARCH_ROOT",
        discovery_starts=[Path.cwd(), Path(__file__).resolve()],
        marker_paths=("AGENTS.md", "00_总控台"),
        label="AI research repository",
    )
    input_path = resolve_repo_path(args.input, repository_root)
    output_path = resolve_repo_path(args.output, repository_root)
    summary_path = resolve_repo_path(args.summary, repository_root)
    market_audit_output_path = (
        resolve_repo_path(args.market_audit_output, repository_root) if args.market_audit_output else None
    )
    market_audit_summary_path = (
        resolve_repo_path(args.market_audit_summary, repository_root) if args.market_audit_summary else None
    )

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    codes = sorted({code for row in candidates if (code := _normalize_stock_code(row.get("代码", "")))})
    unresolved_candidate_row_count = sum(
        _normalize_stock_code(row.get("代码", "")) is None for row in candidates
    )
    quotes = fetch_tencent_quotes(codes, batch_size=args.batch_size, timeout_seconds=args.timeout_seconds)
    records = build_observation_records(
        candidates,
        quotes,
        as_of_date=args.as_of_date,
        threshold_yi=args.threshold_yi,
        boundary_low_yi=args.boundary_low_yi,
        boundary_high_yi=args.boundary_high_yi,
    )
    observation_summary = _summary(
        records,
        len(codes),
        len(quotes),
        args.as_of_date,
        unresolved_candidate_row_count,
    )
    _write_csv(output_path, records)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(observation_summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    output: dict[str, Any] = {"observation_pool": observation_summary}
    if market_audit_output_path and market_audit_summary_path:
        market_rows = fetch_sina_market_rows(
            page_size=args.market_page_size,
            timeout_seconds=args.timeout_seconds,
            minimum_yi=args.boundary_low_yi,
        )
        market_audit_records = build_full_market_audit_records(
            candidates,
            market_rows,
            supplemental_market_rows=[
                {
                    "代码": code,
                    "总市值(亿元)": quote["market_cap_yi"],
                    "快照时间": quote.get("quote_time", ""),
                    "市值来源": "腾讯行情候选补充",
                }
                for code, quote in quotes.items()
            ],
            as_of_date=args.as_of_date,
            threshold_yi=args.threshold_yi,
            boundary_low_yi=args.boundary_low_yi,
            boundary_high_yi=args.boundary_high_yi,
        )
        market_audit_summary = _full_market_audit_summary(market_audit_records, args.as_of_date)
        _write_csv(market_audit_output_path, market_audit_records, fieldnames=FULL_MARKET_AUDIT_FIELDS)
        market_audit_summary_path.parent.mkdir(parents=True, exist_ok=True)
        market_audit_summary_path.write_text(
            json.dumps(market_audit_summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        output["full_market_audit"] = market_audit_summary

    print(json.dumps(output if market_audit_output_path else observation_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
