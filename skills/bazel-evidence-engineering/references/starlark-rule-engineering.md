# Starlark rule engineering

Use this reference when designing or reviewing macros, rules, providers, aspects, actions, build settings, transitions, toolchains, exec groups, output groups, or analysis tests.

## Start from Bazel's phase model

- **Loading:** BUILD files and loaded Starlark declare targets. Macros expand declarations but do not inspect configured providers or run actions.
- **Analysis:** rules and aspects resolve attributes, configurations, platforms, and toolchains; create providers and register actions.
- **Execution:** Bazel runs registered actions according to strategies, caches, and execution platforms.

Put a policy at the earliest phase that has the information to express it. Do not force execution to prove a loading or analysis invariant.

## Choose the smallest abstraction that owns the behavior

| Need | Prefer | Avoid |
|---|---|---|
| Repeated target declarations with no new action semantics | symbolic macro | a custom rule that merely forwards fields |
| A new build contract, provider, action, or toolchain use | rule | opaque macro-generated action tricks |
| Cross-cutting traversal of existing targets | aspect | rewriting every target or global text scans |
| User-selectable typed configuration | Starlark build setting | unconstrained string defines |
| Dependency-specific configuration change | narrow transition | global configuration forks |
| External dependency graph generation | module extension or repository rule | host scripts outside dependency resolution |
| Same rule actions requiring different execution platforms | exec groups or AEGs | host-path tool selection |

Prefer composition over a framework layer. A repository macro may be its public build API; preserve that intent while keeping the underlying rule semantics inspectable.

## Prefer symbolic macros for declaration APIs

When the pinned Bazel supports them, prefer symbolic macros over new legacy macros for typed attributes, visibility semantics, naming contracts, and future lazy-expansion compatibility.

- Keep macro attributes purposeful and inherit only fields that remain part of the public contract.
- Respect macro visibility and generated-target naming rules.
- Use finalizers only for a real package-wide need; they weaken locality and future lazy behavior.
- Do not claim lazy macro expansion as an active optimization until the pinned Bazel implements and enables it.

A macro cannot inspect providers from configured dependencies. If the abstraction must reason about providers or register actions, it is a rule or aspect problem.

## Design rule contracts through providers

- Attributes declare dependencies, inputs, tools, and configuration. Avoid hidden label lookup and host discovery.
- Custom providers should expose a small stable semantic contract rather than raw implementation files.
- Use `DefaultInfo` intentionally for default outputs, executable identity, and runfiles; do not overload it as the only interface when downstream rules need structured data.
- Use `OutputGroupInfo` for opt-in outputs such as IDE metadata, reports, generated interfaces, or validation artifacts that should not inflate every default build.
- Keep files and providers aligned with dependency direction. Generated code needs an owning producer target and explicit consumers.

Use depsets for transitive collections. Preserve their order semantics, avoid flattening during analysis, and use direct/transitive construction rather than repeated list concatenation. Flatten at an action or reporting boundary only when a concrete consumer requires a list.

## Register hermetic actions

- Declare every input, output, executable, and tool through labels, providers, attributes, or toolchains.
- Build command lines with `Args` so Bazel can defer expansion and use param files where appropriate.
- Keep environment inputs narrow and explicit; host `PATH`, cwd, user home, wall clock, random state, and network are not invisible conveniences.
- Write only declared outputs. Keep temporary work under the action's execution environment.
- Give actions stable, meaningful mnemonics and progress messages without exposing secrets.
- Add execution requirements only for a demonstrated constraint, with an owner and fallback.

Use `aquery` to inspect registered commands, tools, environment, inputs, outputs, and exec groups. Use an execution log for executed-spawn evidence and a profile for cost.

## Use aspects for justified cross-cutting work

Aspects can propagate along selected attributes, consume and provide structured providers, register actions, and expose output groups. Good uses include IDE metadata, policy facts, linting, interface extraction, or provenance collection across heterogeneous rule types.

Before adopting one, define:

- the propagation edges and required providers;
- whether the aspect observes or creates outputs;
- the output group and explicit consumer;
- configuration and toolchain behavior;
- analysis and action growth across a representative graph.

Do not use an aspect when an ordinary dependency, macro, query, or dedicated target owns the behavior more clearly. Include aspects explicitly when a configured query or action audit must see them.

## Treat transitions as configuration multipliers

Prefer ordinary attributes, `select()`, platforms, and typed build settings before a custom transition. When a dependency really needs a different configuration:

- declare exactly which settings are read and written;
- keep transitions 1:1 when possible;
- expect split transitions and compositions to multiply configured target instances;
- inspect configuration hashes and edges with `cquery --transitions` and version-matched configuration diagnostics;
- test allowlisted package use, affected platforms, and output disambiguation;
- measure analysis memory, time, cache effects, and remote action identity.

Composition helpers such as `transition.and_then` are version-gated. A convenient composition does not remove Cartesian-product risk.

## Resolve tools through toolchains and execution groups

Use toolchains when a rule needs a tool selected by execution or target constraints. Keep target, execution, and host identities distinct.

- A custom exec group is useful when related tools must share one execution platform or need a named strategy boundary.
- Automatic execution groups can select an execution platform per toolchain type, but adoption differs by ruleset and Bazel version.
- Tests may use a dedicated test execution group in current Bazel lines; verify the pinned ruleset's behavior.
- Put executor-specific requirements in supported platform or target `exec_properties`, not deprecated remote-property fields.

Inspect resolution with configured queries and toolchain diagnostics, then verify registered and executed actions. Do not assume every ruleset has completed its AEG migration.

## Test analysis behavior directly

Different tests prove different things:

- `build --nobuild` proves the selected graph can load and analyze.
- an analysis test can assert providers, actions, failure messages, toolchains, output groups, or configuration behavior.
- an execution test proves runtime behavior of produced outputs.

Use synthetic positive and negative fixtures. Keep expected failures narrow so a different analysis error cannot satisfy the test accidentally. For transitions, assert configuration behavior and guard against unexpected target multiplication.

## Control analysis cost and API growth

Review provider/depset size, macro expansion, aspect propagation, transition fanout, action count, and Starlark memory profiles for large graph changes. Textual convenience is not evidence of analysis efficiency.

Treat public `.bzl` symbols, provider fields, rule attributes, and macro names as APIs. Use load visibility and target visibility deliberately. Remove obsolete APIs instead of keeping silent forwarding layers without maintained consumers.

Experimental subrules, rule inheritance, or other incubating surfaces belong in `Measure` or `Reverify` until the repository pin, ruleset support, migration value, and fallback are clear.

Official starting points: [rules](https://bazel.build/extending/rules), [symbolic macros](https://bazel.build/extending/macros), [aspects](https://bazel.build/extending/aspects), [configuration](https://bazel.build/extending/config), [exec groups](https://bazel.build/extending/exec-groups), and [rule testing](https://bazel.build/rules/testing).
