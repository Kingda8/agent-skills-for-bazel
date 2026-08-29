# Remote build infrastructure

Use this reference for remote caches, remote execution, dynamic execution, Build without the Bytes, remote output materialization, BES, transport concurrency, or cache trust and incident response.

## Separate the remote layers

| Layer | Contract | Evidence |
|---|---|---|
| Remote action cache | action key to ActionResult mapping | cache policy, hit/miss/outcome metrics, writer trust |
| Content-addressable store | digest-addressed input/output bytes | digest verification, retention, eviction, URI resolution |
| Remote execution | executes REAPI actions on selected workers | execution platform, strategy, queue/process timing, result parity |
| Dynamic execution | races eligible local and remote branches | winning branch, cancelled work, latency, duplicate resource cost |
| Remote output policy | controls which remote outputs become local bytes | download mode, local consumers, artifact materialization |
| BEP | invocation event graph | complete announced event graph and result semantics |
| BES | external BEP delivery service | upload completion, acknowledgements, retention, privacy |

A service may implement several layers, but success in one does not prove another.

## Prove prerequisites before remote execution

Remote execution requires more than a reachable executor. Prove that eligible actions:

- declare tools, inputs, outputs, environment, and platform-relevant state;
- resolve compatible execution platforms and toolchains;
- avoid undeclared host paths, SDKs, home directories, mutable cwd state, and uncontrolled network;
- produce equivalent outputs locally and on every worker matching the selected constraints;
- have explicit behavior for external, destructive, exclusive, or non-hermetic tests.

Put executor requirements in supported platform or target `exec_properties`. Treat values as server-defined opaque contracts and verify their effect from configured and executed evidence. Do not revive deprecated remote execution property fields.

## Treat a remote cache as shared execution state

A read-only consumer still trusts every writer in its cache namespace. Define:

- trusted writers and untrusted/read-only consumers;
- service-side read/write permissions and scoped credentials;
- TLS, instance or namespace isolation, retention, eviction, and ownership;
- source-mutation guards and immutable snapshots for cache-producing builds;
- download digest verification supported by the pinned Bazel;
- poisoning detection, isolation, purge, and recovery procedure.

Digest verification proves downloaded bytes match the advertised digest. It does not prove the ActionResult was created by the intended action; writer trust and hermetic action keys remain primary.

Disabling upload of local results can create a read-only cache client for local execution. Do not assume it prevents a remote execution service from caching remotely executed results. Validate service policy and execution requirements with a canary.

During suspected poisoning, stop new writes, isolate or rotate the affected instance, disable remote acceptance for a reproducer, preserve invocation evidence, and only then apply the backend's purge procedure.

## Separate strict acceptance from availability fallback

Maintain distinct policies when both are needed:

- a strict remote-acceptance lane where a remote failure cannot silently fall back to local execution;
- an availability-oriented developer lane that may allow local fallback and reports degraded placement honestly.

A fallback-enabled green run does not prove remote readiness. Record actual strategy, execution platform, queue and process timing, and the first remote failure. Use `no-remote-exec`, `no-remote-cache`, `no-remote`, or narrower execution requirements only for actions with a concrete reason and owner.

Roll out by representative target, platform, mnemonic, and ruleset. Hold promotion on result divergence, unexpected local fallback, unresolved toolchain placement, queue/capacity failure, cache poisoning risk, or missing evidence.

## Choose remote output materialization intentionally

Remote success and local bytes are different facts:

- `minimal` downloads outputs required by local actions;
- `toplevel` also materializes requested top-level outputs;
- `all` materializes every remote output.

At the 2026-08-29 review, Bazel 9.2 defaults to `toplevel`; verify the repository pin rather than copying this value.

Use `minimal` for result-only lanes whose downstream consumers resolve remote artifacts, `toplevel` for ordinary requested artifacts, and `all` only for demonstrated compatibility or debugging needs. Use targeted download patterns when a small extra output set is required.

Under Build without the Bytes, a missing local intermediate is expected and does not mean the action failed. Release evidence must identify either materialized bytes with the expected digest or a resolvable remote URI whose retention covers every consumer.

Treat cache-eviction retries, lost-input rewinding, lease extension, chunking, CAS-backed symlink materialization, and remote output services as version-gated resilience or transfer features—not substitutes for retention and artifact ownership. Correlate all attempts when recovery creates a new invocation identity.

## Treat dynamic execution as a targeted race

Dynamic execution races local and remote branches of the same action and uses the first completed branch while cancelling the other. It requires a real remote executor; a cache endpoint is insufficient.

Start with selected mnemonics after both local and remote paths are independently correct. Measure clean and incremental latency, cache-hit latency, winning branch, work completed after a loss, local resource pressure, remote load, and correctness. A first-completed failure is a failure, not an availability fallback.

Tune local-start delay from measured remote latency. Promote only when latency gain justifies duplicate resource use. Use current strategy documentation and version-matched help; do not copy internal scheduler flags from stale pages.

## Separate concurrency controls

- One Bazel server per output base handles at most one invocation at a time; concurrent clients serialize or follow lock policy.
- Separate output bases allow concurrent invocations but duplicate analysis state, servers, filesystem work, and disk use.
- `--jobs` bounds eligible action concurrency inside one invocation; it does not define invocation count or remote RPC concurrency.
- Remote connections and per-connection concurrency are transport controls that must match service capacity, queue time, retries, and throttling.
- Dynamic execution may spend local and remote resources on one action intentionally.

Prefer immutable source snapshots or isolated worktrees for concurrent agents. Source edits during actions can invalidate evidence and poison shared cache state. Verify the pinned version's concurrent-change guard; it reduces risk but does not make live shared editing a supported evidence model.

## Keep BEP, BES, profiles, and logs distinct

BEP is the event graph. BES transports events to an external service. A successful command does not prove that an asynchronous stream is complete, acknowledged, retained, or able to resolve referenced artifacts.

For formal BES evidence, wait for upload completion or verify backend completeness. Treat fully asynchronous delivery as provisional. Consume file or stream BEP through its real end and require the announced child-event graph to close.

Use:

- BEP/process metrics for invocation, test, cache, and strategy outcomes;
- a profile for phase time, remote cache checks, setup, queue, process, transfer, dynamic locking, and critical path;
- a compact execution log for executed-spawn inputs, arguments, environment, outputs, cacheability, and identity;
- `aquery` for all registered actions;
- a remote gRPC log only for an RPC-level hypothesis.

Current Bazel lines retain invocation-specific profiles for many commands by default. Inspect retained profiles before rerunning. Explicit profile paths require privacy and cleanup ownership. Compact execution logs are not ordered; compare with a version-matched parser and matching invocation identity.

## Report the remote conclusion

Record revision, target, configuration, target and execution platforms, actual strategy, cache namespace and trust lane, output mode, fallback policy, invocation/attempt identities, correctness result, queue/process/transfer evidence, artifacts, privacy boundary, rollout scope, rollback, and owner.

Official starting points: [remote caching](https://bazel.build/remote/caching), [remote execution](https://bazel.build/remote/rbe), [dynamic execution](https://bazel.build/remote/dynamic), [BEP and BES](https://bazel.build/remote/bep), and [JSON profiles](https://bazel.build/advanced/performance/json-trace-profile).
