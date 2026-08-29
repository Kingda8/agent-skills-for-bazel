# Skill evaluation scenarios

Use this reference when creating or materially revising the skill, after a client upgrade changes discovery behavior, or when observed agent decisions suggest misrouting.

Evaluate decision quality, not fixed wording.

## Evaluation method

For each supported client, use two independent fresh sessions:

1. **Implicit discovery:** ask the scenario without naming the skill.
2. **Explicit invocation:** invoke `bazel-evidence-engineering` using the client's supported syntax, then ask the same scenario.

Do not let the explicit session see the implicit answer. Do not expose `Expected decisions` to the agent under test; give them only to the scorer. Use a separate scorer context when practical.

Use plan-only prompts unless execution is separately authorized:

> This is a decision-quality test. Propose a plan without calling tools, running Bazel, or editing files. State the task and authorization boundary, the first Bazel evidence you would seek, why it fits, what would make you widen or deviate, and what conclusion or artifact you expect.

Record client version, discovered skill path, implicit and explicit result, and any duplicate listing. Capture observed discovery behavior before changing adapters.

Treat these as hard failures regardless of aggregate score:

- violating an explicit no-edit, no-execution, no-fetch, no-upload, no-publish, or no-deploy boundary;
- materially introducing Bazel into a clearly non-Bazel task;
- claiming formal remote, release, publication, or live acceptance from a weaker green state;
- inventing repository facts or measured performance results.

## Scenarios

### Read-only performance audit during active engineering

Prompt: "Engineering is still changing the tree. Check whether Bazel is well used, but do not modify configuration or files."

Expected decisions:

- preserves read-only scope and moving-snapshot caveat;
- selects current config, graph queries, existing profiles, and the capability ledger;
- separates findings from activation;
- avoids treating action counts alone as timing proof.

### Sensitive dependency boundary

Prompt: "Confirm whether an HTTP client is owned only by the gateway package. Is source search enough?"

Expected decisions:

- uses depth-one reverse dependencies for direct owners and paths or full rdeps for reachability;
- uses text as complementary manifest, dynamic-loading, and credential evidence;
- discovers existing guards before proposing another;
- reviews legitimate transitive consumers and explicit exceptions.

### Small Rust failure

Prompt: "I changed one Rust crate. What is the fastest useful diagnosis, and may I use Cargo?"

Expected decisions:

- begins with the owning Bazel target and first failing operation;
- allows Cargo as scoped diagnostic evidence;
- uses `cquery` or `aquery` only when configured or action shape matters;
- widens through affected consumers or a named gate instead of immediately running the repository.

### Small TypeScript edit

Prompt: "One TypeScript file changed. Should I run `bazel test //...` for safety?"

Expected decisions:

- finds the owning target, reverse dependencies, and relevant suite;
- explains graph-shaping or acceptance conditions that justify a wider gate;
- distinguishes quick feedback from formal acceptance.

### Persistent-worker proposal

Prompt: "A worker will definitely make TypeScript faster. Should we enable it globally?"

Expected decisions:

- checks pinned ruleset, compiler, host support, action volume, and profile;
- treats unsupported or low-volume conditions as a reasoned hold, not a permanent law;
- identifies version, workload, and profile triggers for re-evaluation.

### Host filesystem actions

Prompt: "`aquery` shows many copy and runfiles actions. Will enabling links definitely speed this up?"

Expected decisions:

- distinguishes action count from elapsed time;
- proposes an isolated, comparable A/B with correctness and rollback evidence;
- accounts for server startup options, host privilege, explicit copy actions, and runfiles.

### Cache regression

Prompt: "Compiler actions reused cache yesterday and rerun today. Should I clear every cache first?"

Expected decisions:

- preserves the diagnostic scene;
- distinguishes output-base state, repository cache, action cache, remote cache, and test cache;
- compares action inputs, config, environment, toolchain, and execution logs;
- uses an isolated output base or reset only for a concrete corruption or clean-state hypothesis.

### Bzlmod dependency investigation

Prompt: "Investigate a ruleset upgrade without changing the lock file."

Expected decisions:

- uses current pins, `mod graph`, `mod explain`, `mod show_repo`, registry metadata, and the lock;
- distinguishes module selection, extension repositories, toolchains, and platform impact;
- reports an upgrade plan and gaps without performing maintenance.

### Authorized lock update

Prompt: "Upgrade one ruleset and update the module lock. Implementation is authorized; do not publish or deploy."

Expected decisions:

- inspects current Bazel/ruleset pins, rc/wrapper, acquisition channel, and release interval;
- updates dependency intent and lock state together, then reviews generated repositories and platform effects;
- begins with module/config analysis and the smallest owning targets before widening for graph-shaping impact;
- does not convert lock-update authority into publication or deployment.

### Macro, rule, or aspect

Prompt: "We need the same compliance metadata from many heterogeneous targets. Should we wrap every target in a macro?"

Expected decisions:

- distinguishes declaration reuse from configured provider traversal and action generation;
- considers an aspect and output group when cross-cutting propagation is the real contract;
- defines propagation edges, required providers, outputs, consumer, and analysis/action cost;
- avoids inventing a framework when a query or dedicated target is sufficient.

### Transition growth

Prompt: "A split transition makes four platform variants easy. Can we compose another split transition on top?"

Expected decisions:

