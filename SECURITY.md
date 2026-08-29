# Security policy

## Reporting sensitive content

Do not open a public issue containing a credential, private identifier, unpublished vulnerability, internal infrastructure detail, or other sensitive material.

The intended public channel is GitHub Private Vulnerability Reporting on the repository's **Security** tab. Before the first public release, the maintainer must enable that feature and verify a private test report. If the private form is unavailable, open only a non-sensitive public issue asking the maintainer to establish a private channel; do not include the sensitive details.

This local repository currently has no public remote, so no private reporting endpoint can be claimed yet. Enabling and verifying the endpoint is an explicit publication gate.

Rotate or revoke an exposed credential through its owner. Deleting it from the latest revision does not remove it from Git history or external caches.

## Scope

Security reports can include:

- secrets or credential-like values;
- private paths, domains, identities, repository names, or customer data;
- semantic leakage that reconstructs a private architecture or operational state;
- instructions that silently broaden authorization or encourage destructive external actions;
- validation bypasses in the public-hygiene tooling;
- plugin packaging that exposes undeclared capabilities or external communication.

General Bazel or agent-client vulnerabilities belong with their upstream maintainers unless Agent Skills for Bazel introduced or amplified the issue.

## Supported versions

Until a stable release exists, only the current default branch is supported. After tagged releases begin, this section must name the supported release lines explicitly.

## Maintainer response

Maintainers should preserve evidence privately, acknowledge a valid private report, remove sensitive material from the public tip, assess history rewrite and credential rotation needs, and publish a minimal advisory when users need to act. Do not repeat the sensitive value in public remediation notes.
