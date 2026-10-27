# Modelo de datos lógico (base inicial)

No es un esquema SQL definitivo; el esquema físico debe seguir a la auditoría y documentarse con migraciones Alembic.

## Entidades

- `users`: id, email normalizado, password hash o subject de proveedor de identidad, status, created_at, last_login_at.
- `roles` / `user_roles`: roles globales y permisos específicos, con restricciones explícitas.
- `candidate_profiles`: user_id, nombre público/pseudónimo, ciudad/ubicación opcional, modalidad, idiomas, resumen confirmado, estado, consent timestamps.
- `candidate_skills`: candidate_id, skill canonical, nivel auto-declarado/evaluado, source/evidence refs, confidence, updated_at.
- `candidate_documents`: owner_id, private storage key, MIME, hash, state, retention deadline, extracted text ref (si se guarda), parser version, deleted_at.
- `projects`: owner_id, URL GitHub/portfolio, repo ID, description, evidence refs, ingestion time, consent/source, repo visibility.
- `companies`: id, name, approved domains/verification state, public facts source.
- `company_members`: company_id, user_id, role; autorización por empresa.
- `jobs`: company_id nullable para importadas, source_id, external_id, URL, title, description, skills/requirements, location, mode, contract type, salary fields with currency/range, published/expiry/last_seen, content hash, status.
- `job_sources`: source name, source URL, access type, ToS review, polling interval, last run, status, contact, permitted fields and policy review date.
- `embeddings_index_state`: entity ref, model id/version, text/content hash, vector collection/id, status/time. Vector payload vive en Qdrant.
- `match_runs`: version of algorithm/model/config, run timestamp, input version IDs, candidate set, result metadata, explainability factors; restrict retention.
- `match_results`: run_id, candidate_id, job_id/company_id, score scale version, factors/evidence references, uncertainty, review status. Not a hiring decision.
- `interests`: actor_type/id, target_type/id, action, created_at, revoked_at; unique active interest constraints.
- `mutual_matches`: candidate_id, company_id/job_id, state, unlocked_at, created_at; only service can create after mutual interest.
- `applications`: candidate_id, job_id, status, date, confirmed_by_user, source_url, notes; manual/confirmed record, not automatic external submission.
- `consents`: user_id, purpose, version, granted_at, withdrawn_at, source; avoid generic all-purpose consent.
- `audit_events`: actor, action, entity type/id, timestamp, correlation_id, outcome, policy/model version if applicable; no CV contents, secrets or unnecessary payload snapshots.
- `background_jobs`: job type, idempotency key, status, retries, started/completed/error category, not sensitive payload dump.
- `model_registry` / `evaluation_runs`: model and prompt hashes, dataset version, metric, subgroup analysis, run config, artifacts location.

## Important constraints

- Separate `profile data` from `blind review projection`; compute the latter server-side with explicit allowlist of fields.
- Apply company tenancy to every query and audit negative cross-tenant tests.
- Foreign keys and deletion workflows must cover document files, vector points, exports and logs according to retention/legal-hold policy.
- `job_sources` must record source permission/status; scraper can be disabled per source.
- Do not keep arbitrary CV text in vector payloads or logs by default.
- Use canonical skill taxonomy IDs plus observed raw terms and evidence; don't infer expertise from language alone.
