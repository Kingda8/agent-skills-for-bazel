# Rust, JavaScript, and TypeScript under Bazel

Use this reference when work touches `rules_rust`, crate_universe, `rules_js`, `rules_ts`, Node or pnpm integration, launchers, runfiles, or language-specific incrementality. Inspect current pins and targets before relying on version-sensitive behavior.

## Preserve one formal authority

- Bazel targets are the formal build, test, package, and release evidence when the repository declares Bazel as its control plane.
- Cargo, pnpm, compiler CLIs, and ecosystem test runners may provide fast diagnostics or editor support.
- Label direct-tool results as diagnostic and close the loop with the smallest relevant Bazel target.
- Keep language manifests, lockfiles, Bazel module state, generated repositories, and toolchain registration deliberately aligned during dependency changes.
- Prefer Bazel-resolved toolchains and runfiles over host output directories or globally installed language state.

## Rust working model

- Use `rust_library`, `rust_binary`, `rust_test`, and repository-defined macros as the dependency and acceptance surface.
- Inspect crate translation, feature unification, platform constraints, build scripts, proc macros, and generated source ownership when Cargo and Bazel behavior differ.
- Use `cquery` for configured dependencies and `aquery` for the resolved compiler, flags, environment, and declared inputs.
- Review broad globs and large libraries when one-file edits invalidate an expensive independent surface. Support structural changes with profile and consumer evidence.

Treat `build.rs` and procedural macros as third-party code executed on an execution platform, not passive source dependencies. Review generation defaults, tool and environment inputs, network/secret visibility, sandbox or remote eligibility, and cache trust. A configured target triple, a translated dependency set, a successful cross-compile, and an upstream host-support claim are four different pieces of evidence.

## Measure pipelined compilation

Pipelined compilation can let downstream Rust work begin from metadata before a full library artifact is complete. Extra actions and resource pressure mean that deep library graphs may benefit more than binaries, proc macros, build scripts, or small graphs.

Treat pipelining as a measured candidate:

1. Confirm support and known limitations in the checked-in `rules_rust` version.
2. Choose representative targets and incremental edits.
3. Hold source, platform, configuration, cache mode, and host load constant.
4. Compare cold, warm, and one-file incremental behavior.
5. Capture profiles, critical path, compiler and metadata actions, cache behavior, CPU and memory pressure, and diagnostics.
6. Validate representative supported platforms before making it shared configuration.

Adopt it only at the scope supported by repeatable benefit. Recheck after material graph, ruleset, toolchain, or CI hardware changes.

## JavaScript and TypeScript working model

- Package metadata and a package-manager lock feed Bazel's npm translation; use the package manager directly for an authorized lock refresh or scoped diagnostic.
- Use `ts_project`, JS library and test rules, declared npm labels, Node toolchains, and runfiles as the formal dependency surface.
- When TypeScript is on the critical path, inspect target size, invalidation, production and test grouping, type-check versus transpile structure, and generated traces before choosing a worker flag.
- Separating tests from production compilation can improve invalidation when module ownership supports a clean boundary.
- A direct TypeScript or test-runner invocation can shorten a reproducer but does not replace Bazel acceptance.

When `ts_project` uses a separate transpiler or no-emit arrangement, the primary target can succeed while type errors remain. Inspect the pinned `rules_ts` contract and make the generated `[name]_typecheck` or `[name]_typecheck_test` target part of formal acceptance when applicable. Transpilation success, type-check success, and runtime-test success are separate claims.

Treat npm lifecycle hooks as dependency code execution. Current `rules_js` behavior can run hooks as Bazel actions while relaxing sandboxing for compatibility. Review the package allowlist, environment, network and secret access, execution requirements, remote/cache policy, and generated outputs rather than assuming that "under Bazel" means hermetic.

## Gate persistent workers on correctness and evidence

Worker support can vary by ruleset, TypeScript version, host platform, execution mode, and action shape. Do not treat a worker flag as a universal speed switch.

Before enabling it:

1. Verify support and correctness notes for the repository's pinned ruleset and compiler.
2. Confirm enough eligible actions exist for startup reuse to matter.
3. Measure whether those actions are on the critical path.
4. Test state isolation, cancellation, diagnostics, cache keys, and platform behavior.
5. Define a named-config or default scope plus a simple rollback.

If support is absent or the action volume is too small, classify the capability as **Not applicable now / Reverify** and record the version or workload trigger for reconsideration.

## Investigate launcher and runfiles failures narrowly

- Keep runtime resources declared through `data`, executable providers, and runfiles lookup.
- Treat runfiles enablement and filesystem materialization choices as separate decisions.
- Use a checked-in wrapper when it establishes required shell or host environment; preserve equivalent startup and rc context for direct analysis commands.
- Begin with the smallest failing binary or test, its declared data, and configured actions before widening.

## Report language evidence

Record:

- exact target and reverse-dependent scope;
- ruleset and compiler or runtime versions;
- host, execution, and target platform;
- whether evidence is ecosystem-native diagnostic output or Bazel formal evidence;
- action shape and critical path when performance is involved;
- lock or generated-repository changes when dependencies are involved.

Also record dependency-code execution boundaries, the type-check target when TypeScript acceptance uses one, and whether platform evidence describes host support, target generation, cross-compilation, or executed tests.
