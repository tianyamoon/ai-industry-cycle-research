from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from path_config import RootResolutionError, resolve_configured_root, resolve_repo_path


SCHEMA_VERSION = "1"
DEFAULT_MAPPING_PATH = "00_总控台/trade-system题材主卡映射表.md"
DEFAULT_OUTPUT_PATH = "00_总控台/AI产业链L4注册表.csv"
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
L4_ID_PATTERN = re.compile(r"^AI-L4-(\d{4,})$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def normalize_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("`").strip())


def normalize_coordinate(value: str) -> str:
    parts = [normalize_cell(part).replace("／", "/") for part in value.split("->")]
    return " -> ".join(parts)


def parse_markdown_tables(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    lines = read_text(path).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not (line.startswith("|") and line.endswith("|")) or index + 1 >= len(lines):
            index += 1
            continue
        separator = lines[index + 1].strip()
        if not re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", separator):
            index += 1
            continue
        header = [cell.strip() for cell in line.strip("|").split("|")]
        index += 2
        while index < len(lines):
            row_line = lines[index].strip()
            if not (row_line.startswith("|") and row_line.endswith("|")):
                break
            cells = [cell.strip() for cell in row_line.strip("|").split("|")]
            if len(cells) < len(header):
                cells += [""] * (len(header) - len(cells))
            rows.append(dict(zip(header, cells)))
            index += 1
    return rows


def load_existing_ids(path: Path) -> tuple[dict[str, str], int]:
    if not path.exists():
        return {}, 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("既有 L4 注册表没有表头")
        missing = [column for column in REGISTRY_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError("既有 L4 注册表缺少列: " + ", ".join(missing))
        rows = list(reader)

    ids_by_coordinate: dict[str, str] = {}
    seen_ids: set[str] = set()
    max_number = 0
    for row_number, row in enumerate(rows, start=2):
        coordinate = normalize_coordinate(row.get("research_coordinate", ""))
        l4_id = normalize_cell(row.get("l4_id", ""))
        if not coordinate:
            raise ValueError(f"既有 L4 注册表第{row_number}行 research_coordinate 为空")
        if coordinate in ids_by_coordinate:
            raise ValueError(f"既有 L4 注册表 research_coordinate 重复: {coordinate}")
        match = L4_ID_PATTERN.fullmatch(l4_id)
        if match is None:
            raise ValueError(f"既有 L4 注册表 l4_id 非法: {l4_id}")
        if l4_id in seen_ids:
            raise ValueError(f"既有 L4 注册表 l4_id 重复: {l4_id}")
        ids_by_coordinate[coordinate] = l4_id
        seen_ids.add(l4_id)
        max_number = max(max_number, int(match.group(1)))
    return ids_by_coordinate, max_number


def build_registry_rows(mapping_path: Path, existing_path: Path) -> list[dict[str, str]]:
    existing_ids, max_number = load_existing_ids(existing_path)
    result: list[dict[str, str]] = []
    seen_coordinates: set[str] = set()

    for row in parse_markdown_tables(mapping_path):
        if normalize_cell(row.get("类型", "")) != "细分":
            continue
        canonical_topic = normalize_cell(row.get("规范主卡", ""))
        coordinate = normalize_coordinate(row.get("研究坐标", ""))
        if not canonical_topic:
            raise ValueError("题材主卡映射表存在规范主卡为空的细分行")
        coordinate_parts = coordinate.split(" -> ") if coordinate else []
        if len(coordinate_parts) != 3 or any(not part for part in coordinate_parts):
            raise ValueError(f"研究坐标必须恰好包含三个层级: {coordinate or '<空>'}")
        if coordinate in seen_coordinates:
            raise ValueError(f"题材主卡映射表研究坐标重复: {coordinate}")
        seen_coordinates.add(coordinate)

        l4_id = existing_ids.get(coordinate)
        if l4_id is None:
            max_number += 1
            l4_id = f"AI-L4-{max_number:04d}"
        l1, l2, l3 = coordinate_parts
        result.append(
            {
                "schema_version": SCHEMA_VERSION,
                "l4_id": l4_id,
                "l1": l1,
                "l2": l2,
                "l3": l3,
                "l4": canonical_topic,
                "canonical_topic": canonical_topic,
                "research_coordinate": coordinate,
                "wiki_path": f"topics/{canonical_topic}.md",
            }
        )
    if not result:
        raise ValueError("题材主卡映射表没有任何 类型=细分 的行")
    result.sort(key=lambda row: int(row["l4_id"].removeprefix("AI-L4-")))
    return result


def write_registry(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTRY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    temporary_path.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the stable AI industry L4 registry.")
    parser.add_argument("--project-root")
    parser.add_argument("--mapping", default=DEFAULT_MAPPING_PATH)
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    tool_root = Path(__file__).resolve().parent
    try:
        project_root = resolve_configured_root(
            cli_value=args.project_root,
            env_name="AI_INDUSTRY_RESEARCH_ROOT",
            discovery_starts=(Path.cwd(), tool_root),
            marker_paths=("AGENTS.md", "00_总控台"),
            label="AI research repository",
        )
        mapping_path = resolve_repo_path(args.mapping, project_root)
        output_path = resolve_repo_path(args.output, project_root)
        if not mapping_path.exists():
            raise ValueError(f"题材主卡映射表不存在: {mapping_path}")
        rows = build_registry_rows(mapping_path, output_path)
        write_registry(output_path, rows)
    except (OSError, RootResolutionError, ValueError) as exc:
        print(f"FAIL\n- {exc}")
        return 1

    print("PASS")
    print(f"- 已生成 {len(rows)} 个稳定 L4 身份: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
