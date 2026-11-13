# Índice maestro de documentación — SkillMatch

Estado: fase 0.1 consolidada; sin código de producto implementado | Última revisión: 13/11/2026 | Último commit: `6d03022`

Este archivo es la única puerta de entrada a la documentación del repositorio. Los enlaces son relativos a `docs/` (donde vive este archivo). Si un documento no aparece aquí, o no existe, o no es parte del alcance vigente.

## Regla cero (leer primero)

- [AGENTS.md](../AGENTS.md) — Instrucciones del proyecto para agentes.
- [START_HERE.md](../START_HERE.md) — Qué es, qué hacer y qué NO hacer.
- [PROJECT_CHARTER.md](PROJECT_CHARTER.md) — Identidad, alcance, métricas y principios no negociables.
- [DECISION_LOG.md](DECISION_LOG.md) — Registro de decisiones de producto y proceso (`D-01`…`D-12`).
- **Propuesta Integral Bilateral MVP v5.0** — documento rector de alcance y ejecución (no versionado en este repositorio por ser un PDF con datos de terceros; disponible en el canal del equipo). Si hay conflicto de alcance, este documento manda; si hay conflicto de arquitectura, mandan los ADR.

## 1. Requisitos oficiales (fuente de verdad)

- [REQUIREMENTS.md](REQUIREMENTS.md) — `FR-001`…`FR-020`, `NFR-001`…`NFR-011`, entregables y notas de interpretación (incluye `FR-015` flujo LangGraph y `FR-015-ext` agente de perfil).
- [REQUIREMENTS_TRACEABILITY.md](REQUIREMENTS_TRACEABILITY.md) — Matriz completa con estados (`COVERED` / `PARTIAL` / `DECISION_REQUIRED` / `NOT_IMPLEMENTED`), criterios, dependencias y evidencia necesaria.
- [REQUIREMENTS_GAP_ANALYSIS.md](REQUIREMENTS_GAP_ANALYSIS.md) — Brechas A (LangGraph entrevista/feedback), B (ranking entrenado vs. baseline) y C (CI/Docker/despliegue); métrica 60 % como hipótesis; decisiones pendientes con responsables.

## 3. Arquitectura y decisiones técnicas

- [ARCHITECTURE.md](ARCHITECTURE.md) — Propuesta (`PROPOSED`): FastAPI + React + PostgreSQL + Qdrant + Docker Compose; módulos; flujo de matching (6 pasos); RAG; rendimiento (<300 ms); límites (monolito modular, datos sintéticos, blind hiring, sin datos reales sin base).
- [DEPLOYMENT.md](DEPLOYMENT.md) — 3 niveles: local reproducible (`docker-compose`); CI/GitHub Actions (build + tests + scan); despliegue funcional (tag inmutable, rollback, health checks, registro de versión, sin datos reales ni secretos).
- [TECH_STACK.md](TECH_STACK.md) — Stack técnica propuesta y dependencias.
- [DATA_MODEL.md](DATA_MODEL.md) — Esquema de datos previsto.

Registro de decisiones de arquitectura (ADRs). Las decisiones de producto y proceso no van aquí: están en [DECISION_LOG.md](DECISION_LOG.md).

- [decisions/ADR-0002-stack-inicial.md](decisions/ADR-0002-stack-inicial.md) — Stack inicial.
- [decisions/ADR-0003-source-of-truth-vectors.md](decisions/ADR-0003-source-of-truth-vectors.md) — Fuente de verdad de vectores (reconstrucción desde datos minimizados).
- [decisions/ADR-0004-jobs-async.md](decisions/ADR-0004-jobs-async.md) — Procesamiento asíncrono en segundo plano.
- [decisions/ADR-0005-matching-explicabilidad.md](decisions/ADR-0005-matching-explicabilidad.md) — Explicabilidad y límites del score de matching.
- [decisions/ADR-0006-agent-harness.md](decisions/ADR-0006-agent-harness.md) — Harness de agentes y límites de autonomy.

## 4. Evaluación y gobernanza de IA

- [MATCHING_EVALUATION.md](MATCHING_EVALUATION.md) — 4 capas (recuperación semántica / ranking / explicaciones / evaluación); baseline sin entrenar (Fase A); ranking aprendido solo con datos etiquetados (Fase B); latencia separada; la métrica 60 % no es probabilidad de contratación.
- [AI_GOVERNANCE.md](AI_GOVERNANCE.md) — Gobernanza de IA, privacidad, GDPR, supervisión humana, registro de decisiones y auditoría de sesgos.
- [SECURITY_PRIVACY.md](SECURITY_PRIVACY.md) — Seguridad y privacidad (autenticación, autorización, datos sintéticos, sin PII en logs).
- [SECURITY.md](../SECURITY.md) — Política de reporte de vulnerabilidades.
- [APPLY_COPILOT_SPEC.md](APPLY_COPILOT_SPEC.md) — Especificación del Apply Copilot (sugerencia/rellenado; nunca auto-envío).
- [OBSERVABILITY_RUNBOOK.md](OBSERVABILITY_RUNBOOK.md) — Runbook de observabilidad, health checks y registro de auditoría.

## 5. Equipo, proceso y gobierno

