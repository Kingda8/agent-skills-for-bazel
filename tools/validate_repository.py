#!/usr/bin/env python3
"""Run bounded structural and public-hygiene checks for Agent Skills for Bazel."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence

if __package__:
    from .history_scan import decode_text, git_history_texts, run_git
    from .plugin_manifest import validate_plugin_manifest
else:
    from history_scan import decode_text, git_history_texts, run_git
    from plugin_manifest import validate_plugin_manifest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT_NAME = "skills"
REQUIRED_ROOT_FILES = {
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    ".codex-plugin/plugin.json",
}
SKIPPED_DIRECTORIES = {
    ".git",
    ".pytest_cache",
    ".venv",
    ".plugin-eval",
    "__pycache__",
}
MAINTAINED_TEXT_SUFFIXES = {
    ".bzl",
    ".bazel",
    ".cff",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
    ".sh",
    ".ps1",
    ".bat",
    ".js",
    ".ts",
}
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])[A-Za-z]:[\\/](?![\\/])"
)
UNC_PATH_PATTERN = re.compile(r"(?<!\\)\\\\[A-Za-z0-9._$-]+\\[A-Za-z0-9._$ -]+")
USER_HOME_PATH_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    re.compile(r"/mnt/[A-Za-z]/Users/[A-Za-z0-9._-]+/", re.IGNORECASE),
    re.compile(r"[A-Za-z]:[\\/]Users[\\/][A-Za-z0-9._-]+[\\/]"),
)
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9.!#$%&'*+/=?^_{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+\b"
)
_SCAFFOLD_WORD = "TO" + "DO"
_REPLACE_MARKER = "REPLACE" + "_ME"
PLACEHOLDER_PATTERN = re.compile(
    r"\[(?:\s*" + _SCAFFOLD_WORD + r"\b|" + _SCAFFOLD_WORD
    + r":|PLACEHOLDER:)|<" + _SCAFFOLD_WORD + r">|" + _REPLACE_MARKER,
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    ("private key block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("OpenAI-style secret", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub-style token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("GitLab-style token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("Stripe live secret", re.compile(r"\bsk_live_[0-9A-Za-z]{20,}\b")),
    ("Slack-style token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("bearer credential", re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{20,}\b")),
    (
        "JWT-like credential",
        re.compile(r"\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{8,}\b"),
    ),
    (
        "assigned credential",
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\b"
            r"\s*[:=]\s*['\"][^'\"\s]{12,}['\"]"
        ),
    ),
)


@dataclass(frozen=True)
class PrivateTerm:
    value: str
    substring: bool = False


def repository_paths(root: Path) -> list[Path]:
    """Return tracked and untracked, non-ignored repository files."""

    result = run_git(root, ["ls-files", "--cached", "--others", "--exclude-standard", "-z"])
    paths: list[Path] = []
    if result.returncode == 0:
        for raw_name in result.stdout.split(b"\0"):
            if not raw_name:
                continue
            relative = Path(raw_name.decode("utf-8", errors="strict"))
            candidate = (root / relative).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                continue
            if candidate.is_file():
                paths.append(candidate)
        return sorted(set(paths))

    for candidate in root.rglob("*"):
        if not candidate.is_file():
            continue
        if any(part in SKIPPED_DIRECTORIES for part in candidate.relative_to(root).parts):
            continue
        paths.append(candidate)
    return sorted(paths)


def read_text(path: Path) -> str:
    """Read a maintained UTF-8 text file."""

    return path.read_text(encoding="utf-8")


def display_path(path: Path, root: Path) -> str:
    """Return a stable relative diagnostic without leaking another root."""

    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return PurePosixPath(*path.parts).as_posix()


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse top-level scalar fields from SKILL.md frontmatter."""

    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return {}
    end = normalized.find("\n---\n", 4)
    if end == -1:
        return {}

    values: dict[str, str] = {}
    for line in normalized[4:end].splitlines():
        if not line or line.startswith((" ", "\t")):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_-]+):\s*(.*?)\s*", line)
        if not match:
            continue
        key, value = match.groups()
        values[key] = value.strip("'\"")
    return values


