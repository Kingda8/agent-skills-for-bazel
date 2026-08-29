# Agent Skills for Bazel instructions

- Write repository content, source, and comments in English.
- Preserve user authorization. Inspection does not imply editing, and local validation does not imply publication.
- Keep skills project-neutral and public by construction. Never commit private identifiers, paths, topology, metrics, incidents, credentials, or unpublished vulnerabilities.
- Encode non-obvious decision logic, evidence semantics, widening conditions, and stop conditions. Remove generic advice and brittle recipes.
- Keep `SKILL.md` focused on shared routing and constraints. Use references for substantial conditional guidance.
- Use synthetic examples and labels. Do not pseudonymize a private system while preserving recognizable structure.
- Prefer small cohesive files. Keep `SKILL.md` at or below 400 physical lines and maintained Markdown or Python files below 600.
- Use `apply_patch` for hand-written file edits. Preserve unrelated changes in a dirty worktree.
- Run `python tools/validate_repository.py --history` and `python -m unittest discover -s tests -v` after material changes.
- Do not claim automatic scanning proves the absence of semantic leakage.
- Do not publish, push, create releases, enable external services, or mutate other external systems without explicit authorization.
