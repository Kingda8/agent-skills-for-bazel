"""Read reachable Git metadata and text blobs for bounded hygiene checks."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence


def run_git(root: Path, args: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
    """Run one read-only Git query without a shell."""

    return subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def decode_text(data: bytes) -> str | None:
    """Decode likely text while skipping ordinary binary files."""

    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        try:
            return data.decode("utf-16")
        except UnicodeDecodeError:
            return None
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def git_history_texts(root: Path) -> tuple[list[tuple[Path, str]], list[str]]:
    """Return text from reachable commits and unique blobs."""

    revisions = run_git(root, ["rev-list", "--all"])
    if revisions.returncode != 0:
        return [], ["git-history: unable to enumerate reachable commits"]

    texts: list[tuple[Path, str]] = []
    errors: list[str] = []
    seen_blobs: set[str] = set()
    for raw_revision in revisions.stdout.splitlines():
        revision = raw_revision.decode("ascii", errors="strict")
        commit = run_git(root, ["cat-file", "commit", revision])
        commit_text = decode_text(commit.stdout)
        if commit.returncode != 0 or commit_text is None:
            errors.append(f"git-history/{revision[:12]}: unable to read commit metadata")
        else:
            texts.append(
                (Path("git-history") / revision[:12] / "commit-metadata", commit_text)
            )

        tree = run_git(root, ["ls-tree", "-r", "-z", "--full-tree", revision])
        if tree.returncode != 0:
            errors.append(f"git-history/{revision[:12]}: unable to read tree")
            continue
        for raw_entry in tree.stdout.split(b"\0"):
            if not raw_entry:
                continue
            metadata, raw_name = raw_entry.split(b"\t", 1)
            fields = metadata.decode("ascii").split()
            if len(fields) != 3 or fields[1] != "blob":
                continue
            blob = fields[2]
            if blob in seen_blobs:
                continue
            seen_blobs.add(blob)
            content = run_git(root, ["cat-file", "blob", blob])
            text = decode_text(content.stdout)
            if content.returncode != 0 or text is None:
                continue
            name = raw_name.decode("utf-8", errors="replace")
            texts.append((Path("git-history") / revision[:12] / Path(name), text))
    return texts, errors
