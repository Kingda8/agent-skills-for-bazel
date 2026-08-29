# External dependencies and upgrades

Use this reference for Bzlmod, module extensions, repository rules, lock behavior, repo mapping, vendoring, offline claims, registries, Bazelisk, or a Bazel/ruleset upgrade.

## Begin with the pinned dependency model

Bazel 9 is Bzlmod-only; the legacy WORKSPACE external-dependency mechanism and `bazel sync` are removed. Older repository pins may still use earlier behavior. Diagnose the checked-in version before proposing migration syntax.

Separate these layers:

- `MODULE.bazel`: direct module intent, overrides, extension usage, and declared repositories;
- module graph: version selection and compatibility resolution;
- module extensions: repository generation driven by tags, platform facts, and extension implementation;
- repository rules: external repository creation from declared and observed inputs;
- `MODULE.bazel.lock`: resolution and extension evaluation state for the Bazel version and invocation;
- language locks or translation inputs: crate, npm, or other ecosystem dependency identity;
- vendor, distdir, mirrors, and repository cache: different source-availability mechanisms.

None alone is a complete product SBOM or offline proof.

## Choose the `bazel mod` question precisely

Use version-matched subcommands rather than defaulting to one graph dump:

- `graph` for the resolved dependency graph;
- `deps` for dependency information about selected modules;
- `path` or `all_paths` for why a module is reachable;
- `explain` for selection and resolution reasoning;
- `show_repo` for a generated repository definition;
- `show_extension` for extension usage and generated repositories;
- `dump_repo_mapping` when an external tool or IDE needs the apparent-to-canonical mapping.

Machine-readable output is useful for guards, but output schemas and order are version-sensitive. Preserve the exact Bazel version and arguments.

## Keep repository names semantically correct

Source and Starlark should use apparent names as resolved in their repository context. Canonical repository names are implementation details and are not stable identifiers to hardcode. Use label APIs such as `Label.repo_name` when code needs repository identity, and provide repo mappings to external tools instead of reverse-engineering canonical names.

Respect strict dependency declarations: an extension-generated repository must be imported deliberately with `use_repo`, and a direct repository rule used from a module should use the supported `use_repo_rule` surface rather than recreating WORKSPACE-era global behavior.

## Treat lock behavior as a mutation boundary

The default lock mode in current Bazel lines can update `MODULE.bazel.lock`. A task described as read-only must inspect effective rc/wrapper flags and use a version-supported fail-closed lock mode when invoking dependency resolution.

Distinguish:

- inspection of the current lock and module graph;
- validation that errors rather than rewriting stale state;
- authorized lock refresh or module tidy;
- vendor or repository maintenance;
- an upgrade proposal with no mutation.

Review lock changes semantically: module selection, extension inputs/results, platform variants, generated repositories, and Bazel-version effects. Do not accept a large generated diff merely because a command exited successfully.

## Make module extensions reproducible where truthful

An extension's output follows its declared tags, module graph, relevant platform/environment facts, fetched inputs, and implementation. Use reproducibility metadata only when the extension meets the contract.

- Record generated repositories and root-module imports explicitly.
- Use persistent facts and a versioned facts contract only when supported and useful; `facts_version` is Bazel-version-gated.
- Ensure environment or host facts that affect repositories are declared through supported APIs.
- Use `REPO.bazel` metadata and ignored-directory controls where they clarify repository ownership.
- Test extension behavior with synthetic modules and the pinned Bazel versions.

Reproducible extension metadata can reduce lock churn; it does not prohibit the extension from accessing the network or prove source availability.

## Design repository rules as supply-chain code

Repository rules and extension implementations execute during dependency acquisition. Review:

- source URLs, mirrors, integrity hashes, signatures, and registry trust;
- declared environment inputs and watched files/directories;
- host executables or `ctx.execute` calls;
- network behavior, retries, authentication, and secret visibility;
- platform-dependent repository contents;
- generated BUILD or metadata ownership;
- cacheability and invalidation when inputs change.

Prefer content-addressed, declared inputs and maintained rulesets. A repository rule that discovers host state silently is a build input with no trustworthy identity.

## Separate lock, fetch, vendor, and offline guarantees

Use a tiered claim:

1. **Resolution frozen:** lock validation does not rewrite state. This does not guarantee all bytes are present.
2. **Inputs prefetched:** required repositories are available in a repository cache and a `--nofetch` canary succeeds for named targets.
3. **Controlled source closure:** vendor mode, distdir, or mirrors cover the intended target/config/platform closure with reviewed integrity.
4. **Offline proven:** an externally network-isolated, clean environment builds the named closure without undeclared host dependencies.

Vendor output depends on selected targets, configuration, platform, and Bazel version. Stale markers may cause refetch behavior, and Windows symlink support is an explicit host requirement. Bazel flags alone cannot prevent a repository implementation from using arbitrary host processes to reach the network; external isolation is the final proof.

## Upgrade in decision-sized stages

For an authorized Bazel or ruleset upgrade:

1. Freeze the current revision, supported platforms, active gates, and artifact identities.
2. Read release/migration notes for the current-to-target interval, not only the target release.
3. Update one control-plane layer where practical: Bazel, a ruleset family, a language lock, or a toolchain.
4. Inspect module resolution, lock and generated repository changes before broad execution.
5. Run loading/analysis and the smallest owning targets, then widen for graph-shaping impact and named gates.
6. Compare configured actions, platform/toolchain resolution, artifacts, and performance only where the change can affect them.
7. Record rollback, remaining incompatibilities, and the next reverify trigger.

Bazelisk and `.bazelversion` can make version selection repeatable, but CI and release must still record the resolved Bazel binary identity. Resolve ruleset versions from the channel the repository uses; a GitHub release may precede Bazel Central Registry availability.

Official starting points: [modules](https://bazel.build/external/module), [`bazel mod`](https://bazel.build/external/mod-command), [lockfiles](https://bazel.build/external/lockfile), [module extensions](https://bazel.build/external/extension), [vendor mode](https://bazel.build/external/vendor), and [Bazelisk](https://bazel.build/install/bazelisk).
