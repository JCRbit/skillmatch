---
name: implement-issue
description: Implement one approved issue with minimal scope, tests, traceability, and a reviewable patch.
---

# Implement one issue

1. Confirm PO-approved issue, requirement IDs, non-goals and acceptance criteria. During phase 0, implementation is prohibited unless explicitly authorized in writing by PO.
2. Inspect working tree and relevant files. Never overwrite uncommitted work.
3. Propose a brief plan and identify risky assumptions before edits.
4. Work on a feature branch/worktree isolated to that task. Do not share writable files with parallel agents.
5. Make the smallest coherent change. Do not refactor unrelated code or upgrade unrelated dependencies.
6. Add tests that prove acceptance criteria and likely regressions. Include negative authorization/privacy cases where relevant.
7. Run format, lint, typecheck, unit/integration tests that apply. Record exact commands and result; mark not-run honestly.
8. Review diff for secrets, PII, migration safety, dependencies, license and unintended files.
9. Update requirement traceability and docs/ADR if behavior or architecture changes.
10. Return summary, changed files, requirement IDs, tests, risks and evidence. Do not merge or deploy autonomously.
