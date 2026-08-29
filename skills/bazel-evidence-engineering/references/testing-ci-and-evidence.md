# Tests, CI, and formal evidence

Use this reference for target selection, suites and tags, timeouts and exclusivity, affected-target lanes, BEP, profiles, execution logs, cache reporting, and cross-platform acceptance.

## Rediscover the current gate

Treat remembered target lists as hints. Before a formal conclusion, inspect the active task or release policy, workflow, runner, suite definitions, platform matrix, and current revision.

Graph queries show what targets and suites contain. BEP and result artifacts show what an invocation actually executed. Keep those claims separate.

## Match validation to propagation risk

Use the validation ladder in `SKILL.md`. This reference adds CI and result semantics rather than maintaining a second copy of that ladder.

A shared BUILD file, `.bzl` macro, module, lock, platform, toolchain, suite, guard, or CI change usually justifies broader analysis than an isolated source edit. A scoped or repository-wide `build --nobuild` can catch syntax, label, load, and analysis failures without executing actions.

Full execution is most valuable when it answers a named acceptance risk, not when used as general reassurance.

## Give every important test an owner

Every test intended to matter should have an execution owner such as presubmit, full, external or live, platform-specific, release, or an explicitly reviewed standalone lane.

To investigate suite gaps:

1. Query the first-party test-rule universe.
2. Discover formal suites from BUILD files, workflows, runners, and task policy.
3. Expand suites with `tests(...)` and compare their union with the test universe.
4. Review platform incompatibility and manual, external, provider-backed, destructive, or intentionally standalone semantics.
5. Express intentional exceptions with an owner and trigger.

Tags describe scheduling or environment semantics; they do not prove a test belongs outside every formal lane.

`query tests(...)` gives static suite expansion. Wildcards, `manual`, suite tags, command flags, and configured compatibility can change actual execution, and `cquery` does not provide the same `tests()` expansion. Grant lane authority only from the canonical command/configuration and complete BEP.

## Interpret tags, size, timeout, and exclusivity

- Audit `manual`, `external`, `exclusive`, `exclusive-if-local`, large sizes, and long timeouts in context.
- `exclusive` serializes a test and constrains remote execution. Inspect ports, temp directories, child processes, and other shared resources before retaining or replacing it.
- `exclusive-if-local` may fit contention that exists only on a local executor.
- Size and timeout should reflect observed runtime and leave CI time to persist the first useful failure evidence.
- A test timeout should usually be shorter than the outer job timeout so BEP and sanitized summaries can finish.
- Sharding helps only when the runner implements Bazel's sharding protocol and the work is divisible.
- `flaky` and `runs_per_test` are diagnostic or acceptance tools; pair them with a concrete hypothesis or consecutive-run criterion.

## Treat affected-target selection as a confidence system

Capture base and head revision, Bazel version, configuration, platform, selector version, and impacted labels. Expand to the full gate when confidence falls because of:

- module, lock, `.bazelrc`, BUILD, or `.bzl` changes;
- platform, toolchain, suite, guard, generated-contract, or CI changes;
- deletions, renames, query failures, unowned inputs, or an unexpectedly empty selection.

Changed-file-to-rdeps queries are useful hypotheses. Graph-hash tools model more cases but still inherit configuration and modeling assumptions. Fast feedback and complete promotion evidence can coexist.

## Define a fail-closed BEP evidence contract

For formal execution evidence, capture as applicable:

- revision, relevant clean or dirty state, and base revision for diff selection;
- Bazel version, startup options, named configs, platform, and toolchain identity;
- requested patterns and the expanded, sorted target or test-set digest;
- Bazel invocation ID, start time, duration, exit code, aborted reason, and terminal state;
- executed, cached, and unknown test or action counts with definitions;
- first failed target, test, or action, mnemonic, status, stage, and typed detail available from Bazel;
- artifact labels, URIs or digests, and sanitized evidence location;
- whether matrix entries used the same source and intended target set.

Read streaming BEP through end-of-file because summary events can follow `BuildFinished`. Require every announced child event needed for the evidence graph to appear. Treat parse errors, an open announced-event graph, missing terminal events, zero discovered tests when tests were expected, or mismatched platform target sets as evidence gaps rather than green results.

Raw BEP, profiles, execution logs, command lines, paths, test logs, and action outputs can contain sensitive material. Prefer a fixed-schema sanitized long-lived summary and controlled, short-lived storage for raw diagnostics.

## Separate BEP semantics from BES delivery

BEP is the event graph describing an invocation. BES is a gRPC transport that publishes BEP bytes externally. A successful Bazel command does not prove that an asynchronous BES stream is complete, acknowledged, retained, or able to resolve referenced artifacts.

For formal evidence, wait for upload completion or verify backend completeness. Treat fully asynchronous delivery as provisional. Verify required artifact URIs under the selected build-event upload policy and retention period. A BES results page is not itself an artifact store or release gate.

## Define coverage as its own gate

`bazel coverage` is not ordinary test success with a percentage attached. Record instrumented target filters, language support, platform and remote-execution behavior, cached-test semantics, report generation/merge targets, and which sources are excluded.

Keep three claims distinct: tests passed, coverage data was produced, and a complete policy report met a threshold. Verify that remote outputs needed for coverage merge are materialized or resolvable, and that a cached test result cannot silently erase required instrumentation evidence.

## Report cache evidence precisely

Define whether a cache rate refers to tests, actions, repository fetches, a local disk cache, or a remote cache. BEP metrics and execution logs can support action-level evidence; a cached test-summary count does not describe compiler or filesystem reuse.

Review which events can restore or save CI caches, whether untrusted changes are read-only consumers, namespace identity, retained outputs, invalidation, and poisoned-entry response.

## Keep acceptance states separate

The same revision is necessary but may not be sufficient across platforms. Compare target-set identity, configs, platform and toolchain identity, and result schema.

Report local-only, platform-specific, matrix-green, package-green, published, and live acceptance as distinct states. A local container build does not prove a Bazel release target, an uploaded image, a signed attestation, or a running service.

## Stop when the gate is answered

Conclude when selected evidence proves the named gate or a blocker prevents further decision-relevant work. For an explicitly broad audit, continue independent inventory after a first defect unless that defect invalidates the remaining evidence. Repeat an unchanged broad suite only for a documented flake investigation, changed environment/input, or explicit consecutive-run requirement.
