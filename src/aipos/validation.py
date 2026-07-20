from __future__ import annotations

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