def validate_frontmatter(path: Path, text: str, root: Path) -> list[str]:
    """Validate the bounded Agent Skills frontmatter contract."""

    label = display_path(path, root)
    normalized = text.replace("\r\n", "\n")
    errors: list[str] = []
    if not normalized.startswith("---\n"):
        return [f"{label}: missing opening frontmatter delimiter"]
    end = normalized.find("\n---\n", 4)
    if end == -1:
        return [f"{label}: missing closing frontmatter delimiter"]

    frontmatter = normalized[4:end]
    if len(frontmatter) > 2_500:
        errors.append(f"{label}: frontmatter is unexpectedly large")
    for number, line in enumerate(frontmatter.splitlines(), start=2):
        if not line or line.startswith("  "):
            continue
        if line.startswith("\t") or not re.fullmatch(r"[A-Za-z0-9_-]+:\s*.*", line):
            errors.append(f"{label}:{number}: malformed frontmatter line")
    return errors


def validate_markdown_links(path: Path, text: str, root: Path) -> list[str]:
    """Return errors for missing or escaping relative Markdown links."""

    errors: list[str] = []
    label = display_path(path, root)
    for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
        target = raw_target.strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target_without_fragment = target.split("#", 1)[0]
        if not target_without_fragment:
            continue
        resolved = (path.parent / target_without_fragment).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{label}: relative link escapes the repository: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{label}: missing relative link target: {target}")
    return errors


def is_allowed_email(email: str, public_emails: Sequence[str]) -> bool:
    """Return whether an email is an example, reserved, no-reply, or authorized."""

    lowered = email.casefold()
    if lowered in {value.casefold() for value in public_emails}:
        return True
    return lowered.endswith(
        (
            "@example.com",
            "@example.org",
            "@example.net",
            ".invalid",
            "@users.noreply.github.com",
            "@noreply.github.com",
        )
    )


def private_term_match(text: str, term: PrivateTerm) -> re.Match[str] | None:
    """Match a private term with token boundaries unless substring mode is explicit."""

    if term.substring:
        return re.search(re.escape(term.value), text, re.IGNORECASE)
    pattern = (
        r"(?<![A-Za-z0-9_])"
        + re.escape(term.value)
        + r"(?![A-Za-z0-9_])"
    )
    return re.search(pattern, text, re.IGNORECASE)


def match_line(text: str, match: re.Match[str]) -> int:
    """Return a one-based line number without echoing matched content."""

    return text.count("\n", 0, match.start()) + 1


def validate_public_hygiene(
    path: Path,
    text: str,
    private_terms: Sequence[PrivateTerm | str],
    root: Path = REPOSITORY_ROOT,
    public_emails: Sequence[str] = (),
) -> list[str]:
    """Return bounded credential, identity, path, and scaffold findings."""

    label = display_path(path, root)
    errors: list[str] = []

    for secret_label, pattern in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            errors.append(f"{label}:{match_line(text, match)}: possible {secret_label}")

    for path_label, pattern in (
        ("Windows absolute path", WINDOWS_ABSOLUTE_PATH_PATTERN),
        ("UNC path", UNC_PATH_PATTERN),
    ):
        match = pattern.search(text)
        if match:
            errors.append(f"{label}:{match_line(text, match)}: contains a {path_label}")

    for pattern in USER_HOME_PATH_PATTERNS:
        match = pattern.search(text)
        if match:
            errors.append(f"{label}:{match_line(text, match)}: contains a user-home path")
            break

    for email in EMAIL_PATTERN.findall(text):
        if not is_allowed_email(email, public_emails):
            position = re.search(re.escape(email), text)
            line = match_line(text, position) if position else 1
            errors.append(f"{label}:{line}: contains an unapproved public email")
            break

    placeholder = PLACEHOLDER_PATTERN.search(text)
    if placeholder:
        errors.append(
            f"{label}:{match_line(text, placeholder)}: contains an unfinished scaffold marker"
        )

    for raw_term in private_terms:
        term = raw_term if isinstance(raw_term, PrivateTerm) else PrivateTerm(raw_term)
        if not term.value:
            continue
        match = private_term_match(text, term)
        if match:
            errors.append(
                f"{label}:{match_line(text, match)}: contains a configured private term"
            )
    return errors


