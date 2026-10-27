# Security, privacy and data governance baseline

> This is engineering guidance, not legal advice or a declaration of compliance. Get qualified privacy/legal review for the actual deployment and the role of each party.

## Data inventory

For each field/document, record purpose, source, legal basis/consent process, role access, storage, recipients/providers, retention, deletion behavior and whether sent to an LLM. Collect only the minimum data needed for the purpose.

## Controls required before real user data

- TLS in transit; encrypted disks/object storage/managed database at rest where available.
- Secrets outside Git; least-privilege credentials, rotation and separate dev/staging/prod environments.
- Passwords hashed with a suitable modern password hashing scheme, or a trusted identity provider. Never log auth tokens.
- Server-side authorization, tenant isolation, rate limits, upload size/type limits, parser sandboxing/timeouts and safe file names.
- Protect against SSRF, SQL injection, XSS, CSRF where applicable, broken access control, insecure redirects, path traversal and malicious file uploads.
- Validate GitHub/repository URLs and prevent server-side requests to internal/private network targets; prefer API client with allowlisted hosts.
- Structured logs must redact email, phone, CV text, tokens, cookies, personal prompts and content fields.
- Backups encrypted; restoration drills; define deletion's treatment of backups and legal obligations.
- Retention job for expired CVs, derived text/embeddings, temporary artifacts and candidate exports.
- Dependency lockfiles, vulnerability scans, secret scanning and code review.

## GDPR work items

- Define controller/processor roles and purposes; document lawful basis and informed consent where applicable.
- Provide privacy notices and data-subject paths for access, correction, objection/withdrawal as applicable, portability where required, and erasure.
- Data minimization, purpose limitation, storage limitation and data protection by design/default.
- Assess whether a DPIA is needed due to employment-related profiling/monitoring and planned scale/context.
- Document providers and international transfers/retention; don't send CVs to an LLM provider before approval and disclosure.
- Special-category data must not be inferred/used for ranking; demographic attributes may be collected for fairness auditing only under approved governance and kept separate from decision features.

## Threat model

- Unauthorized candidate profile or CV access by another candidate/company.
- Blind-review field leakage via API, cache, logs, analytics, vector payloads or error output.
- Prompt injection in CV, job description, GitHub README, web page or RAG corpus.
- Malicious PDF, oversized archive, parser vulnerability or SSRF.
- Compromised dependency, leaked API key, unsafe agent tool permission.
- Queue retry/duplicate creating inconsistent interest/match state.
- Model drift/disparate impact and falsely confident explanations.
- Apply Copilot filling wrong person’s data, selecting wrong dropdown or answering legal declaration incorrectly.

## LLM and agent controls

- Least-privilege tools and narrowly scoped context; read-only by default.
- Treat retrieved content as untrusted data; delimit it; never let it change system/developer policy.
- Tool output and generated text validated by schemas; no shell/SQL/browser actions based only on LLM output.
- Human approval for any externally visible/high-impact action; final submission always manual.
- Test direct/indirect prompt injection, data exfiltration, cross-tenant retrieval, harmful output and unbounded token/cost usage.

## Incident response

Document how to disable a source/worker/model, rotate credentials, isolate affected data, restore from backup, notify owners and review logs. The first demo must not depend on real CVs or production credentials.
