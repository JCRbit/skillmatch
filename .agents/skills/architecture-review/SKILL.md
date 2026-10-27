---
name: architecture-review
description: Review a proposed or changed system design against requirements, simplicity, privacy, reliability, latency, operations, and ADRs.
---

# Architecture review

1. Read `AGENTS.md`, relevant requirements and existing ADRs.
2. Draw the data flow and trust boundaries. Identify data owners, failure modes and external dependencies.
3. Verify every new service has a concrete requirement, expected operating cost, local test path and fallback.
4. Check system-of-record boundaries (PostgreSQL canonical; Qdrant derived), tenant isolation, deletion/re-index workflow, idempotency, retries, observability and restore path.
5. Evaluate p95 latency and load using a reproducible workload. Never assert a latency target without measurements and hardware/software details.
6. Check least privilege, secrets, prompt injection, personal data exposure and human override.
7. Report `PASS`, `PASS WITH RISKS`, or `BLOCKED`; create/update ADR rather than silently changing design.
