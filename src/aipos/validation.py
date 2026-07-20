from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import PurePosixPath


def require_non_empty_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def validate_artifact_path(value: object, field_name: str = "path") -> str:
    path = require_non_empty_string(value, field_name)
    if "\\" in path:
        raise ValueError(f"{field_name} must use forward slashes: {path}")
    if path.endswith("/"):
        raise ValueError(f"{field_name} must point to a file-like artifact path: {path}")

    parsed = PurePosixPath(path)
    if parsed.is_absolute():
        raise ValueError(f"{field_name} must be project-relative: {path}")
    if any(part in {"", ".", ".."} for part in parsed.parts):
        raise ValueError(f"{field_name} must not contain empty, current, or parent segments: {path}")
    return path


def artifact_path_matches_contract(path: str, contract_path: str) -> bool:
    if not _has_glob(contract_path):
        return path == contract_path
    return _match_parts(tuple(PurePosixPath(path).parts), tuple(PurePosixPath(contract_path).parts))


def _match_parts(path_parts: tuple[str, ...], pattern_parts: tuple[str, ...]) -> bool:
    if not pattern_parts:
        return not path_parts

    pattern = pattern_parts[0]
    if pattern == "**":
        return _match_parts(path_parts, pattern_parts[1:]) or bool(
            path_parts and _match_parts(path_parts[1:], pattern_parts)
        )

    if not path_parts:
        return False
    return fnmatchcase(path_parts[0], pattern) and _match_parts(path_parts[1:], pattern_parts[1:])


def _has_glob(path: str) -> bool:
    return any(character in path for character in "*?[")
