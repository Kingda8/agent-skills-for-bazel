# Contributing to Agent Skills for Bazel

Thank you for helping agents make better engineering decisions.

**Bring a hard decision, not a longer prompt.**

## Contributions we value

- a real, generalizable engineering decision with a clear evidence boundary;
- an evaluation scenario that exposes unsafe, wasteful, or unsupported agent behavior;
- a reproducible compatibility result for an agent client;
- a Bazel or ruleset change that moves an existing judgment boundary.

## Contribution standard

A useful skill contains guidance that changes decisions. It should not restate generic competence, copy a product manual, or turn one incident into a universal law.

Prefer:

- decision criteria and evidence selection;
- meaningful authorization and safety boundaries;
- conditions for widening, deviating, or stopping;
- progressive disclosure through focused references;
- realistic behavioral evaluations;
- defaults with reasons, exceptions, and expected proof.

Avoid:

- exhaustive command catalogs;
- organization-specific policy presented as universal truth;
- ceremonial process or test repetition;
- compatibility shims without a maintained consumer;
- claims of performance, correctness, currency, or support without evidence.

## Public-by-construction workflow

Do not copy a private skill directory or its Git history into this repository. Reconstruct the reusable method in a clean public tree.

Classify source material before writing:

- **Reusable:** general decision frameworks, evidence semantics, validation logic, and synthetic evaluation cases.
- **Rewrite:** lessons that remain useful after names, topology, metrics, and local policy are removed.
- **Private:** secrets, credential locations, private domains, workstation paths, repository names, branch or release state, internal targets, customer data, unpublished incidents or vulnerabilities, and infrastructure topology.

Redaction is not enough. Ask whether harmless-looking target names, scale figures, rollout language, providers, or file locations combine to reconstruct a private system.

Use synthetic labels such as `//service:api` and generic paths such as `path/to/target`. Do not replace one private identifier with a thin pseudonym while preserving its surrounding topology.

## Rights and license

By contributing, you certify that:

- you authored the contribution or have the right to submit it;
- it does not copy employer, customer, or other privately owned skill material without permission;
- it contains no secrets or confidential information;
- you agree that the contribution is licensed under this repository's MIT License.

The project uses an inbound-equals-outbound model and does not currently require a separate contributor license agreement.

## Skill structure

Every portable skill requires:

```text
skills/<skill-name>/
|-- SKILL.md
|-- LICENSE.txt
|-- agents/          Optional client adapters
|   `-- openai.yaml
`-- references/      Optional progressive-disclosure material
```

Requirements:

- use lowercase letters, digits, and hyphens for the skill name;
- keep the frontmatter description concise and discriminating;
- keep automatic discovery enabled unless explicit-only behavior is deliberate;
- put shared routing and essential constraints in `SKILL.md`;
- place substantial mode-specific guidance in references and link it from the entrypoint;
- keep one maintained source for each detailed instruction;
- write repository content in English.

OpenAI metadata is required only for skills claiming Codex support. Other adapters may be added after their behavior is tested. Scripts and assets are welcome only when they materially improve repeatability or generated output.

## Behavioral evaluation

Test decisions rather than exact wording. Include realistic cases covering:

- implicit discovery and explicit invocation in separate fresh sessions;
- a request that should trigger the skill and a nearby request that should not;
- read-only and mutation-authorized boundaries;
- a small evidence surface and a condition that requires widening;
- uncertainty, degraded state, and a real stop condition;
- a hard failure for authorization violations and material misrouting.

Keep expected decisions hidden from the agent under test. Avoid tests that merely match headings, regex phrases, or generated prose.

## Validation

Before proposing a change, run:

```text
python tools/validate_repository.py --history
python -m unittest discover -s tests -v
```

If the skill came from private practice, also pass uncommitted private terms:

```text
python tools/validate_repository.py --history --private-term project-codename --private-term private-host.example
```

Review every diff manually for semantic leakage. Automated scanning cannot decide whether architecture, metrics, or workflow details reveal a private system.

## Review checklist

- The skill changes meaningful decisions and has a clear trigger boundary.
- User authorization is preserved.
- Repository facts outrank examples and remembered versions.
- Diagnostic evidence is not mislabeled as formal acceptance.
- Widening and stopping conditions are explicit.
- References are discoverable and loaded only when useful.
- Examples are synthetic and project-neutral.
- The contributor has the right to submit the material under MIT.
- No private history, identifiers, topology, metrics, credentials, or unpublished vulnerabilities are present.
- Structure, links, tests, plugin metadata, and bounded hygiene validation pass.