- [PROJECT_CHARTER.md](PROJECT_CHARTER.md) — Identidad, roles, principios, criterios de éxito, MVP, fuera de alcance, restricciones y supuestos.
- [RACI.md](RACI.md) — Matriz RACI inicial (equipo técnico propuesto, aún por validar).
- [TEAM_WORKING_AGREEMENT.md](TEAM_WORKING_AGREEMENT.md) — Roles (PO/SM), reparto inicial, cadencia sugerida y acuerdos de trabajo con agentes.
- [ROADMAP_6_WEEKS.md](ROADMAP_6_WEEKS.md) — Cronograma 2 nov.–11 dic. 2026 con gating; salidas por semana.
- [QUALITY_GATES.md](QUALITY_GATES.md) — Checks de pull request y objetivo de merge.
- [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md) — Criterios de terminación (`VERIFIED` solo con evidencia de test o demo reproducible).
- [PRODUCT_NAME_DECISION.md](PRODUCT_NAME_DECISION.md) — Decisión pendiente del nombre público (`PENDING_PO_DECISION`); `SkillMatch` sigue siendo codename provisional.
- **Propuesta Integral Bilateral MVP v5.0** — documento rector de alcance y ejecución (externo al repositorio, disponible en el canal del equipo). Origen de las decisiones `D-01`…`D-12`, del backlog `US-01`…`US-18`, del equipo/RACI, de la metodología y de la demo.
- [DECISION_LOG.md](DECISION_LOG.md) — Decisiones de producto y proceso (`D-01`…`D-12`) con estado, responsable, evidencia y fecha de revisión.
- [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md) — Snapshot del backlog de producto de la v5.0 (`US-01`…`US-18`, MoSCoW) y Definition of Ready; el tracker vivo está en GitHub Issues/Projects.

## 6. Operación y desarrollo

- [CONTRIBUTING.md](CONTRIBUTING.md) — Cómo contribuir (alcance, commits, revisiones).
- [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) — Entorno local reproducible.
- [HARNESS_AND_AGENT_WORKFLOW.md](HARNESS_AND_AGENT_WORKFLOW.md) — Flujo de trabajo con agentes y reglas de coordinación.
- [LEGACY_AUDIT_RUNBOOK.md](LEGACY_AUDIT_RUNBOOK.md) — Procedimiento reproducible de auditoría.
- [REFERENCES.md](REFERENCES.md) — Referencias externas y fuentes normativas citadas.
- [AUDIT_FIRST_PROMPT.md](../AUDIT_FIRST_PROMPT.md) — Prompt de arranque de la auditoría (fase 0).
- [CLAUDE.md](../CLAUDE.md) — Adaptador de instrucciones para Claude Code.
- [.claude/](../.claude/) — Mismas habilidades para Claude Code.
- [.cursor/](../.cursor/) — Reglas de editor para Cursor.
- [.github/](../.github/) — Plantillas de issue y PR, instrucciones para Copilot y workflows de CI.
- [../.github/workflows/ci.yml](../.github/workflows/ci.yml) — CI mínimo (enlaces de documentación, escaneo heurístico de secretos, lint/tests cuando exista `backend/` o `frontend/`).
- [../scripts/](../scripts/) — Scripts de apoyo: `legacy_inventory.sh` y `check_foundation.sh`.
- [../.env.example](../.env.example) — Plantilla de variables de entorno (solo valores de desarrollo; nunca secretos reales).

## 7. Estado del repositorio (verificado 13/11/2026)

- **Alcance de este PR/rama**: establece el marco de gobernanza documental y CI — `INDEX.md`, `DECISION_LOG.md`, `PRODUCT_BACKLOG.md` y `.github/workflows/ci.yml`.
- **Documento rector**: Propuesta Integral Bilateral MVP v5.0 (disponible en el canal del equipo, no versionada en el repositorio por ser un PDF con datos de terceros). Es la fuente de alcance y ejecución; las decisiones `D-01`…`D-12` y el backlog `US-01`…`US-18` derivan de ella.
- **Último commit base**: `6d03022`. Rama: `docs/kickoff-alignment-v5`. Remoto: `origin` → `https://github.com/JCRbit/skillmatch.git`.
- **Código de producto**: no implementado. No existe `backend/` ni `frontend/`; no hay datos sintéticos generados; no hay `Dockerfile` ni `docker-compose.dev.yml`.
- **CI**: definido en [.github/workflows/ci.yml](../.github/workflows/ci.yml). Los pasos de lint/tests se activan solos cuando existan `backend/pyproject.toml` o `frontend/package.json`.
- **Decisiones**: las 12 decisiones oficiales de la v5.0 (`D-01`…`D-12`) están en estado `DECISION_PENDING`. Ver [DECISION_LOG.md](DECISION_LOG.md).
- **Backlog**: snapshot del backlog de la v5.0 (`US-01`…`US-18`) en [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md); el tracker vivo está en GitHub Issues/Projects.
- **Bloqueos abiertos**: nombre definitivo del producto, datos sintéticos, y los conflictos de alcance entre la v5.0 y la documentación vigente listados en [DECISION_LOG.md](DECISION_LOG.md) §3.
- **Nota**: el estado de ejecución real no es verificable desde este repositorio; el tracker vivo está en GitHub.
