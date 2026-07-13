from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "build_l4_registry.py"
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


def write_registry(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTRY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def test_builder_preserves_mapping_order_and_separates_same_canonical_topic(
    tmp_path: Path,
) -> None:
    mapping_path = tmp_path / "trade-system题材主卡映射表.md"
    output_path = tmp_path / "AI产业链L4注册表.csv"
    write_text(
        mapping_path,
        """# mapping

| 规范主卡 | 类型 | 研究坐标 | 既有页复用 | aliases |
|---|---|---|---|---|
| 人形机器人 | 细分 | 全球映射与海外变量传导层 -> 海外终端与具身主链 -> 人形机器人 | 是 | - |
| AI产业链 - 海外终端与具身主链 | 分支题 | 全球映射与海外变量传导层 -> 海外终端与具身主链 | 否 | - |
| 人形机器人 | 细分 | 终端、机器人与具身智能层 -> 机器人链 -> 人形机器人 | 是 | - |
""",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--mapping",
            str(mapping_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    with output_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == REGISTRY_COLUMNS
    assert [row["l4_id"] for row in rows] == ["AI-L4-0001", "AI-L4-0002"]
    assert [row["canonical_topic"] for row in rows] == ["人形机器人", "人形机器人"]
    assert rows[0]["research_coordinate"] != rows[1]["research_coordinate"]
    assert rows[0]["l1"] == "全球映射与海外变量传导层"
    assert rows[0]["l2"] == "海外终端与具身主链"
    assert rows[0]["l3"] == "人形机器人"
    assert rows[0]["l4"] == "人形机器人"
    assert rows[0]["wiki_path"] == "topics/人形机器人.md"
    assert {row["schema_version"] for row in rows} == {"1"}


def test_builder_reuses_existing_ids_when_a_coordinate_is_inserted_in_the_middle(
    tmp_path: Path,
) -> None:
    mapping_path = tmp_path / "trade-system题材主卡映射表.md"
    output_path = tmp_path / "AI产业链L4注册表.csv"
    write_registry(
        output_path,
        [
            {
                "schema_version": "1",
                "l4_id": "AI-L4-0001",
                "l1": "主层",
                "l2": "分支",
                "l3": "坐标 A",
                "l4": "主题 A",
                "canonical_topic": "主题 A",
                "research_coordinate": "主层 -> 分支 -> 坐标 A",
                "wiki_path": "topics/主题 A.md",
            },
            {
                "schema_version": "1",
                "l4_id": "AI-L4-0002",
                "l1": "主层",
                "l2": "分支",
                "l3": "坐标 C",
                "l4": "主题 C",
                "canonical_topic": "主题 C",
                "research_coordinate": "主层 -> 分支 -> 坐标 C",
                "wiki_path": "topics/主题 C.md",
            },
        ],
    )
    write_text(
        mapping_path,
        """# mapping

| 规范主卡 | 类型 | 研究坐标 |
|---|---|---|
| 主题 A | 细分 | 主层 -> 分支 -> 坐标 A |
| 主题 B | 细分 | 主层 -> 分支 -> 坐标 B |
| 主题 C | 细分 | 主层 -> 分支 -> 坐标 C |
""",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--mapping",
            str(mapping_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    with output_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    ids_by_coordinate = {row["research_coordinate"]: row["l4_id"] for row in rows}
    assert [row["l4_id"] for row in rows] == ["AI-L4-0001", "AI-L4-0002", "AI-L4-0003"]
    assert ids_by_coordinate == {
        "主层 -> 分支 -> 坐标 A": "AI-L4-0001",
        "主层 -> 分支 -> 坐标 B": "AI-L4-0003",
        "主层 -> 分支 -> 坐标 C": "AI-L4-0002",
    }
