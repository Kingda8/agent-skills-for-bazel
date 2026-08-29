# Current Bazel baseline

Agent Skills for Bazel keeps its dated Bazel and ecosystem compatibility record inside the distributable skill:

- [current Bazel and ecosystem boundary](../skills/bazel-evidence-engineering/references/current-ecosystem.md)
- [external dependencies and upgrade discipline](../skills/bazel-evidence-engineering/references/external-dependencies-and-upgrades.md)
- [Starlark rule-engineering boundary](../skills/bazel-evidence-engineering/references/starlark-rule-engineering.md)
- [remote build infrastructure boundary](../skills/bazel-evidence-engineering/references/remote-build-infrastructure.md)

At the 2026-08-29 review, Bazel 9.2.0 was the Bazel 9 Active LTS baseline and Bazel 10 was the rolling line. Repository pins still outrank this snapshot.

The maintainer must refresh the dated reference when the Active LTS changes, a named ruleset changes its compatibility floor or lifecycle state, an official default used by the skill changes, or a behavioral evaluation exposes stale advice.

Primary upstream entry points:

- [Bazel release model](https://bazel.build/release)
- [Bazel 9 announcement](https://blog.bazel.build/2026/01/20/bazel-9.html)
- [Bazel 9.2.0 release notes](https://github.com/bazelbuild/bazel/releases/tag/9.2.0)
- [Bazel Central Registry](https://registry.bazel.build/)

This is a compatibility review, not a claim that every current or experimental Bazel capability should be enabled.
