"""Validate the bounded skill-only Codex plugin manifest used by this project."""

from __future__ import annotations

import json
import re
from pathlib import Path


PLUGIN_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def validate_plugin_manifest(root: Path) -> list[str]:
    """Validate the repository's skill-only Codex plugin manifest."""

    path = root / ".codex-plugin" / "plugin.json"
    label = ".codex-plugin/plugin.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [f"{label}: invalid JSON manifest: {error.__class__.__name__}"]

    errors: list[str] = []
    name = data.get("name")
    if not isinstance(name, str) or not PLUGIN_NAME_PATTERN.fullmatch(name):
        errors.append(f"{label}: invalid or missing plugin name")
    version = data.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        errors.append(f"{label}: version must be strict semver")
    if not isinstance(data.get("description"), str) or not data["description"].strip():
        errors.append(f"{label}: missing description")
    author = data.get("author")
    if not isinstance(author, dict) or not isinstance(author.get("name"), str):
        errors.append(f"{label}: missing author.name")
    if data.get("license") != "MIT":
        errors.append(f"{label}: expected MIT license")
    if "hooks" in data:
        errors.append(f"{label}: unsupported hooks field")

    skills_path = data.get("skills")
    if not isinstance(skills_path, str):
        errors.append(f"{label}: missing skills path")
    else:
        resolved = (root / ".codex-plugin" / skills_path).resolve()
        if not resolved.is_dir():
            resolved = (root / skills_path).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{label}: skills path escapes repository")
        else:
            if not resolved.is_dir():
                errors.append(f"{label}: skills path does not exist")

    interface = data.get("interface")
    required_interface = {
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "capabilities",
        "defaultPrompt",
    }
    if not isinstance(interface, dict):
        errors.append(f"{label}: missing interface object")
        return errors
    missing = sorted(required_interface - interface.keys())
    if missing:
        errors.append(f"{label}: missing interface fields: {', '.join(missing)}")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        errors.append(f"{label}: defaultPrompt must contain 1-3 strings")
    elif any(not isinstance(value, str) or len(value) > 128 for value in prompts):
        errors.append(f"{label}: defaultPrompt entries must be strings of at most 128 chars")
    for field in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
        value = interface.get(field)
        if value is not None and (
            not isinstance(value, str) or not value.startswith("https://")
        ):
            errors.append(f"{label}: {field} must use https")
    return errors
