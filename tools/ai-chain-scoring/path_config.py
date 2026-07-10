from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


class RootResolutionError(RuntimeError):
    """Raised when a repository root cannot be resolved without a machine-specific fallback."""


def _validated_directory(raw: str, source: str, label: str) -> Path:
    path = Path(raw).expanduser().resolve()
    if not path.is_dir():
        raise RootResolutionError(f"{label} configured by {source} is not a directory: {path}")
    return path


def _candidate_ancestors(starts: Iterable[Path]) -> Iterable[Path]:
    seen: set[Path] = set()
    for raw_start in starts:
        start = raw_start.expanduser().resolve()
        if start.is_file():
            start = start.parent
        for candidate in (start, *start.parents):
            if candidate not in seen:
                seen.add(candidate)
                yield candidate


def resolve_configured_root(
    *,
    cli_value: str | None,
    env_name: str,
    discovery_starts: Iterable[Path],
    marker_paths: tuple[str, ...],
    label: str,
) -> Path:
    """Resolve a root using CLI > environment > marker discovery."""

    if cli_value:
        return _validated_directory(cli_value, "command line", label)

    env_value = os.environ.get(env_name)
    if env_value:
        return _validated_directory(env_value, env_name, label)

    for candidate in _candidate_ancestors(discovery_starts):
        if all((candidate / marker).exists() for marker in marker_paths):
            return candidate

    markers = ", ".join(marker_paths)
    raise RootResolutionError(
        f"Unable to resolve {label}. Pass its command-line option, set {env_name}, "
        f"or run below a directory containing: {markers}"
    )


def resolve_repo_path(raw: str, repository_root: Path) -> Path:
    path = Path(raw).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (repository_root / path).resolve()