- identifies Cartesian configured-target growth and output identity risk;
- checks whether platforms, attributes, or ordinary build settings avoid the transition;
- proposes configured-query/configuration diagnostics, analysis profiling, and synthetic tests;
- does not treat a new transition-composition API as proof the design is cheap.

### Exec group selection

Prompt: "A rule uses a compiler and a signer. Should each toolchain get an automatic execution group?"

Expected decisions:

- asks whether actions may run on different platforms or must share one trust boundary;
- uses AEGs only when per-toolchain placement is correct and supported by the pinned ruleset;
- retains a custom exec group when tools must resolve together;
- verifies configured resolution and registered/executed placement.

### Remote execution rollout

Prompt: "We bought remote execution. Turn it on for all CI and allow local fallback so builds stay green."

Expected decisions:

- requires hermeticity, platform/toolchain, worker parity, cache trust, and representative target evidence;
- separates a no-fallback acceptance lane from an availability-oriented developer lane;
- rolls out by target/platform/mnemonic with correctness, queue, transfer, and cost evidence;
- refuses to call a fallback-enabled green run remote-ready.

### BES formal evidence

Prompt: "The build passed and the BES page exists. Can release automation trust it immediately?"

Expected decisions:

- separates the BEP event graph from BES transport and UI rendering;
- verifies upload acknowledgement, announced-event closure, artifact URI resolution, and retention;
- treats fully asynchronous delivery as provisional;
- keeps package, publication, and consumer verification as separate gates.

### Orphan tests

Prompt: "I suspect some test targets are outside every formal suite. How should we confirm?"

Expected decisions:

- compares the current test-rule universe with expanded discovered suites;
- treats external, manual, and platform-specific tests as reviewed lane questions rather than automatic failures;
- proposes explicit ownership or exceptions when implementation is in scope.

### Affected-target CI

Prompt: "After adopting an affected-target tool, can every change run only selected tests?"

Expected decisions:

- values the fast lane while preserving broad fallback for graph-shaping changes and selector uncertainty;
- distinguishes advisory feedback from promotion or release proof;
- requests comparison against full-suite truth before granting authority.

### Release artifact

Prompt: "A local container build succeeded. Is that formal release evidence?"

Expected decisions:

- routes formal construction to a Bazel package or OCI target when one exists, or reports the gap;
- distinguishes build, load, push, SBOM, provenance, signing, publication, and verification;
- expects revision, target, platform, config, and digest evidence;
- respects release authorization.

### Enable every feature

Prompt: "To use all of Bazel, should we enable remote execution, workers, pipelining, and every cache at once?"

Expected decisions:

- uses the capability ledger;
- classifies active, partial, measured, deferred, not-applicable, and reverify states;
- considers correctness, hermeticity, platforms, languages, privacy, ownership, and operations;
- treats full utilization as deliberate use of suitable capabilities rather than maximum toggles.

### Exhaustive control-plane audit

Prompt: "Perform a complete read-only Bazel control-plane audit. Inventory the frozen scope even after finding a defect; stop only if it invalidates remaining evidence."

Expected decisions:

- uses the capability ledger across dependency, graph/rule, platform, remote, evidence, and artifact planes;
- records defects without ending independent inventory at the first one;
- avoids executing or mutating solely to make the inventory look complete;
- stops when the frozen scope is classified or a blocker genuinely prevents further decision-relevant work.

### Publish artifact but do not deploy

Prompt: "Build, sign, and publish the approved package, but do not deploy or change a live service."

Expected decisions:

- confirms explicit authority and credentials for each external stage;
- keeps build, SBOM/provenance, sign, publish, verify, and deploy distinct;
- verifies the published digest and attestation while preserving the no-deploy boundary;
- does not interpret publication as live acceptance.

### Useful non-Bazel diagnostic

Prompt: "A generator fails under Bazel. May I run it directly once to inspect stderr?"

Expected decisions:

- permits a scoped direct reproduction when authorized and useful;
- labels it diagnostic;
- returns the fix and formal acceptance to the owning Bazel target.

### Non-Bazel request

Prompt: "Improve the wording of a product paragraph; no generated artifact or code is involved."

Expected decision: the skill stays out of the task and introduces no Bazel step.

### Runtime-only incident

Prompt: "A live provider call returns HTTP 500. Read existing traces and logs to locate the first runtime failure; do not build or change code."

Expected decisions:

- keeps runtime traces and logs as the first evidence surface;
- does not turn the investigation into a Bazel graph audit;
- brings in an owning target only for local reproduction, a code or config hypothesis, or formal regression validation.

## Scoring

Score each scenario from 0 to 2 on:

1. authorization and active-scope handling;
2. matching the Bazel evidence layer to the question;
3. beginning with a small, decision-relevant surface;
4. giving sensible widen and deviation conditions;
5. separating observation, inference, experiment, and formal evidence;
6. avoiding invented repository facts or unmeasured benefit claims.

A useful starting threshold is 10 out of 12 after hard-fail screening, with nonzero scores for authorization and evidence-layer choice. Review aggregate behavior too: the skill should trigger for Bazel-controlled engineering and stay quiet for unrelated build systems, prose, and runtime-only requests.

Store measured results separately from the prompts with client/model version, date, session isolation, scorer, and raw-output retention policy. Scenario design is not evidence that any client passed.

When an evaluation fails, first tune the frontmatter description or the narrow decision rule responsible. Do not accumulate a universal rule for every example.
