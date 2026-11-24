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
- [CANDIDATE_PROFILE.md](CANDIDATE_PROFILE.md) — Perfil de candidato (B-03, FR-002): endpoints, decisiones, esquema físico y criterios de aceptación con sus pruebas.

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
- [NARRATIVE_V0.md](NARRATIVE_V0.md) — Narrativa v0 (problema, propuesta de valor y límites honestos para sesión transversal, `[R-03]`).


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

## 7. Estado del repositorio (verificado 24/11/2026)

- **Estado del proyecto**: implementación de producto en curso. El repositorio contiene `backend/` y `frontend/`.
- **Backend**: Python, FastAPI y SQLAlchemy; incluye autenticación/autorización B-02 y endpoints de observabilidad P-05. La rama de trabajo actual desarrolla B-03 (perfil de candidato).
- **Frontend**: existe `frontend/package.json`; su estado funcional y nivel de integración deben verificarse por separado.
- **Rama local de trabajo**: `feat/candidate-crud`.
- **Último commit de HEAD**: `b10c15f` — `merge: integrate B-02 authentication into P-05 observability`.
- **Alcance en curso**: B-03 — CRUD del perfil de candidato, skills declaradas, preferencias y visibilidad (issue #30).
- **Estado de B-03**: cambios implementados y validados localmente; todavía sin commit ni push. Los archivos modificados y nuevos permanecen en el árbol de trabajo.
- **Calidad del backend B-03**: última validación local con 484 tests superados, cobertura de ramas del 97,98 %, Ruff y mypy sin errores.
- **Migración B-03**: definida en Alembic, pero todavía no ejecutada.
- **CI y despliegue**: su estado operativo debe comprobarse en GitHub Actions y en el entorno de despliegue; la existencia de los archivos de configuración no demuestra por sí sola que estén funcionando.
- **Documento rector**: Propuesta Integral Bilateral MVP v5.0, disponible en el canal del equipo y no versionada en el repositorio.
- **Fuente de verdad del alcance**: requisitos, matriz de trazabilidad, backlog y decisiones documentadas, junto con el documento rector. El estado de ejecución debe contrastarse con GitHub Issues/Projects.
- **Nota**: este índice refleja el estado verificado en la fecha indicada; debe actualizarse cuando se integren nuevas funcionalidades o cambie el estado de las ramas.