def parse_openai_yaml(path: Path, root: Path) -> tuple[dict[str, str], list[str]]:
    """Parse the tiny scalar OpenAI adapter shape without adding a dependency."""

    label = display_path(path, root)
    text = read_text(path).replace("\r\n", "\n")
    errors: list[str] = []
    values: dict[str, str] = {}
    lines = [
        line
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines or lines[0] != "interface:":
        return {}, [f"{label}: expected top-level interface mapping"]

    for number, line in enumerate(lines[1:], start=2):
        if "\t" in line or not line.startswith("  "):
            errors.append(f"{label}:{number}: malformed interface field indentation")
            continue
        match = re.fullmatch(r"  ([A-Za-z0-9_-]+):\s*(.+)", line)
        if not match:
            errors.append(f"{label}:{number}: malformed interface scalar")
            continue
        key, raw_value = match.groups()
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            errors.append(f"{label}:{number}: interface strings must be JSON-quoted")
            continue
        if not isinstance(value, str):
            errors.append(f"{label}:{number}: interface field must be a string")
            continue
        values[key] = value
    return values, errors


def validate_skill(skill_dir: Path, root: Path) -> list[str]:
    """Validate one skill's structure, frontmatter, links, and adapters."""

    errors: list[str] = []
    label = display_path(skill_dir, root)
    skill_file = skill_dir / "SKILL.md"
    license_file = skill_dir / "LICENSE.txt"
    agent_file = skill_dir / "agents" / "openai.yaml"

    if not skill_file.is_file():
        return [f"{label}: missing SKILL.md"]
    if not license_file.is_file():
        errors.append(f"{label}: missing LICENSE.txt for standalone distribution")

    text = read_text(skill_file)
    errors.extend(validate_frontmatter(skill_file, text, root))
    frontmatter = parse_frontmatter(text)
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    if not name:
        errors.append(f"{display_path(skill_file, root)}: frontmatter is missing name")
    elif not SKILL_NAME_PATTERN.fullmatch(name) or len(name) > 63:
        errors.append(f"{display_path(skill_file, root)}: invalid skill name")
    elif name != skill_dir.name:
        errors.append(f"{display_path(skill_file, root)}: name does not match its folder")

    if not description or len(description) < 40 or len(description) > 1_024:
        errors.append(
            f"{display_path(skill_file, root)}: description must be 40-1024 characters"
        )
    if frontmatter.get("license") != "MIT":
        errors.append(f"{display_path(skill_file, root)}: expected license: MIT")
    if len(text.splitlines()) > 400:
        errors.append(f"{display_path(skill_file, root)}: exceeds the 400-line limit")
    errors.extend(validate_markdown_links(skill_file, text, root))

    if agent_file.is_file():
        values, adapter_errors = parse_openai_yaml(agent_file, root)
        errors.extend(adapter_errors)
        required = {"display_name", "short_description", "default_prompt"}
        missing = sorted(required - values.keys())
        if missing:
            errors.append(
                f"{display_path(agent_file, root)}: missing fields: {', '.join(missing)}"
            )
        if name and name not in values.get("default_prompt", ""):
            errors.append(
                f"{display_path(agent_file, root)}: default prompt does not invoke $" + name
            )
        if len(values.get("display_name", "")) > 64:
            errors.append(f"{display_path(agent_file, root)}: display_name is too long")
        short_length = len(values.get("short_description", ""))
        if short_length and not 20 <= short_length <= 80:
            errors.append(
                f"{display_path(agent_file, root)}: short_description must be 20-80 characters"
            )
    return errors


def collect_private_terms(
    cli_terms: Sequence[str], cli_substrings: Sequence[str]
) -> list[PrivateTerm]:
    """Combine uncommitted CLI and environment private-term inputs."""

    environment_terms = os.environ.get("BAZEL_SKILLS_PRIVATE_TERMS", "")
    bounded = [*cli_terms, *environment_terms.split(",")]
    values = {
        PrivateTerm(value.strip(), False)
        for value in bounded
        if value.strip()
    }
    values.update(
        PrivateTerm(value.strip(), True)
        for value in cli_substrings
        if value.strip()
    )
    return sorted(values, key=lambda item: (item.value.casefold(), item.substring))


def collect_public_emails(cli_emails: Sequence[str]) -> list[str]:
    """Collect explicitly authorized public emails without printing them."""

    environment = os.environ.get("BAZEL_SKILLS_PUBLIC_EMAILS", "")
    return sorted(
        {
            value.strip()
            for value in [*cli_emails, *environment.split(",")]
            if value.strip()
        },
        key=str.casefold,
    )


def validate_repository(
    root: Path,
    private_terms: Sequence[PrivateTerm | str],
    public_emails: Sequence[str] = (),
    history: bool = False,
) -> list[str]:
    """Run repository validations and return a stable error list."""

    root = root.resolve()
    errors: list[str] = []
    for relative in sorted(REQUIRED_ROOT_FILES):
        if not (root / relative).is_file():
            errors.append(f"{relative}: missing required repository file")

    skills_root = root / SKILLS_ROOT_NAME
    if not skills_root.is_dir():
        return sorted(set([*errors, f"{SKILLS_ROOT_NAME}: missing skills directory"]))
    skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
    if not skill_dirs:
        errors.append(f"{SKILLS_ROOT_NAME}: no skills found")
    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir, root))

    if (root / ".codex-plugin" / "plugin.json").is_file():
        errors.extend(validate_plugin_manifest(root))

    for path in repository_paths(root):
        data = path.read_bytes()
        text = decode_text(data)
        if text is None:
            if path.suffix.lower() in MAINTAINED_TEXT_SUFFIXES:
                errors.append(f"{display_path(path, root)}: maintained text is not UTF-8")
            continue
        errors.extend(
            validate_public_hygiene(path, text, private_terms, root, public_emails)
        )
        if path.suffix.lower() == ".md":
            errors.extend(validate_markdown_links(path, text, root))
        if path.suffix.lower() in {".md", ".py"} and path.name != "SKILL.md":
            if len(text.splitlines()) > 600:
                errors.append(
                    f"{display_path(path, root)}: exceeds the 600-line maintained-file limit"
                )

    if history:
        history_texts, history_errors = git_history_texts(root)
        errors.extend(history_errors)
        for path, text in history_texts:
            errors.extend(
                validate_public_hygiene(path, text, private_terms, root, public_emails)
            )
    return sorted(set(errors))


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="Repository root to validate.",
    )
    parser.add_argument(
        "--private-term",
        action="append",
        default=[],
        help="Private token matched at identifier boundaries; may be repeated.",
    )
    parser.add_argument(
        "--private-substring",
        action="append",
        default=[],
        help="Private value matched as an exact substring; may be repeated.",
    )
    parser.add_argument(
        "--public-email",
        action="append",
        default=[],
        help="Explicitly authorized public email; may be repeated.",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Also scan reachable Git commit metadata and text blobs.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = args.root.resolve()
    private_terms = collect_private_terms(args.private_term, args.private_substring)
    public_emails = collect_public_emails(args.public_email)
    errors = validate_repository(root, private_terms, public_emails, args.history)

    if errors:
        print(f"Agent Skills for Bazel validation failed with {len(errors)} issue(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    skill_count = sum(1 for path in (root / SKILLS_ROOT_NAME).iterdir() if path.is_dir())
    history_status = " including reachable history" if args.history else ""
    print(
        "Agent Skills for Bazel bounded automated checks passed"
        f"{history_status}: {skill_count} skill(s), structure, links, metadata, "
        "and configured hygiene patterns found no issue. Manual semantic review remains required."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
