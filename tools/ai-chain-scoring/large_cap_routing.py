from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

from path_config import resolve_configured_root, resolve_repo_path


SINA_COMPANY_PROFILE_URL = (
    "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{code}.phtml"
)
INPUT_FIELDS = (
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
OUTPUT_FIELDS = INPUT_FIELDS + (
    "路由结论",
    "审计状态",
    "建议主层级",
    "建议细分",
    "业务证据等级",
    "业务证据来源",
    "业务证据抓取日期",
    "公司类型",
    "主营业务",
    "判定理由",
    "下一步动作",
)
OBSERVATION_OUTPUT_FIELDS = (
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

AI_ROUTE_RULES = (
    (
        "计算芯片/整机系统",
        "半导体芯片/集成电路/处理器/服务器/人工智能计算/算力设备",
        (
            "半导体芯片",
            "集成电路",
            "芯片设计",
            "芯片制造",
            "处理器",
            "服务器",
            "人工智能计算",
            "算力",
            "gpu",
            "npu",
        ),
    ),
    (
        "数据中心与基础设施",
        "数据中心/IDC/AIDC/云计算/云服务/算力租赁",
        (
            "数据中心",
            "idc",
            "aidc",
            "云计算",
            "云服务",
            "算力租赁",
            "算力服务",
        ),
    ),
    (
        "高速互联",
        "光模块/光器件/光通信/光纤光缆/高速连接",
        (
            "光模块",
            "光器件",
            "光通信",
            "光纤光缆",
            "光纤",
            "光缆",
            "高速连接",
            "连接器",
            "硅光",
        ),
    ),
    (
        "芯片制造与材料",
        "半导体设备/封装测试/电子材料/PCB/印制电路板",
        (
            "半导体设备",
            "封装测试",
            "集成电路封装",
            "电子材料",
            "半导体材料",
            "电子化学品",
            "印制电路板",
            "pcb",
            "晶圆",
            "硅片",
        ),
    ),
    (
        "工具链与基础软件",
        "人工智能/大模型/算法/机器学习/网络安全软件",
        (
            "人工智能",
            "大模型",
            "机器学习",
            "深度学习",
            "算法平台",
            "ai软件",
            "网络安全软件",
        ),
    ),
    (
        "终端与具身智能",
        "工业机器人/服务机器人/机器视觉/智能传感器",
        (
            "工业机器人",
            "服务机器人",
            "人形机器人",
            "机器视觉",
            "智能传感器",
            "视觉传感器",
            "激光雷达",
        ),
    ),
)
PRIORITY_AI_ROUTE_RULES = (
    (
        "先进封装",
        "先进封装/晶圆级封装/系统级封装/封装测试",
        (
            "先进封装",
            "晶圆级封装",
            "系统级封装",
            "晶圆中测",
            "封装测试",
        ),
    ),
    (
        "芯片制造与材料",
        "半导体设备/晶圆制造/半导体材料",
        (
            "集成电路专用设备",
            "半导体专用设备",
            "半导体设备",
            "晶圆代工",
            "晶圆制造",
            "半导体硅片",
            "电子化学品",
            "半导体材料",
        ),
    ),
    (
        "存储链",
        "企业级SSD/存储器/闪存/存储控制器",
        (
            "企业级ssd",
            "ssd",
            "存储器",
            "存储产品",
            "闪存",
            "dram",
            "nand",
            "存储控制器",
        ),
    ),
    (
        "高速互联",
        "光模块/光器件/光通信/PCB/高速连接",
        (
            "光无源器件",
            "光芯片",
            "光模块",
            "光器件",
            "光电子器件",
            "光通信",
            "光纤光缆",
            "高速连接",
            "印制电路板",
            "pcb",
            "覆铜板",
            "电子铜箔",
            "电子级玻璃纤维布",
        ),
    ),
)
AMBIGUOUS_UPSTREAM_KEYWORDS = (
    "光伏",
    "太阳能",
    "动力电池",
    "量子通信",
    "量子保密通信",
)
NON_AI_ROUTE_RULES = (
    (
        "金融服务",
        (
            "商业银行",
            "银行业务",
            "证券经纪",
            "证券承销",
            "保险业务",
            "人寿保险",
            "财产保险",
            "信托业务",
            "基金管理",
            "期货经纪",
        ),
    ),
    (
        "食品饮料",
        (
            "白酒",
            "茅台酒",
            "酿酒",
            "啤酒",
            "黄酒",
            "葡萄酒",
            "酒类",
            "乳制品",
            "食品饮料",
            "餐饮服务",
        ),
    ),
    (
        "地产与物业",
        (
            "房地产开发",
            "物业管理",
            "房地产经营",
        ),
    ),
    (
        "交通运输",
        (
            "铁路运输",
            "航空运输",
            "港口服务",
            "远洋运输",
            "公路运输",
            "快递服务",
        ),
    ),
    (
        "传统能源开采",
        (
            "煤炭开采",
            "煤炭生产",
            "石油天然气开采",
            "原油开采",
            "原油",
            "天然气",
            "煤炭",
        ),
    ),
    (
        "制药与医药流通",
        (
            "化学药",
            "中成药",
            "药品生产",
            "药品批发",
            "医药流通",
            "药物",
            "药品",
            "医疗器械",
            "医药",
        ),
    ),
    (
        "农业与养殖",
        (
            "生猪",
            "养殖",
            "屠宰",
            "饲料",
            "种子",
        ),
    ),
    (
        "交通运输",
        (
            "旅客运输",
            "集装箱运输",
            "海运业务",
            "航空客运",
            "航空货运",
            "船舶制造",
            "高铁",
        ),
    ),
    (
        "商品零售与日用消费",
        (
            "调味品",
            "厨房食品",
            "商品零售",
            "旅游商品零售",
            "日用陶瓷",
            "品牌服装",
        ),
    ),
)


def _normalize_code(raw: Any) -> str | None:
    code = str(raw or "").strip()
    return code if re.fullmatch(r"\d{6}", code) else None


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _html_to_text(html: str) -> str:
    without_scripts = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1>",
        " ",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return _clean_text(unescape(re.sub(r"<[^>]+>", " ", without_scripts)))


def _extract_field(text: str, label: str, terminators: tuple[str, ...]) -> str:
    boundary = "|".join(re.escape(item) for item in terminators)
    matched = re.search(
        rf"{re.escape(label)}[：:]\s*(.*?)(?=\s+(?:{boundary})[：:]|$)",
        text,
        flags=re.DOTALL,
    )
    return _clean_text(matched.group(1)) if matched else ""


def parse_sina_company_profile(html: str) -> dict[str, str]:
    text = _html_to_text(html)
    company_type = _extract_field(
        text,
        "机构类型",
        (
            "组织形式",
            "董事会秘书",
            "公司电话",
            "公司传真",
            "公司电子邮箱",
            "公司网址",
            "邮政编码",
            "信息披露网站",
            "证券简称更名历史",
            "注册地址",
            "办公地址",
            "公司简介",
            "主营业务",
        ),
    )
    business_matched = re.search(
        r"主营业务[：:]\s*(.*?)(?=\s*(?:↑\s*返回页顶|返回页顶|客户服务热线|欢迎批评指正|Copyright)|$)",
        text,
        flags=re.DOTALL,
    )
    main_business = _clean_text(business_matched.group(1)) if business_matched else ""
    return {"公司类型": company_type, "主营业务": main_business}


def _first_matching_keyword(text: str, keywords: Iterable[str]) -> str:
    normalized = text.lower()
    for keyword in keywords:
        if keyword.lower() in normalized:
            return keyword
    return ""


def classify_route(profile: dict[str, str]) -> dict[str, str]:
    company_type = profile.get("公司类型", "").strip()
    main_business = profile.get("主营业务", "").strip()
    evidence_text = " ".join(part for part in (company_type, main_business) if part)
    if not evidence_text:
        return {
            "路由结论": "信息不足",
            "审计状态": "待补证",
            "建议主层级": "待补证",
            "建议细分": "待核主营业务",
            "当前等级": "L0待补证",
            "判定理由": "未取得可用主营业务字段，不能按公司名称、概念标签或市场热度推断AI关系。",
            "下一步动作": "优先回源最新年报、公告、投关材料或官网产品页，确认主营产品、客户与AI关系。",
        }

    ambiguous_keyword = _first_matching_keyword(main_business, AMBIGUOUS_UPSTREAM_KEYWORDS)
    if ambiguous_keyword:
        return {
            "路由结论": "信息不足",
            "审计状态": "待补证",
            "建议主层级": "待补证",
            "建议细分": "待核主营业务与AI关系",
            "当前等级": "L0待补证",
            "判定理由": f"主营业务出现“{ambiguous_keyword}”，属于可能受AI基础设施间接带动的泛上游，不能仅因材料名称或概念标签认定为AI产业链。",
            "下一步动作": "优先回源年报、公告、投关材料或官网产品页，确认是否承担AI关键零部件、原材料、设备或基础设施供给。",
        }

    for layer, segment, keywords in PRIORITY_AI_ROUTE_RULES + AI_ROUTE_RULES:
        keyword = _first_matching_keyword(evidence_text, keywords)
        if keyword:
            return {
                "路由结论": "AI产业链相关",
                "审计状态": "已初筛",
                "建议主层级": layer,
                "建议细分": segment,
                "当前等级": "L0",
                "判定理由": f"主营业务或公司类型出现“{keyword}”，可定位为{segment}的直接供给或服务线索。",
                "下一步动作": "回源年报、公告、投关材料或官网产品页，核对产品、客户、收入与AI业务纯度后再升级。",
            }

    for category, keywords in NON_AI_ROUTE_RULES:
        keyword = _first_matching_keyword(evidence_text, keywords)
        if keyword:
            return {
                "路由结论": "非AI",
                "审计状态": "已初筛",
                "建议主层级": "非AI",
                "建议细分": category,
                "当前等级": "不适用",
                "判定理由": f"主营业务出现“{keyword}”，当前可见主业属于{category}，未见直接AI产业链产品或服务。",
                "下一步动作": "保留审计记录；如后续年报、公告或产品页披露直接AI产业链产品，再重新路由。",
            }

    return {
        "路由结论": "信息不足",
        "审计状态": "待补证",
        "建议主层级": "待补证",
        "建议细分": "待核主营业务与AI关系",
        "当前等级": "L0待补证",
        "判定理由": "主营业务未出现可直接定位的AI产业链产品；泛材料、通用制造、电力与基础设施不因名称或概念标签强行归类。",
        "下一步动作": "优先回源年报、公告、投关材料或官网产品页，确认是否承担AI关键零部件、原材料、设备或基础设施供给。",
    }


def _profile_url(code: str) -> str:
    return SINA_COMPANY_PROFILE_URL.format(code=code)


def fetch_sina_company_profile(code: str, *, timeout_seconds: int, retries: int) -> dict[str, str]:
    url = _profile_url(code)
    last_error = ""
    for _attempt in range(retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            opener = build_opener(ProxyHandler({}))
            with opener.open(request, timeout=timeout_seconds) as response:
                html = response.read().decode("gb18030", errors="replace")
            profile = parse_sina_company_profile(html)
            profile["抓取状态"] = "已获取" if profile["主营业务"] else "未提取到主营业务"
            profile["证据链接"] = url
            return profile
        except (HTTPError, URLError, OSError, TimeoutError) as error:
            last_error = str(error)
    return {
        "公司类型": "",
        "主营业务": "",
        "抓取状态": f"抓取失败：{last_error or '未知错误'}",
        "证据链接": url,
    }


def fetch_sina_company_profiles(
    codes: Iterable[str],
    *,
    workers: int,
    timeout_seconds: int,
    retries: int,
) -> dict[str, dict[str, str]]:
    normalized_codes = sorted({code for raw in codes if (code := _normalize_code(raw))})
    profiles: dict[str, dict[str, str]] = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(
                fetch_sina_company_profile,
                code,
                timeout_seconds=timeout_seconds,
                retries=retries,
            ): code
            for code in normalized_codes
        }
        for future in as_completed(futures):
            code = futures[future]
            try:
                profiles[code] = future.result()
            except Exception as error:  # pragma: no cover - defensive boundary for a worker failure
                profiles[code] = {
                    "公司类型": "",
                    "主营业务": "",
                    "抓取状态": f"抓取失败：{error}",
                    "证据链接": _profile_url(code),
                }
    return profiles


def load_profile_cache(path: Path) -> dict[str, dict[str, str]]:
    profiles: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            code = _normalize_code(row.get("代码", ""))
            main_business = row.get("主营业务", "").strip()
            if not code or not main_business:
                continue
            profiles[code] = {
                "公司类型": row.get("公司类型", "").strip(),
                "主营业务": main_business,
                "抓取状态": "已从快照复用",
                "证据链接": row.get("业务证据来源", "").strip(),
            }
    return profiles


def _base_record(row: dict[str, str]) -> dict[str, str]:
    return {field: row.get(field, "").strip() for field in INPUT_FIELDS}


def build_routing_records(
    rows: Iterable[dict[str, str]],
    profiles: dict[str, dict[str, str]],
    *,
    as_of_date: str,
) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for raw_row in rows:
        record = _base_record(raw_row)
        code = _normalize_code(record["代码"])
        is_pending = record["AI路由状态"] == "待路由审计"
        if not is_pending:
            record.update(
                {
                    "路由结论": "AI产业链相关",
                    "审计状态": "已路由",
                    "建议主层级": record["主层级"],
                    "建议细分": record["细分"],
                    "业务证据等级": "沿用既有候选池",
                    "业务证据来源": "既有AI候选宇宙",
                    "业务证据抓取日期": as_of_date,
                    "公司类型": "",
                    "主营业务": "",
                    "判定理由": "该代码已在既有AI候选宇宙中路由；本批不以门户资料重复判定。",
                    "下一步动作": record["下一步回源"],
                }
            )
        else:
            profile = profiles.get(code or "", {})
            conclusion = classify_route(profile)
            record.update(
                {
                    "路由结论": conclusion["路由结论"],
                    "审计状态": conclusion["审计状态"],
                    "建议主层级": conclusion["建议主层级"],
                    "建议细分": conclusion["建议细分"],
                    "业务证据等级": "B",
                    "业务证据来源": profile.get("证据链接", _profile_url(code or "")),
                    "业务证据抓取日期": as_of_date,
                    "公司类型": profile.get("公司类型", ""),
                    "主营业务": profile.get("主营业务", ""),
                    "判定理由": conclusion["判定理由"],
                    "下一步动作": conclusion["下一步动作"],
                    "当前等级": conclusion["当前等级"],
                }
            )
        records.append(record)

    return sorted(
        records,
        key=lambda row: (
            0 if row["观察状态"] in {"强制观察", "强制审计"} else 1,
            -float(row["总市值(亿元)"] or 0),
            row["代码"],
        ),
    )


def build_summary(records: Iterable[dict[str, str]], *, as_of_date: str) -> dict[str, Any]:
    materialized = list(records)
    pending = [record for record in materialized if record["AI路由状态"] == "待路由审计"]
    hard_pending = [record for record in pending if record["观察状态"] == "强制审计"]
    boundary_pending = [record for record in pending if record["观察状态"] == "边界待路由"]
    hard_counts = Counter(record["路由结论"] for record in hard_pending)
    boundary_counts = Counter(record["路由结论"] for record in boundary_pending)
    all_counts = Counter(record["路由结论"] for record in materialized)
    return {
        "as_of_date": as_of_date,
        "input_row_count": len(materialized),
        "hard_pending_count": len(hard_pending),
        "boundary_pending_count": len(boundary_pending),
        "pending_total_count": len(pending),
        "hard_pending_ai_related_count": hard_counts["AI产业链相关"],
        "hard_pending_non_ai_count": hard_counts["非AI"],
        "hard_pending_information_insufficient_count": hard_counts["信息不足"],
        "boundary_pending_ai_related_count": boundary_counts["AI产业链相关"],
        "boundary_pending_non_ai_count": boundary_counts["非AI"],
        "boundary_pending_information_insufficient_count": boundary_counts["信息不足"],
        "all_record_conclusion_counts": dict(sorted(all_counts.items())),
        "unresolved_count": sum(record["路由结论"] == "信息不足" for record in pending),
        "evidence_note": "本批为主营业务预筛，使用新浪财经公司资料中的主营业务和机构类型，证据等级=B；不作为经营验证、评分或结果层结论依据。",
        "routing_rule": "明确直接AI产品/服务可列AI产业链相关；主营明确属于非AI行业可列非AI；泛材料、通用制造、电力与基础设施一律保留信息不足，等待年报、公告、投关或官网产品页补证。",
    }


def build_expanded_observation_records(
    routing_records: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    records_by_code: dict[str, dict[str, str]] = {}
    for routed in routing_records:
        if routed.get("路由结论") != "AI产业链相关":
            continue
        code = _normalize_code(routed.get("代码", ""))
        if not code:
            continue
        existing_candidate = routed.get("AI路由状态") == "已路由AI候选"
        hard_observation = routed.get("观察状态") in {"强制观察", "强制审计"}
        records_by_code[code] = {
            "代码": code,
            "标的": routed.get("标的", ""),
            "市值快照日期": routed.get("市值快照日期", ""),
            "快照时间": routed.get("快照时间", ""),
            "总市值(亿元)": routed.get("总市值(亿元)", ""),
            "市值状态": routed.get("市值状态", ""),
            "观察状态": "强制观察" if hard_observation else "边界复核",
            "边界复核": routed.get("边界复核", ""),
            "主层级": routed.get("主层级", "") if existing_candidate else routed.get("建议主层级", ""),
            "细分": routed.get("细分", "") if existing_candidate else routed.get("建议细分", ""),
            "来源网站": "既有AI候选宇宙" if existing_candidate else "新浪公司资料主营业务预筛",
            "来源条数": routed.get("来源条数", "") if existing_candidate else "1",
            "当前等级": routed.get("当前等级", "") if existing_candidate else "L0",
            "第一变量": routed.get("第一变量", "") if existing_candidate else "产品、客户、收入与AI业务纯度",
            "样本角色": routed.get("样本角色", "") if existing_candidate else "全市场路由补位/L0",
            "下一步回源": routed.get("下一步回源", "") if existing_candidate else routed.get("下一步动作", ""),
            "证伪点": routed.get("证伪点", "") if existing_candidate else "年报、公告、投关或产品页不能证明直接AI产业链产品、客户或收入。",
        }
    return sorted(
        records_by_code.values(),
        key=lambda row: (
            0 if row["观察状态"] == "强制观察" else 1,
            -float(row["总市值(亿元)"] or 0),
            row["代码"],
        ),
    )


def build_expanded_observation_summary(records: Iterable[dict[str, str]]) -> dict[str, Any]:
    materialized = list(records)
    return {
        "observation_pool_count": len(materialized),
        "strong_observation_count": sum(record["观察状态"] == "强制观察" for record in materialized),
        "boundary_review_count": sum(record["观察状态"] == "边界复核" for record in materialized),
        "existing_candidate_count": sum(record["来源网站"] == "既有AI候选宇宙" for record in materialized),
        "newly_routed_l0_count": sum(record["来源网站"] == "新浪公司资料主营业务预筛" for record in materialized),
        "coverage_note": "强制观察只表示必须进入研究视野；新路由样本为主营业务预筛L0，仍须按年报、公告、投关或产品页补证。",
    }


def _write_csv(
    path: Path,
    records: Iterable[dict[str, str]],
    *,
    fieldnames: tuple[str, ...] = OUTPUT_FIELDS,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    parser = argparse.ArgumentParser(description="按主营业务分流全A百亿待路由标的")
    parser.add_argument("--repo-root", help="AI研究仓根目录；默认按CLI、环境变量和仓库标记发现")
    parser.add_argument("--input", required=True, help="全市场市值路由审计CSV，相对路径基于研究仓根目录")
    parser.add_argument("--output", required=True, help="分流审计CSV，相对路径基于研究仓根目录")
    parser.add_argument("--summary", required=True, help="分流审计摘要JSON，相对路径基于研究仓根目录")
    parser.add_argument("--observation-output", help="合并后的百亿强制观察池CSV，相对路径基于研究仓根目录")
    parser.add_argument("--observation-summary", help="合并后的百亿强制观察池摘要JSON，相对路径基于研究仓根目录")
    parser.add_argument("--as-of-date", required=True, help="分流抓取日期，格式YYYY-MM-DD")
    parser.add_argument("--profile-cache", help="可复用的既有分流CSV，缺失的主营业务字段仍会重新抓取")
    parser.add_argument("--workers", type=int, default=8, help="公司资料并发抓取数")
    parser.add_argument("--timeout-seconds", type=int, default=20, help="单次抓取超时秒数")
    parser.add_argument("--retries", type=int, default=1, help="单只抓取失败后的重试次数")
    args = parser.parse_args()
    if bool(args.observation_output) != bool(args.observation_summary):
        parser.error("--observation-output and --observation-summary must be provided together")

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
    observation_output_path = (
        resolve_repo_path(args.observation_output, repository_root) if args.observation_output else None
    )
    observation_summary_path = (
        resolve_repo_path(args.observation_summary, repository_root) if args.observation_summary else None
    )
    profile_cache_path = (
        resolve_repo_path(args.profile_cache, repository_root) if args.profile_cache else None
    )

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    pending_codes = [
        row.get("代码", "")
        for row in rows
        if row.get("AI路由状态", "") == "待路由审计"
    ]
    profiles = load_profile_cache(profile_cache_path) if profile_cache_path else {}
    missing_codes = [
        code for code in pending_codes if (normalized := _normalize_code(code)) and normalized not in profiles
    ]
    profiles.update(
        fetch_sina_company_profiles(
            missing_codes,
            workers=args.workers,
            timeout_seconds=args.timeout_seconds,
            retries=args.retries,
        )
    )
    records = build_routing_records(rows, profiles, as_of_date=args.as_of_date)
    summary = build_summary(records, as_of_date=args.as_of_date)
    _write_csv(output_path, records)
    if observation_output_path and observation_summary_path:
        observation_records = build_expanded_observation_records(records)
        observation_summary = build_expanded_observation_summary(observation_records)
        _write_csv(
            observation_output_path,
            observation_records,
            fieldnames=OBSERVATION_OUTPUT_FIELDS,
        )
        observation_summary_path.parent.mkdir(parents=True, exist_ok=True)
        observation_summary_path.write_text(
            json.dumps(observation_summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        summary["expanded_observation_pool"] = observation_summary
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
