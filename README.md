# Agent Skills for Bazel

**Advanced engineering judgment for Bazel-powered agents.**

Agent Skills for Bazel is an open-source Agent Skills project for engineering work where the hard part is not running a command, but choosing the evidence that can support a claim, preserving authorization, widening validation deliberately, and knowing when to stop.

Its flagship skill, [`bazel-evidence-engineering`](skills/bazel-evidence-engineering/SKILL.md), treats Bazel as an engineering evidence control plane rather than a command catalog. The skill follows the open [Agent Skills specification](https://agentskills.io/specification), keeps its core guidance portable across Codex, Claude Code, and Cursor, and carries a Codex-specific UI adapter separately.

> Open Agent Skills for evidence-driven Bazel engineering, validation, performance, and release decisions.

## Why this exists

Coding agents can usually run a command. The harder problem is knowing which command proves which claim, when broader validation is justified, and when a green local result is not release evidence.

This project packages that missing judgment as version-controlled skills. It is not a Bazel manual, beginner tutorial, prompt dump, CI framework, or substitute for repository policy. Repository-pinned versions, the owning control plane, and current evidence remain authoritative.

The project is for:

- platform, build, and release engineers responsible for Bazel repositories;
- teams using coding agents for formal engineering validation;
- skill authors who want to turn expert decision logic into portable, testable instructions.

## Flagship skill

| Skill | Purpose | Status |
|---|---|---|
| [`bazel-evidence-engineering`](skills/bazel-evidence-engineering/SKILL.md) | Select the correct Bazel evidence across repository identity, graphs, configuration, actions, execution, CI, artifacts, and provenance | Pre-1.0 public preview |

The Bazel skill covers:

| Plane | Decision surfaces |
|---|---|
| Repository and dependency truth | Bazel version, rc and wrapper identity, Bzlmod, lock policy, module extensions, repo mapping, vendor and offline guarantees |
| Graph and architecture | `query`, `cquery`, `aquery`, ownership, visibility, suites, configured universes, aspects, transitions, and analysis tests |
| Rule engineering | symbolic macros, rules, providers, depsets, actions, output groups, runfiles, exec groups, and configuration growth |
| Hermetic execution | platforms, toolchains, sandboxes, declared inputs, environment, reproducibility, and generated-code ownership |
| Distributed builds | local and remote caches, remote execution, dynamic execution, Build without the Bytes, fallback policy, and cache trust |
| Evidence and performance | BEP versus BES, profiles, execution logs, critical paths, affected targets, concurrency, and stop conditions |
| Delivery and trust | packages, OCI images, SBOM scope, provenance, signing, publication, and consumer verification |

It deliberately does not prescribe one remote-build vendor, one universal flag set, every language's basic Bazel syntax, or features that a repository's pinned version and rulesets do not support.

## How it thinks

1. Establish repository truth and the active authorization boundary.
2. Classify the engineering question and the surface Bazel actually owns.
3. Select the smallest evidence layer that can answer it.
4. Widen only for demonstrated propagation risk or a named acceptance gate.
5. Report provenance, uncertainty, evidence class, and the stop condition.

For example, a one-file TypeScript change should not automatically trigger `bazel test //...`. The skill first identifies the owning target, configured consumers, type-check contract, and relevant gate—then states exactly what would justify widening.

## Current Bazel baseline

The guidance was reviewed on **2026-08-29** against **Bazel 9.2.0**, the current Bazel 9 Active LTS at that review date. Bazel 10 was the rolling line. This is a maintenance baseline, not permission to override a repository pin.

See [the dated Bazel baseline](docs/bazel-current-baseline.md) for the official sources, current/experimental boundaries, ecosystem snapshot, and re-review triggers.

## Try it

Explicitly invoke the skill, then give it a real decision:

```text
$bazel-evidence-engineering

Audit whether this repository uses Bazel as a complete engineering control plane.
Stay read-only. Classify every relevant capability, show the evidence surface for
each conclusion, and do not stop at the first defect unless it invalidates the
remaining audit.
```

The skill also supports implicit discovery for work whose relevant build, test, artifact, or release surface is already Bazel-controlled or explicitly being evaluated for Bazel.

## Install

Copy the complete `skills/bazel-evidence-engineering/` directory into one supported location. Keep `SKILL.md`, `agents/`, `references/`, and `LICENSE.txt` together.

| Client | User-level installation | Repository-level installation | Explicit invocation |
|---|---|---|---|
| Codex | `~/.agents/skills/bazel-evidence-engineering/` | `<repo>/.agents/skills/bazel-evidence-engineering/` | `$bazel-evidence-engineering` |
| Claude Code | `~/.claude/skills/bazel-evidence-engineering/` | `<repo>/.claude/skills/bazel-evidence-engineering/` | `/bazel-evidence-engineering` |
| Cursor | `~/.agents/skills/bazel-evidence-engineering/` or `~/.cursor/skills/bazel-evidence-engineering/` | `<repo>/.agents/skills/bazel-evidence-engineering/` or `<repo>/.cursor/skills/bazel-evidence-engineering/` | `/bazel-evidence-engineering` |

For a repository used by all three clients, `.agents/skills/` serves Codex and Cursor; add the same complete skill under `.claude/skills/` for Claude Code. On Windows, `~` means the current user's profile directory.

Current client references: [Codex skill locations](https://developers.openai.com/codex/skills), [Claude Code skill locations](https://code.claude.com/docs/en/skills), and [Cursor Agent Skills](https://cursor.com/docs/skills).

The repository root also contains a [Codex plugin manifest](.codex-plugin/plugin.json), so the same source tree is ready to be distributed as a skill-only plugin after a public marketplace or repository URL exists. No public plugin, marketplace listing, or public remote has been published.

## Trust and maturity

- The flagship skill is instruction-only; installing it does not itself execute scripts or contact services.
- The repository validator checks structure, links, plugin metadata, common credential and private-path shapes, configured private terms, and reachable Git text history.
- Automated checks are bounded. They cannot prove the absence of semantic leakage; manual review remains required.
- Behavioral scenarios and hard-fail criteria are versioned with the skill. Cross-client measured results have not yet been published.
- Filesystem installation is documented for Codex, Claude Code, and Cursor. The OpenAI adapter is maintained for Codex; measured Claude Code and Cursor decision results remain pre-1.0 work until recorded in fresh sessions.

Run the local gates with Python 3.10 or newer:

```text
python tools/validate_repository.py --history
python -m unittest discover -s tests -v
```

Maintainers adapting private practice should pass private terms without committing them:

```text
python tools/validate_repository.py --history --private-term internal-project --private-term private-domain.example
```

The comma-separated `BAZEL_SKILLS_PRIVATE_TERMS` environment variable provides the same bounded input. Use `--private-substring` only when exact substring matching is intentional.

## Contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a skill or material rewrite.

**Bring a hard decision, not a longer prompt.** Especially useful contributions include a generalizable engineering decision, an evaluation that exposes a bad agent behavior, a recorded client-compatibility result, or a version change that moves a judgment boundary.

## Author and license

Created and maintained by **kingda8**, with contributions welcome under the [MIT License](LICENSE).

Bazel is a trademark of Google LLC. Agent Skills for Bazel is an independent project and is not affiliated with or endorsed by Google, the Bazel project, OpenAI, or any ruleset maintainer.
