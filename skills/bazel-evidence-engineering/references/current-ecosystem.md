# Current Bazel and ecosystem boundary

**Last reviewed:** 2026-08-29  
**Stable baseline:** Bazel 9.2.0, Bazel 9 Active LTS  
**Rolling line at review:** Bazel 10

This reference constrains claims of currency. Repository pins remain authoritative.

## Bazel 9 baseline

- Bazel 9 is Bzlmod-only: legacy WORKSPACE external dependency resolution and `bazel sync` are removed.
- Symbolic macros are available and preferred for new declaration APIs where supported; lazy expansion is not a completed guarantee.
- Aspects, build settings, Starlark transitions, exec groups, and automatic execution groups are high-value control surfaces, but exact ruleset adoption is pin-specific.
- Bazel 9.2 adds or refines `transition.and_then`, constraint refinement, module-extension facts versioning, and resource estimates from selected execution properties.
- `remote_download_outputs` supports `minimal`, `toplevel`, and `all`; Bazel 9.2 defaults to `toplevel`.

Primary sources: [release model](https://bazel.build/release), [Bazel 9](https://blog.bazel.build/2026/01/20/bazel-9.html), [9.2.0 notes](https://github.com/bazelbuild/bazel/releases/tag/9.2.0), and [command reference](https://bazel.build/reference/command-line-reference).

## Do not normalize experimental surfaces into defaults

Subrules, rule inheritance, remote repository-content caching, remote output services, lost-input recovery, transfer chunking, and similar incubating features require a pinned-version check, concrete problem, bounded canary, and fallback.

Official pages can drift internally. Use version-matched `bazel help`, current pins, and executed evidence when a flag, default, or lifecycle status matters.

## Ecosystem channel snapshot

GitHub releases and the Bazel Central Registry can move at different times. Resolve from the repository's chosen channel.

| Component | State observed on 2026-08-29 |
|---|---|
| `rules_rust` | GitHub and BCR 0.74.0; BCR publication observed during this review |
| `aspect_rules_js` | BCR 3.4.1 |
| `aspect_rules_ts` | BCR 3.10.1 |
| `rules_oci` | GitHub 2.3.3; BCR 2.3.0; stable maintenance mode |
| `rules_pkg` | BCR 1.3.0 |
| `package_metadata` | BCR 0.0.13; active early development |

This snapshot is a re-review trigger, not a recommended upgrade set. Inspect current BCR metadata, release notes, compatibility, telemetry, license, platform support, and transitive modules before adoption.

Current source indexes: [Bazel Central Registry](https://registry.bazel.build/), [`rules_rust`](https://github.com/bazelbuild/rules_rust), [`rules_oci`](https://github.com/bazel-contrib/rules_oci), [`rules_pkg`](https://github.com/bazelbuild/rules_pkg), and [`package_metadata`](https://registry.bazel.build/modules/package_metadata/).

## Supply-chain boundary

- `rules_oci` signing and attestation helpers remain preview surfaces and act on remote registries; build, push, sign, attest, and verify stay separate.
- `rules_pkg` can support reproducible archives, but duplicate-path policy and host-discovered packaging tools still require explicit review.
- `package_metadata` is promising for provider-based inventory but is not yet proof of an end-to-end artifact-complete SBOM.
- The approved SLSA specification at review is v1.2. Name both track and level. Build provenance still uses the `https://slsa.dev/provenance/v1` predicate type.
- BCR attestations describe upstream module inputs, not the consuming repository's release provenance.

Sources: [SLSA v1.2](https://slsa.dev/spec/v1.2/), [BCR attestations](https://github.com/bazelbuild/bazel-central-registry/blob/main/docs/attestations.md), and the linked ruleset projects above.

## Maintenance trigger

Refresh this file when the Active LTS changes, a named ruleset changes its compatibility floor or lifecycle state, an official default used by the skill changes, or an evaluation shows stale guidance. Keep durable principles in the topic references and dated facts here.
