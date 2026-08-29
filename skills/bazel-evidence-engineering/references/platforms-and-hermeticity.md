# Modules, platforms, toolchains, and hermeticity

Use this reference for platform selection, toolchain resolution, exec groups, runfiles, sandboxing, declared inputs, and reproducibility. Use [external-dependencies-and-upgrades.md](external-dependencies-and-upgrades.md) for Bzlmod, locks, repository rules, vendoring, and offline guarantees.

## Connect dependency identity to execution identity

- `MODULE.bazel` expresses direct module intent, module-extension inputs, and declared external artifacts.
- `MODULE.bazel.lock` records resolution and extension evaluation state.
- Language lockfiles and crate or npm translation inputs describe dependency graphs Bazel turns into targets.
- External file hashes and registry integrity metadata contribute to source identity.
- Lockfiles are useful SBOM inputs but do not by themselves describe the exact contents of a release artifact.

Dependency inputs become meaningful only through the selected platform, toolchain, and actions. Review module and language locks together with configured toolchain resolution when an external dependency changes by platform.

## Keep platform identities distinct

- **Host platform:** where Bazel itself runs.
- **Execution platform:** where an action runs and its tools execute.
- **Target platform:** where the built artifact is intended to run.

Use `cquery`, platform constraints, compatibility providers, `--toolchain_resolution_debug` or its version-matched equivalent, and configuration identity to explain configured behavior. Use `aquery` to verify the command, tool, exec group, environment, and declared inputs produced by that resolution.

Named platforms become useful when host autodetection no longer describes the build or release contract. Typical triggers include:

- formal evidence needs an explicit platform label;
- execution and target platforms differ;
- platform selection logic repeats across packages;
- cross-platform packages or OCI images become formal outputs;
- a remote cache or executor needs stable platform identity.

Model a dependency as a toolchain when actions need to resolve it by execution or target constraints. A pinned binary used as ordinary data may remain a target until toolchain resolution adds real value.

Use execution groups when one rule's actions require distinct toolchain sets or execution-platform contracts. Automatic execution groups can select per toolchain type, but ruleset adoption is version-specific. Keep a custom group when multiple tools must resolve on the same execution platform. Treat test execution-group behavior and constraint refinement as pinned-version features, not assumed universals.

Put executor-specific requirements in supported `exec_properties` on a platform or target, and verify what the remote service actually does with them. Avoid deprecated remote-property surfaces. Route remote acceptance, fallback, and output-download policy through [remote-build-infrastructure.md](remote-build-infrastructure.md).

## Audit the hermetic action model

An action is reproducible to the extent that its result follows from declared inputs, tools, relevant environment, command line, platform, and toolchain identity.

Look for:

- tools found through host `PATH` rather than labels or toolchains;
- reads from cwd, user home, system SDKs, network, wall clock, or random state;
- environment variables that affect results without entering the action key;
- generated outputs written outside declared paths;
- hardcoded output-tree, execroot, runfiles-tree, or workstation paths;
- platform-specific shell or launcher assumptions;
- repository rules or module extensions whose inputs are not pinned or recorded.

Use `aquery` for declared action shape and an execution log for comparable-run differences. A sandbox, isolated output base, or remote executor can expose hidden dependencies, but none alone proves hermeticity. A remote cache can also mask or amplify a bad action result; use a controlled cache lane rather than treating cache behavior as an isolation oracle.

For determinism, compare a named release artifact from two isolated builds with the same source, configuration, and platform. Compare digests and explain expected metadata differences rather than comparing an entire output tree indiscriminately.

## Treat runfiles as a runtime contract

- Put runtime data and tools on attributes that propagate them into runfiles.
- Resolve resources through the language or ruleset runfiles API, not cwd assumptions.
- Keep writable state in a runtime scratch location rather than the runfiles tree.
- Validate supported platforms when launcher or path semantics differ.

## Use sandboxing as evidence, not ceremony

Sandboxing is useful evidence for declared inputs and tools. Support differs by host and ruleset, so begin with a narrow canary before changing repository-wide configuration. When sandboxing is relaxed for diagnosis, keep the successful local result distinct from hermetic acceptance.

Apply privacy and retention policy to build actions, BEP, profiles, execution logs, caches, and packaging. Command lines, environment, paths, stdout, stderr, and outputs may persist beyond one invocation.

## Reverify after graph-shaping changes

Refresh platform and hermeticity conclusions after changes to:

- `.bazelversion`, `.bazelrc`, `MODULE.bazel`, or its lock;
- language rules, module extensions, external artifact pins, or registries;
- host, execution, or target platforms;
- CI images, remote cache or execution policy, shells, SDKs, or environment allowlists;
- package, OCI, SBOM, or release contracts.
