# Bazel capability ledger

Use this ledger for broad audits, planning, and periodic re-verification. It is a decision map, not a demand that every feature become active.

## Status vocabulary

- **Active:** configured and supported by current evidence.
- **Partial:** present but not applied across the intended scope.
- **Measure:** a controlled trial can determine value or correctness.
- **Deferred:** useful after a prerequisite or ownership decision.
- **Not applicable now:** current platform, ruleset, scale, or correctness constraints make it low-value.
- **Reverify:** a version, platform, workload, service, or repository change may alter the decision.

Leave an item unclassified until repository evidence supports a status. Do not import statuses from another project or from this reference.

## Repository and dependency plane

| Capability | Evidence to inspect | Typical status-moving trigger |
|---|---|---|
| Bazel version and effective rc/wrapper identity | pins, rc imports, canonical command, version-matched help | Bazel, runner, wrapper, or policy change |
| Bzlmod resolution and lock mode | module graph, selection paths, lock behavior | dependency or Bazel upgrade |
| Module-extension reproducibility | tags, generated repos, facts, lock entries, tests | extension or platform input change |
| Repository rules and repo mapping | apparent names, mapping export, fetch inputs, host/network use | external-tool or dependency migration |
| Vendor, mirror, and offline closure | target/config/platform closure, nofetch and isolated canaries | offline or source-control requirement |
| Bazelisk and upgrade discipline | resolved binary, interval notes, smallest gates, rollback | Active LTS or ruleset-floor change |
| Dependency code execution | repository/extension code, build scripts, proc macros, lifecycle hooks | new package or execution policy |

## Graph and rule-engineering plane

| Capability | Evidence to inspect | Typical status-moving trigger |
|---|---|---|
| `query`, `cquery`, and `aquery` diagnosis | real investigations, explicit universes/configs, guards | recurring misuse or missing graph layer |
| Fine-grained target ownership | source inventory, owners, deps/rdeps, invalidation | orphan input or broad rebuild |
| Visibility and load boundaries | target/load visibility, package groups, consumers | new public surface or dependency direction |
| Symbolic versus legacy macros | public declaration APIs, typed attrs, visibility, naming | Bazel migration or new macro API |
| Rules, providers, depsets, and actions | provider contracts, action inputs/tools, analysis cost | new build semantic or generator |
| Aspects and output groups | propagation, providers, outputs, configured/action growth | IDE, lint, policy, or metadata need |
| Build settings and custom transitions | read/write sets, config hashes, fanout, analysis profile | dependency-specific configuration need |
| Analysis tests and policy guards | positive/negative fixtures, providers/actions/failures | rule API or architecture invariant |
| Generated-code ownership | producer actions, providers/output groups, consumers | new generated contract or stale drift |

## Platform and execution plane

| Capability | Evidence to inspect | Typical status-moving trigger |
|---|---|---|
| Bazel-resolved language toolchains | registrations, configured resolution, actions | new platform, compiler, or ruleset |
| Exec groups, AEGs, and test exec group | ruleset adoption, toolchain sets, resolved platforms | multi-tool or remote placement need |
| Platform constraints and refinement | target/exec compatibility, inheritance semantics | platform model growth |
| Cross-platform action hermeticity | `aquery`, sandbox/remote canaries, isolated builds | hidden host dependency or new executor |
| Runfiles-based runtime data | providers, launchers, supported platform tests | cwd assumption or platform failure |
| Sandboxing | supported actions, narrow negative canaries | hidden inputs or stricter executor |
| Host filesystem strategy | runfiles, links, copies, permissions, profile | host upgrade or measured bottleneck |
| Multi-agent source/output-base policy | snapshot isolation, contention, cache reuse | concurrent workload growth |

## Remote and performance plane

| Capability | Evidence to inspect | Typical status-moving trigger |
|---|---|---|
| Repository cache | location, sharing, retention, runner behavior | CI topology or dependency volume |
| Local disk action cache | cross-output-base reuse, trust, growth | worktree scale or storage pressure |
| Remote cache trust and incident response | writer ACLs, namespaces, digest checks, isolation/purge drill | new trust domain or poisoning suspicion |
| Remote output materialization and BwoB | download mode, local consumers, URI retention/eviction | CI or artifact-consumption change |
| Strict remote execution acceptance | platforms, toolchains, exec properties, no-fallback canary | new executor, platform, or ruleset |
| Dynamic execution by mnemonic | local/remote parity, win/loss profile, duplicate resource cost | latency or workload change |
| Remote transport concurrency/resilience | jobs, connections, queue, retries, timeouts, metrics | scale or remote regression |
| Cache eviction and lost-input recovery | retention, missing-blob reproducer, attempt correlation | BwoB adoption or incident |
| Workers and language pipelining | support, action volume, correctness, critical path | compiler/ruleset or graph change |
| Affected-target selection | selector fixtures versus full-gate truth | graph-shaping input or false negative |

## Test and evidence plane

| Capability | Evidence to inspect | Typical status-moving trigger |
|---|---|---|
| Analysis-only graph validation | scoped `build --nobuild` or analysis tests | graph-shaping change |
| Named suites and test ownership | test universe, suite expansion, canonical BEP | orphan test or lane-policy change |
| Coverage under Bazel | instrumentation, language/platform support, report merge | named coverage gate |
| BEP formal evidence | closed announced-event graph, invocation identity, failures | schema, CI, or Bazel update |
| BES delivery and artifact resolution | upload mode, acknowledgement, URI access/retention | external UI gains authority |
| Profiles and execution logs | concrete timing/cache hypothesis, matched invocations | critical-path or reuse regression |

## Language and supply-chain plane

| Capability | Evidence to inspect | Typical status-moving trigger |
|---|---|---|
| Rust translation and platform support | crate graph, features, build code, host/target evidence | crate or platform change |
| TypeScript type-check acceptance | transpiler mode, generated type-check target, canonical gate | rules_ts or compile-layout change |
| Ecosystem telemetry/privacy | transitive modules, environment controls, documented collection | ruleset adoption/update |
| Reproducible packages and OCI outputs | action inputs, layout, duplicate policy, digest, consumers | distribution contract |
| License inventory and artifact SBOM | provider coverage versus actual artifact contents | compliance or release requirement |
| Upstream attestation versus product provenance | input identity, builder statement, artifact digest | trust or SLSA requirement |
| Build manifest, SLSA track/level, signing, verification | builder identity, predicate, key custody, verifier policy | release maturity |

## Review questions

For every capability being reconsidered, record:

1. What bottleneck, architecture risk, or acceptance need does it address?
2. Which revision, target, platform, configuration, and workload represent the test?
3. Which metric or invariant decides success?
4. What could make the result unsafe to generalize?
5. What is the fallback if correctness, performance, privacy, cost, or operations regress?
6. Who owns the configuration and incident response?
7. Should the result become a default, named config, advisory tool, or occasional diagnostic?

A capability may remain deferred without being forgotten when its prerequisite and next evidence are explicit.

## Suggested record shape

```markdown
### Capability name

- Status:
- Revision and dirty state:
- Target and workload:
- Host / execution / target platform:
- Configuration, strategy, and cache lane:
- Evidence:
- Decision:
- Generalization limits:
- Fallback:
- Owner:
- Reverify trigger:
```
