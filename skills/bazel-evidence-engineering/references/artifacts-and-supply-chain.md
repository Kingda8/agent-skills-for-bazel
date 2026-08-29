# Artifacts, OCI, SBOM, and provenance

Use this reference for generated contracts, conventional packages, OCI images, dependency and license inventory, SBOMs, provenance, signing, attestations, publication, and release consumption.

## Distinguish artifact layers

Keep these concepts separate:

1. Bazel binary or default output.
2. Conventional archive or package with a stable layout.
3. OCI image or layout with platform and layer identity.
4. Dependency or license inventory.
5. Artifact-scoped SBOM.
6. Upstream or source provenance.
7. Local build manifest or SLSA build provenance.
8. Cryptographically signed attestation.
9. Registry or release publication.
10. Consumer-side verification.

Success at one layer does not prove the next. Select the smallest stage matching the task and state which layer the evidence covers.

## Inventory supply-chain inputs before claiming coverage

Useful ingredients can include:

- Bazel, language rules, and toolchain pins;
- Bzlmod and language lock state;
- external artifact hashes, registries, and platform selection;
- target graphs connecting source, generated contracts, tools, and runtime data;
- upstream provenance metadata for selected third-party artifacts.

Reinspect the repository before claiming completeness. Upstream provenance records an input's identity; it is not provenance for the repository's built release artifact.

## Make conventional packages first-class targets

When a distributable archive or installer contract exists, evaluate a maintained packaging ruleset against the pinned Bazel and module versions.

Useful acceptance criteria:

- all package inputs come from labels, providers, or runfiles;
- archive paths, modes, ownership, and timestamps are reproducible;
- supported runtime contents receive representative smoke checks;
- CI and release consume the declared Bazel output rather than harvesting an incidental output-tree path;
- the target exposes a stable artifact identity and content manifest.

Generated code and metadata must have an owning producer rule or aspect, declared inputs/tools, structured providers or output groups, and explicit consumers. Do not treat a checked-in generated file or incidental output-tree path as the production contract. Decide whether generated content is reviewed source, an action output, or a release artifact, and keep stale checks aligned with that ownership.

Reproducible packaging requires more than normalized timestamps. Reject conflicting duplicate archive paths, control modes and ownership, and ensure host-discovered packagers are represented by a toolchain or are disclosed as a non-hermetic boundary. Stamping can be useful for traceability but may break byte-for-byte reproducibility; define which identity the release contract values.

## Separate OCI build, load, push, and trust stages

For a first formal OCI path, evaluate one maintained ruleset at a time. Choose alternatives only when a measured layer, transfer, multi-platform, or content-addressable storage bottleneck justifies comparison.

Prefer, where supported:

- digest-addressed base images and explicit platforms;
- stable layers arranged so frequently changing application content does not invalidate large bases;
- distinct build, load, push, sign, attest, and verify stages;
- image digests and platform manifests in formal evidence;
- push, sign, and attest only within an explicitly authorized release lane.

Inspect the selected ruleset's lifecycle and acquisition channel. A maintained but maintenance-mode ruleset can remain the correct stable choice; a newer alternative deserves a measured trial only for a concrete transfer, layering, or remote-execution bottleneck. Treat preview signing or attestation helpers as remote registry mutations, not ordinary build actions, and keep consumer verification independent.

## Define SBOM completeness by artifact

Before calling an output a release SBOM, define its scope. A complete product SBOM may need to cover:

- Bzlmod modules;
- translated Rust crates;
- translated npm packages;
- downloaded executables and tools;
- OCI base images and layers;
- license, version, package URL, and content hash;
- the exact package or image digest represented.

A partial SBOM remains useful when its scope and omissions are explicit. Prefer deterministic output, schema validation, cross-platform execution where relevant, and reverse comparison with actual package or image contents.

Provider-based package metadata is an input to completeness, not proof of completeness. Reverse-check the final artifact for translated Rust and npm dependencies, downloaded tools, generated content, OCI bases/layers, and other bytes that may not propagate metadata through every rule.

Evaluate candidate rules or tools for maintenance, Bazel compatibility, supported platforms, host dependencies, telemetry, output schema, and ecosystem coverage before granting them authority in the graph.

## Keep provenance concepts precise

- **Upstream or source provenance:** where an input came from and how its identity was verified.
- **Build manifest:** target, source, configuration, platform, toolchains, locks, and output digest.
- **SLSA provenance:** a statement matching a specific SLSA version and builder model.
- **Signed attestation:** a cryptographic envelope around a defined statement.
- **Verification:** consumer policy checking digest, signer or builder identity, build type, parameters, and allowed sources.

An initial build manifest can include:

- exact Bazel target and source revision;
- Bazel, ruleset, and toolchain identities;
- module and language lock digests;
- execution and target platforms plus relevant config;
- artifact, image, and SBOM digests;
- BEP, profile, or execution-evidence reference;
- known equivalence or completeness gaps.

Use a named SLSA **track and level** only after checking every requirement against the selected specification and verifier. Under SLSA v1.2, a locally written manifest does not automatically meet Build L1, signing alone does not meet Build L2, and Build Provenance continues to use the `https://slsa.dev/provenance/v1` predicate type. Builder capabilities, hosted-build identity, account trust, key custody, and private-source support belong in the design.

Bazel Central Registry attestations can strengthen trust in an upstream module's source archive and registry metadata. They are not provenance for the consuming repository's built release.

## Adopt supply-chain layers for a named need

Consider implementation when the scope includes a product artifact, deployment consumer, compliance requirement, offline or reproducibility need, or release gate.

Ask:

1. Who owns the artifact contract and verifier?
2. Do isolated builds produce matching digests or an explained difference?
3. Are platform and runtime contents tested?
4. Is SBOM scope visible and tied to the artifact digest?
5. Are publication, signing, and ordinary build or test separated?
6. Are mutable tags, credentials, network access, and external state confined to the release stage?
7. Are action count, cache behavior, artifact size, and operational cost acceptable?

## Treat external tooling as code dependencies

Before adopting a ruleset or supply-chain tool, review its license, pinned version or commit, integrity, registry or release status, maintenance, transitive modules, telemetry, platform support, and update ownership. Link to upstream sources; do not copy external agent packages into a repository without a license and a concrete ownership reason.

Third-party code may execute during dependency acquisition or builds: repository rules, module extensions, Rust `build.rs`, procedural macros, npm lifecycle hooks, code generators, and packaging tools. Review allowlists, sandbox or remote behavior, environment and secret visibility, network access, cache trust, and platform identity as part of adoption.

Current source boundaries: [SLSA v1.2](https://slsa.dev/spec/v1.2/), [BCR attestations](https://github.com/bazelbuild/bazel-central-registry/blob/main/docs/attestations.md), and the ruleset sources linked from [current-ecosystem.md](current-ecosystem.md).
