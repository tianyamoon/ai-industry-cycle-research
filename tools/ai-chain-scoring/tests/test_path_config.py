from __future__ import annotations

import sys
from pathlib import Path

import pytest


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from path_config import RootResolutionError, resolve_configured_root, resolve_repo_path


def test_cli_root_takes_precedence_over_environment_and_discovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cli_root = tmp_path / "cli"
    env_root = tmp_path / "env"
    discovered_root = tmp_path / "discovered"
    for root in (cli_root, env_root, discovered_root):
        root.mkdir()
    (discovered_root / "AGENTS.md").write_text("# marker", encoding="utf-8")
    monkeypatch.setenv("AI_INDUSTRY_RESEARCH_ROOT", str(env_root))

    resolved = resolve_configured_root(
        cli_value=str(cli_root),
        env_name="AI_INDUSTRY_RESEARCH_ROOT",
        discovery_starts=[discovered_root],
        marker_paths=("AGENTS.md",),
        label="AI research repository",
    )

    assert resolved == cli_root.resolve()


def test_environment_root_takes_precedence_over_marker_discovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_root = tmp_path / "env"
    discovered_root = tmp_path / "discovered"
    env_root.mkdir()
    discovered_root.mkdir()
    (discovered_root / "AGENTS.md").write_text("# marker", encoding="utf-8")
    monkeypatch.setenv("AI_INDUSTRY_RESEARCH_ROOT", str(env_root))

    resolved = resolve_configured_root(
        cli_value=None,
        env_name="AI_INDUSTRY_RESEARCH_ROOT",
        discovery_starts=[discovered_root],
        marker_paths=("AGENTS.md",),
        label="AI research repository",
    )

    assert resolved == env_root.resolve()


def test_marker_discovery_walks_up_from_an_arbitrary_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_root = tmp_path / "project"
    nested = project_root / "tmp" / "runner"
    nested.mkdir(parents=True)
    (project_root / "AGENTS.md").write_text("# marker", encoding="utf-8")
    (project_root / "00_总控台").mkdir()
    monkeypatch.delenv("AI_INDUSTRY_RESEARCH_ROOT", raising=False)

    resolved = resolve_configured_root(
        cli_value=None,
        env_name="AI_INDUSTRY_RESEARCH_ROOT",
        discovery_starts=[nested],
        marker_paths=("AGENTS.md", "00_总控台"),
        label="AI research repository",
    )

    assert resolved == project_root.resolve()


def test_missing_root_never_falls_back_to_a_personal_machine_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("TRADE_SYSTEM_ROOT", raising=False)

    with pytest.raises(RootResolutionError, match="TRADE_SYSTEM_ROOT"):
        resolve_configured_root(
            cli_value=None,
            env_name="TRADE_SYSTEM_ROOT",
            discovery_starts=[tmp_path],
            marker_paths=("topics", "entities/stocks"),
            label="trade-system wiki",
        )


def test_relative_inputs_are_resolved_from_the_repository_root(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    assert resolve_repo_path("03_结果层/report.md", project_root) == (
        project_root / "03_结果层" / "report.md"
    ).resolve()
