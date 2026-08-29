# Repository-first inspection

Use this reference before repository-specific analysis or execution, after a branch or workspace change, or whenever versions, effective configuration, remote services, or authorization boundaries may affect the answer. Skip it for generic conceptual guidance.

## Authority and scope

Read the repository's governing instructions and active task boundary before selecting work. The current user request defines mutation and execution authority; this skill does not widen it.

In a shared checkout:

- preserve unrelated and in-progress work;
- report when evidence is a moving snapshot;
- identify other worktrees or agents that may share source, output bases, caches, or servers;
- avoid shutdown, clean, cache reset, dependency refresh, or lock mutation unless the task authorizes it.

## Freeze enough provenance

Record only the provenance needed for the conclusion:

- repository root and applicable instruction files;
- revision, branch, and relevant dirty state;
- worktree relationships when another checkout may own the same branch or cache;
- host, execution, and target platform identities;
- Bazel version, startup options, named configs, and wrapper identity;
- target labels, universe, and configuration represented by existing evidence.

A dirty tree is not automatically invalid evidence. State whether the relevant files differ from the recorded revision and whether generated or untracked inputs affect the target.

## Inspect before invoking

Prefer narrow file discovery and reads before a broad Bazel command. Useful starting points include:

1. The nearest agent or contributor instructions and any active taskbook or release policy.
2. `git status --short --branch`, the relevant revision, and worktree relationships.
3. `.bazelversion`, system/user/workspace rc files and imports, wrappers, `MODULE.bazel`, `MODULE.bazel.lock`, and version-appropriate vendor or repository policy files.
4. The nearest `BUILD` or `BUILD.bazel` files and loaded `.bzl` entry points.
5. Current language-rule, toolchain, compiler, and runtime pins.
6. Relevant platforms, toolchain registrations, suites, generated targets, packaging targets, and CI wrappers.

Use repository search to locate candidate labels and declarations. Then choose `mod`, `query`, `cquery`, `aquery`, or execution based on the question rather than using a broad build as reconnaissance.

## Treat invocation as an identity

The following can materially change the graph or result:

- startup options and output-base identity;
- command options and named configs;
- repository environment and action environment;
- host, execution, and target platforms;
- toolchain resolution;
- remote execution or cache endpoints and trust policy;
- repository overrides, vendor mode, and lock behavior;
- wrapper-provided shell, SDK, authentication, or path setup.

Before calling an invocation read-only, inspect the effective rc and wrapper policy for:

- lockfile mode and any command that can rewrite resolution state;
- remote-cache writer or remote-execution endpoints;
- BES upload and remote build-event artifact policy;
- credentials, headers, environment inheritance, and output destinations;
- startup options that select another server, output base, or filesystem behavior.

A source-read-only task may still start a server, fetch repositories, write caches, upload action results, or publish BEP externally. Use a version-supported fail-closed lock policy and disable unapproved external writes only after confirming how the repository's wrapper and rc layers compose. Do not bypass an owning wrapper casually; it may also provide required correctness policy.

Prefer a checked-in wrapper when it supplies required environment or policy. Otherwise keep startup and command options explicit in the evidence.

## Classify command side effects

| Class | Examples | Working approach |
|---|---|---|
| Static inspection | source, config, lock, BUILD, and workflow reads | normally safe for read-only tasks |
| Bazel inspection | `mod`, `query`, `cquery`, `aquery`, `info` | may start a server, fetch repositories, update a lock under effective defaults, write/upload cache results, or stream BES events; preflight side effects |
| Analysis | `build --nobuild`, toolchain diagnostics | align configuration and platform with the question |
| Execution | scoped `build`, `test`, or `run` | begin with the smallest owning target |
| Repository maintenance | module tidy, lock refresh, vendoring | use only when dependency maintenance is in scope and review generated changes |
| External state | publish, push, sign, attest, deploy | require explicit intent, credentials, and a verifier |

## Resolve version drift honestly

When examples, remembered commands, upstream documentation, and repository pins differ:

1. establish the checked-in versions and active configuration;
2. consult documentation matching those versions when behavior matters;
3. distinguish current diagnosis from an upgrade proposal;
4. label unverified version assumptions instead of silently applying the newest syntax.

## First-inspection output

A useful short handoff states:

- the question and authorization boundary;
- revision and relevant working-tree state;
- the first evidence surface selected and why;
- the exact target, universe, configuration, and platform if already known;
- effective rc/wrapper, lock, remote writer/executor, and BES boundary when an invocation is contemplated;
- what would justify widening or executing;
- any shared-server, cache, worktree, or moving-snapshot caveat.
