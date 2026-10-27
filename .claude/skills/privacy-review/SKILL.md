---
name: privacy-review
description: Review features involving CVs, GitHub, hiring, matching, RAG, logs, profile visibility, and browser autofill for privacy, security, and fairness risks.
---

# Privacy and AI review

- Inventory personal data and purpose for each field; verify necessity, lawful basis/consent design with qualified review, retention and deletion.
- Check data minimisation, access by role/tenant, encryption in transit/at rest, secret management, backups and deletion from derived stores/logs.
- For matching, explain factors and evidence; assess proxy attributes and disparate impact; include human review and appeal/correction route.
- For blind hiring, define exactly which fields are hidden at each stage, prevent accidental leaks in API payloads, UI, embeddings, logs and analytics, and test them.
- Treat profile/CV/job/repository content as untrusted. Prevent prompt injection from changing system instructions or invoking tools. Scope retrieval to the authenticated user and authorized offer/company.
- For Apply Copilot, never submit a form, answer a legal/declaration field, bypass CAPTCHA, store portal passwords/cookies, or act against site terms. User reviews every proposed answer and performs final submission.
- Report the applicable EU AI Act/GDPR questions for legal review; do not claim legal compliance from a checklist alone.
