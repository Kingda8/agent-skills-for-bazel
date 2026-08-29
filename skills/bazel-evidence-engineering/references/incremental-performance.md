# Incremental performance and cache decisions

Use this reference for local and CI caches, output bases, concurrent agents, profiles, execution logs, workers, pipelining, filesystem behavior, resource tuning, and affected-target acceleration.

## Measure the bottleneck before selecting a lever

Separate:

- loading and analysis time;
- action creation from action execution;
- critical-path time from aggregate action time;
- local execution from cache hits;
- cold repository fetches, cold action cache, and warm incremental state;
- compiler work, tests, runfiles, copy or link work, storage, antivirus, and process startup.

Action counts describe graph shape. Combine them with profiles, BEP metrics, execution logs, wall time, disk use, resource pressure, and correctness before assigning performance priority.

## Design controlled comparisons

For an A/B:

1. Freeze revision, target, platform, configuration, cache mode, and meaningful environment.
2. Change one material variable where practical.
3. Alternate lanes or otherwise reduce ordering bias.
4. Repeat enough to distinguish signal from noise; three runs are a starting heuristic, not a universal gate.
5. Capture critical path, executed and cached actions by mnemonic, wall time, peak resources where relevant, and correctness.
6. Define the fallback and what evidence would make the setting local, named-config, CI-only, or default.

Do not average incomparable cold and warm lanes into one number.

## Keep cache layers distinct

- **Output-base analysis and action state:** fastest warm reuse, tied to one Bazel server and output base.
- **Repository cache:** downloaded external archives and repository inputs.
- **Disk action cache:** action results reusable across output bases on one machine or restored CI storage.
- **Remote cache:** shared action cache and content-addressable storage with authentication, trust, retention, and operations concerns.
- **Test result cache:** governed by test inputs, tags, environment, and cache policy.

For a disk action cache, choose storage separate from output bases and the repository cache. Demonstrate cross-output-base reuse with isolated short output bases, then measure growth and define retention based on the observed working set. Review whether logs, action outputs, paths, or test artifacts contain sensitive material.

A shared remote cache becomes credible after actions are reproducible across intended platforms and configurations. Use [remote-build-infrastructure.md](remote-build-infrastructure.md) for writer trust, namespaces, remote execution, output materialization, and poisoning response.

## Separate the concurrency layers

- Bazel selects one server per output base, and one server handles at most one invocation at a time. Concurrent clients using that output base follow lock/serialization policy.
- Separate output bases permit concurrent invocations but duplicate analysis state, servers, filesystem work, and disk use.
- `--jobs` limits eligible actions in one invocation; it does not control invocation count or directly define remote RPC concurrency.
- Remote transport concurrency and dynamic local/remote races consume different resource pools; tune them against queue time, retries, throttling, and host pressure.
- Prefer immutable source snapshots or isolated worktrees. Source edits during action execution can invalidate evidence and pollute shared cache state.
- Stable, short output bases and symlink prefixes can isolate experiments without discarding all incremental state. Random output bases increase churn.
- Share a repository cache deliberately; use a disk action cache only after measuring reuse and trust across isolated output bases.
- Give BEP, profile, and execution-log files invocation-specific paths and inspect ownership before shutdown, clean, or reset.

## Measure filesystem strategy by host

Copying, links, junctions, runfiles, path length, storage, permissions, antivirus, and launcher behavior can dominate host-specific builds.

Compare filesystem lanes with matching source, target, config, and cache state. Record:

- action shape for copy, link, runfiles, and junction operations;
- profile and critical path;
- alternating cold and warm wall time;
- binary, test, launcher, and runfiles correctness;
- disk use, path, permission, and security-software behavior.

Some filesystem settings are Bazel startup options and therefore select a different server. Use an isolated output base rather than disturbing active work. Fewer copy actions are encouraging but do not alone prove a faster or correct build.

## Treat resources, workers, and pipelining as experiments

- Derive jobs, CPU, memory, and local resources from representative workload and host capacity, not a copied large constant.
- Check upstream ruleset support and correctness before enabling workers.
- Measure startup savings against action volume, cache behavior, state leakage, diagnostics, and platform support.
- Evaluate language pipelining against representative incremental edits and supported platforms.
- Keep a reasoned hold visible and define natural triggers for re-evaluation.

## Use profiles and execution logs together

Before rerunning solely to capture a profile, inspect invocation-specific profiles retained in the output base. Current Bazel lines create profiles for many build-like commands and queries by default; explicit profile paths need separate cleanup and privacy ownership.

JSON profiles show elapsed time, critical paths, phase timing, remote queue/transfer/process categories, and scheduler or resource clues. Compact execution logs describe executed spawns—their arguments, inputs, environment, outputs, cacheability, and identity. They are not sorted and do not enumerate every registered action; use a version-matched parser and `aquery` for the action graph.

For remote performance, separate cache check, setup, queue, process, upload, download, network, local execution, dynamic locking, and lost-race work. Add detailed profile categories only when the default profile cannot answer the hypothesis.

Profiles and logs may contain labels, paths, command lines, environment, and outputs. Apply privacy and retention policy before retaining or uploading them.

## Keep affected-target acceleration conservative

An affected-target selector can provide a fast advisory lane for ordinary source changes. Compare it against full-suite truth before granting acceptance authority.

Maintain broad fallbacks for changes to modules, locks, BUILD or `.bzl` files, configs, platforms, toolchains, generated-contract rules, suites, and other graph-shaping inputs. A fast affected lane and a complete promotion or release gate can coexist.

## Preserve the diagnostic scene before cleaning

Warm state is evidence. Before clearing it, compare configuration, toolchain, environment, action inputs, output-base identity, and execution logs. A fresh isolated output base often tests corruption with less impact on concurrent work.

Use `clean` or an expunge only when disk reclamation, clean-build reproduction, or a concrete state-corruption hypothesis is the task. Record that the result no longer represents ordinary incremental behavior.

## Report performance conclusions

Include the revision, target, platforms, configuration, cache lanes, sample shape, critical-path evidence, correctness result, observed effect, uncertainty, and fallback. Avoid turning a one-host improvement into a universal default without representative proof.
