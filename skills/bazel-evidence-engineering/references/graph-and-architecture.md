# Graph, ownership, and architecture

Use this reference for target ownership, dependency direction, visibility, architecture boundaries, suite coverage, orphan detection, and target granularity.

## Select the graph layer

| Need | Surface | Interpretation |
|---|---|---|
| Declared targets and dependency paths | `query` | unconfigured possibilities |
| Platform or config-specific edges | `cquery` | configured target graph |
| Commands, inputs, outputs, tools, and mnemonics | `aquery` | registered action graph |
| Cross-run execution or cache differences | BEP/process metrics, profiles, compact execution logs | invocation outcomes, time, and executed-spawn behavior |

Useful query shapes, adapted to the real labels and universe:

```text
deps(//path/to:target)
rdeps(//..., //path/to:target)
rdeps(//..., //path/to:target, 1)
somepath(//consumer:target, //provider:target)
allpaths(//consumer:target, //provider:target)
kind(".*_test rule", //...)
tests(//tests:suite)
```

Use a bounded universe for `rdeps` when the question concerns one subsystem. `allpaths` can be large; begin with `somepath`, then expand when every path matters. Prefer stable machine-readable output when a guard or artifact will consume the result.

## Make configured-query semantics explicit

Serious configured ownership or architecture conclusions require more than replacing `query` with `cquery`.

- Set `--universe_scope` deliberately for expressions more complex than a simple target dependency closure; the top-level universe affects which configurations and transitions exist.
- Treat one label in different target, exec, or transitioned configurations as different configured target instances. Preserve configuration hashes or another stable configured identity.
- Decide whether aspects belong in the question and include them explicitly when their providers or actions matter.
- Decide whether implicit dependencies and tool dependencies belong in an ownership or policy conclusion; excluding them changes the graph being claimed.
- Inspect top-level compatibility and selected platform/toolchain context before calling a target absent or unreachable.
- Use transition output or version-matched configuration diagnostics when an edge changes configuration.

`tests(...)` is a `query` expansion surface, not a general `cquery` function. Static suite membership, configured compatibility, and the tests actually run by a command are separate evidence.

## Separate direct owners from transitive consumers

A full reverse-dependency query answers who can reach a dependency, not who declares the direct edge. Transitive consumers may be legitimate binaries, tests, launchers, generators, or tools.

For a sensitive dependency boundary:

1. Identify the provider, client, or capability label.
2. Inspect depth-one reverse dependencies to find direct Bazel owners.
3. Inspect full `rdeps`, `somepath`, or `allpaths` when transitive reachability matters.
4. Compare the configured graph with the architectural rule and reviewed exceptions.
5. Use text search to locate manifests, credentials, feature flags, dynamic loading, or comments that the Bazel graph does not model.
6. Discover existing guards before proposing a parallel enforcement path.

## Use visibility as an architecture surface

- New targets usually benefit from the narrowest visibility that serves known consumers.
- Package-level public defaults deserve explicit review because future targets inherit them silently.
- `package_group`, `__pkg__`, and `__subpackages__` can express stable ownership boundaries without repeating long allowlists.
- Target visibility and `.bzl` load visibility solve different problems; consider both when shared Starlark is an API.
- `exports_files` and source-file visibility can create paths around otherwise narrow rule visibility.

Enumerate current consumers before tightening a boundary. If a wider interface is intentional, record the owning abstraction and dependency direction rather than treating width alone as a defect.

## Choose target granularity from evidence

A useful target is cohesive in dependencies, visibility, ownership, platform, and test impact.

Consider splitting a target when:

- unrelated source groups have different consumers or dependency sets;
- tests and production sources invalidate the same expensive action without needing to;
- platform-specific sources create broad `select()` or compatibility logic;
- one change regularly recompiles a large independent surface;
- a narrower visibility boundary would clarify dependency direction.

Avoid one-target-per-file churn when graph overhead and maintenance outweigh measured reuse. Use profiles and invalidation evidence to support structural performance work.

Non-recursive `glob()` can fit homogeneous sources. Explicit lists or a guard may better expose new files in architecture-sensitive code. A file appearing in `srcs` does not prove it is reachable from a language module tree or contributes to the artifact.

## Find orphan sources, targets, and tests

Treat ownership and execution as separate questions:

- **Source ownership:** every product source, tool, contract, and generated input should be reachable through a reviewed Bazel target.
- **Target reachability:** a target may exist yet have no production consumer, suite, package, or release lane.
- **Test-lane ownership:** compare the set of test rules with expanded named suites, not only tags or BUILD-file text.

A practical orphan-test investigation:

1. Query all first-party test rules in the intended universe.
2. Discover and expand every formal suite or lane with `tests(...)`.
3. Compute the difference using query set operations or stable exported labels.
4. Review manual, external, platform-incompatible, live-provider, destructive, and intentionally standalone tests as possible exceptions.
5. Prefer an explicit lane or reviewed exception with an owner over silent omission.

Treat that difference as a static ownership check. Wildcards, `manual`, suite tag filtering, command flags, and configured compatibility can change the actual lane; verify formal execution with the canonical command and BEP.

For source or tool orphans, combine Bazel ownership queries with a repository file inventory. Account for generated, vendor, documentation, and intentionally local metadata so the result is decision-ready rather than a raw false-positive list.

## Enforce invariants at the earliest useful phase

Durable architecture checks can use:

- visibility and package boundaries that reject an invalid edge during analysis;
- query-based checks for dependency reachability or target and suite ownership;
- Starlark analysis tests for providers, toolchains, compatibility, or rule contracts;
- generated-contract checks comparing producer and checked-in consumer state;
- small Bazel tests for repository policies such as line or file-size thresholds.

Prefer the earliest Bazel phase that can express the invariant. A textual check remains appropriate when the policy concerns file content that providers and labels do not expose.

When the invariant requires a new macro, rule, aspect, provider, transition, or output group, use [starlark-rule-engineering.md](starlark-rule-engineering.md) to select the owning abstraction rather than embedding policy in an opaque query wrapper.

For a ratcheted policy, keep inherited exceptions exact and visible. New drift should fail; accepted debt should not silently grow. Synthetic negative fixtures can prove the evaluator catches orphan tests, unowned tools, forbidden owners, public surfaces, or affected-selection failures without inserting intentionally bad edges into the production graph.

## Report architecture evidence

Include:

- exact graph universe and configuration;
- direct owners separately from transitive consumers;
- relevant dependency paths when reachability is non-obvious;
- visibility or policy targets that enforce the rule;
- reviewed exceptions and their owner;
- whether the conclusion is structural, configured, executed, or inferred from text.
