from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.validate_repository import (
    PrivateTerm,
    git_history_texts,
    parse_frontmatter,
    parse_openai_yaml,
    repository_paths,
    validate_markdown_links,
    validate_plugin_manifest,
    validate_public_hygiene,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class FrontmatterTests(unittest.TestCase):
    def test_parses_top_level_scalars_and_ignores_nested_metadata(self) -> None:
        text = (
            "---\n"
            "name: evidence-skill\n"
            "description: Choose evidence for a bounded engineering task.\n"
            "metadata:\n"
            "  author: maintainer\n"
            "---\n"
        )

        result = parse_frontmatter(text)

        self.assertEqual(result["name"], "evidence-skill")
        self.assertEqual(
            result["description"],
            "Choose evidence for a bounded engineering task.",
        )
        self.assertEqual(result["metadata"], "")
        self.assertNotIn("author", result)


class PublicHygieneTests(unittest.TestCase):
    def test_detects_windows_and_user_path_without_storing_one(self) -> None:
        sample = "C" + ":\\Users\\Alice\\private\\config.txt"
        path = Path("sample.md")

        errors = validate_public_hygiene(path, sample, [])

        self.assertTrue(any("absolute path" in error for error in errors))
        self.assertTrue(any("user-home path" in error for error in errors))

    def test_detects_multiple_credential_shapes_constructed_at_runtime(self) -> None:
        samples = [
            "sk-" + ("x" * 32),
            "glpat-" + ("a" * 24),
            "Bearer " + ("b" * 32),
            "eyJ" + ("c" * 16) + "." + ("d" * 16) + "." + ("e" * 12),
        ]

        for sample in samples:
            with self.subTest(prefix=sample[:6]):
                errors = validate_public_hygiene(Path("sample.txt"), sample, [])
                self.assertTrue(any("possible" in error for error in errors))

    def test_private_terms_use_identifier_boundaries_by_default(self) -> None:
        clean = validate_public_hygiene(
            Path("sample.md"),
            "A sentence around the boundary.",
            [PrivateTerm("Round")],
        )
        found = validate_public_hygiene(
            Path("sample.md"),
            "The Round boundary is explicit.",
            [PrivateTerm("Round")],
        )

        self.assertFalse(any("private term" in error for error in clean))
        self.assertTrue(any("private term" in error for error in found))

    def test_private_substring_mode_is_explicit(self) -> None:
        errors = validate_public_hygiene(
            Path("sample.md"),
            "A sentence around the boundary.",
            [PrivateTerm("Round", substring=True)],
        )

        self.assertTrue(any("private term" in error for error in errors))

    def test_public_email_allowlist_is_separate_from_identity(self) -> None:
        sample = "maintainer" + "@" + "public.test"
        blocked = validate_public_hygiene(Path("sample.md"), sample, [])
        allowed = validate_public_hygiene(
            Path("sample.md"),
            sample,
            [],
            public_emails=[sample],
        )

        self.assertTrue(any("unapproved public email" in error for error in blocked))
        self.assertFalse(any("unapproved public email" in error for error in allowed))

    def test_reserved_invalid_email_is_allowed(self) -> None:
        sample = "contributors" + "@" + "project.invalid"

        errors = validate_public_hygiene(Path("sample.md"), sample, [])

        self.assertFalse(any("unapproved public email" in error for error in errors))

    def test_plain_todo_word_is_not_an_unfinished_scaffold(self) -> None:
        clean = validate_public_hygiene(
            Path("sample.md"),
            "A TODO can be an intentional backlog topic.",
            [],
        )
        unfinished = validate_public_hygiene(
            Path("sample.md"),
            "[" + "TO" + "DO: replace this before release]",
            [],
        )

        self.assertFalse(any("scaffold" in error for error in clean))
        self.assertTrue(any("scaffold" in error for error in unfinished))

    def test_alternate_root_diagnostics_do_not_emit_absolute_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "nested" / "sample.md"
            page.parent.mkdir()
            sample = "C" + ":\\private\\config.txt"

            errors = validate_public_hygiene(page, sample, [], root=root)

            self.assertTrue(errors)
            self.assertTrue(all(directory not in error for error in errors))
            self.assertTrue(all(error.startswith("nested/sample.md") for error in errors))


class FileInventoryTests(unittest.TestCase):
    def test_fallback_inventory_includes_extensionless_and_env_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "BUILD").write_text("package(default_visibility = [])", encoding="utf-8")
            (root / ".env").write_text("SAFE_VALUE=example", encoding="utf-8")
            (root / "script.ps1").write_text("Write-Output 'safe'", encoding="utf-8")

            names = {path.name for path in repository_paths(root)}

            self.assertEqual(names, {"BUILD", ".env", "script.ps1"})


class MarkdownLinkTests(unittest.TestCase):
    def test_reports_missing_relative_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "page.md"
            page.write_text("[missing](references/missing.md)", encoding="utf-8")

            errors = validate_markdown_links(page, page.read_text(encoding="utf-8"), root)

            self.assertEqual(len(errors), 1)
            self.assertIn("missing relative link target", errors[0])


class MetadataTests(unittest.TestCase):
    def test_current_openai_adapter_parses_as_quoted_scalars(self) -> None:
        path = (
            REPOSITORY_ROOT
            / "skills"
            / "bazel-evidence-engineering"
            / "agents"
            / "openai.yaml"
        )

        values, errors = parse_openai_yaml(path, REPOSITORY_ROOT)

        self.assertEqual(errors, [])
        self.assertIn("$bazel-evidence-engineering", values["default_prompt"])

    def test_current_plugin_manifest_passes_bounded_schema(self) -> None:
        self.assertEqual(validate_plugin_manifest(REPOSITORY_ROOT), [])

    def test_plugin_name_is_independent_of_clone_folder(self) -> None:
        source = REPOSITORY_ROOT / ".codex-plugin" / "plugin.json"
        manifest = json.loads(source.read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "my-bazel-skills"
            (root / ".codex-plugin").mkdir(parents=True)
            (root / "skills").mkdir()
            (root / ".codex-plugin" / "plugin.json").write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )

            errors = validate_plugin_manifest(root)

        self.assertEqual(errors, [])


class GitHistoryTests(unittest.TestCase):
    def test_reachable_history_includes_deleted_text_blob(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.run_git(root, "init")
            self.run_git(root, "config", "user.name", "Example")
            self.run_git(root, "config", "user.email", "example@example.com")
            page = root / "old.txt"
            marker = "historical-" + "marker"
            page.write_text(marker, encoding="utf-8")
            self.run_git(root, "add", "old.txt")
            self.run_git(root, "commit", "-m", "add old")
            page.unlink()
            self.run_git(root, "add", "-u")
            self.run_git(root, "commit", "-m", "remove old")

            texts, errors = git_history_texts(root)

            self.assertEqual(errors, [])
            self.assertTrue(any(marker in text for _, text in texts))

    @staticmethod
    def run_git(root: Path, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


if __name__ == "__main__":
    unittest.main()
