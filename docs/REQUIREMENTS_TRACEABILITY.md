# Matriz de trazabilidad de requisitos — SkillMatch
Estado: `VERIFIED_DOCUMENTAL` (no `VERIFIED_IMPLEMENTED`).
Fecha: 27/10/2026
Auditor: Agente fase 0.1

## Definición de estados documentales
- `COVERED`: requisito reflejado con detalle suficiente y vinculado a criterios verificables.
- `PARTIAL`: reflejado parcialmente o con detalle insuficiente.
- `MISSING`: no aparece en documentación existente.
- `DECISION_REQUIRED`: requiere aprobación de Vanessa (PO) antes de implementar.

Nota: `VERIFIED` solo cuando hay evidencia de test/reproducible; `NOT_IMPLEMENTED` mientras no haya código.

---

## Funcionales oficiales del brief

| ID oficial | Requisito oficial (resumen) | Documento SkillMatch | Estado doc. | Módulo futuro | Criterio de aceptación | Tests necesarios | Evidencia para VERIFICADO | Dependencias | Prioridad | Riesgo / bloqueo |
|---|---|---|---|---|---|---|---|---|---|---|
| FR-01 / FR-002 / FR-003 / FR-004 / FR-005 / FR-006 / FR-007 / FR-008 / FR-009 / FR-010 / FR-011 / FR-012 / FR-013 / FR-014 / FR-015 / FR-016 / FR-017 / FR-018 / FR-019 / FR-020 | Registro y CRUD dos roles (Candidate/Company); ingestión ofertas (API/scraping ético); análisis CV PDF; análisis GitHub API; matching embeddings + modelo ranking entrenado; % afinidad explicable; interés mutuo; desbloqueo contacto; asistente RAG empresa/oferta + preparación entrevista; agente mejora perfil + carta presentación; dashboard empresa; auditoría acciones; consentimiento/GDPR; Apply Copilot (stretch) | docs/REQUIREMENTS.md (FR-001 a FR-020); docs/ARCHITECTURE.md; docs/ROADMAP_6_WEEKS.md | COVERED (FR-001 a FR-020 presentes); PARTIAL (ranking entrenado: FR-010 indica que solo se llama "entrenado" si hay entrenamiento verificable; existe como requisito P1 con baseline) | identity, candidates, companies, jobs, ingestion, documents, github_evidence, matching, interactions, rag, agent_assist, audit, dashboard, browser_extension | Ver requisitos individuales por documento | Unit + integration + fixtures sintéticos | Código + tests + dataset sintético + evidencia de evaluación | Depende de esquema DB, auth, embeddings, datos sintéticos | P0 (FR-001 a FR-019); P1 (FR-010 ranking entrenado, FR-015 asistencia entrevista, FR-017 dashboard); P2 (FR-020 Apply Copilot) | FR-010: sin datos etiquetados no hay ranking entrenado; debe registrarse como riesgo. FR-015: requiere LangGraph para flujo de entrevista/feedback personalizado (ver Brecha A). FR-017: métrica 60% reducción cribado debe ser medida, no asumida (ver Brecha C). |

## Detalle de requisitos críticos del brief oficial (no omitidos)

### Brecha A — Entrevista inicial con IA y feedback personalizado (LangGraph)
- Requisito oficial: "Sistema Multi-Agente: Implementación en LangGraph para agenciar la entrevista inicial y simular feedback personalizado."
- Estado actual en docs/ARCHITECTURE.md: `agent_assist`: sugerencias editables de perfil, carta y preparación de entrevista.
- Estado actual en docs/REQUIREMENTS.md: FR-015 (asistente preparación entrevista, P1); FR-016 (sugerencias perfil/carta, P1).
- **Falta**: flujo específico de entrevista inicial con LangGraph que contemple: contexto autorizado, preparación de preguntas, recogida de respuestas, generación de feedback personalizado con fortalezas/mejoras/recomendaciones, distinción hechos/sugerencias, revisión humana, registro versión/fuentes/evaluación, casos de error/manipulación.
- **Corrección necesaria**: actualizar `docs/REQUIREMENTS.md` para incluir `FR-021` (o extender `FR-015`) con criterios de flujo LangGraph; crear documento `docs/INTERVIEW_AGENT_FLOW.md`; actualizar `docs/ARCHITECTURE.md` para incluir nodo `interview_agent` en módulo `agent_assist` con restricciones claras (no decisión automática).

### Brecha B — Modelo de ranking entrenado
- Requisito oficial: "Motor de matching con embeddings semánticos y un modelo de ranking entrenado, que muestra el porcentaje de afinidad y los motivos del match."
- Estado actual: `REQUIREMENTS.md` FR-010 indica correctamente que solo se debe llamar "entrenado" si hay entrenamiento verificable; `ARCHITECTURE.md` menciona "ranking aprobado" y línea base; `ROADMAP_6_WEEKS.md` menciona "ranking supervisado solo si hay dataset etiquetado válido".
- **Falta**: documento que defina explícitamente las 4 capas (recovery semántica, ranking entrenable, explicaciones, evaluación) con criterios detallados; documento `docs/MATCHING_EVALUATION.md` debe actualizarse con metodología de evaluación, dataset sintético, baseline, métricas y limitaciones.
- **Corrección**: actualizar `docs/MATCHING_EVALUATION.md`; actualizar `docs/REQUIREMENTS.md` para incluir criterio que exija dataset etiquetado o registro explícito de ausencia; añadir ADR si se decide implementar ranking con baseline explicable en lugar de modelo entrenado en MVP.

### Brecha C — Pipeline MLOps: Docker Hub, CI/CD y despliegue funcional
- Requisito oficial: "Contenerización completa con Docker, pipeline de integración continua con GitHub Actions y panel en FastAPI / React." + "Pipeline MLOps automatizado (Docker Hub + GitHub Actions) listo para entornos de producción." + "Entregable: Aplicación web desplegada y funcional."
- Estado actual: `ARCHITECTURE.md` menciona Docker Compose para local; `ROADMAP_6_WEEKS.md` menciona Docker comprobado desde máquina limpia; `REQUIREMENTS.md` NFR-010 menciona CI para build/test; `PROJECT_CHARTER.md` menciona demo funcional y aplicación desplegada.
- **Falta**: documento que diferencie claramente los 3 niveles: entorno local reproducible (Docker Compose), CI/CD (GitHub Actions con build + tests + security scan), publicación (Docker Hub con tags inmutables) y despliegue funcional (versión accesible con instrucciones). No hay documento `docs/DEPLOYMENT.md` ni `docs/DOCKER_HUB.md` con estrategia de etiquetado, secretos, rollback, health checks, registro de versión desplegada.
- **Corrección**: crear `docs/DEPLOYMENT.md` con los 3 niveles; actualizar `docs/REQUIREMENTS.md` NFR-010 para incluir criterios de despliegue funcional; actualizar `docs/ROADMAP_6_WEEKS.md` para asegurar que semana 6 incluye verificación de despliegue.

---

## Requisitos no funcionales oficiales (revisados)

| ID oficial | Requisito oficial (resumen) | Documento SkillMatch | Estado doc. | Criterio de aceptación actualizado | Pruebas / Evidencia | Dependencias | Prioridad | Riesgo / bloqueo |
|---|---|---|---|---|---|---|---|---|
| NFR-01 | Separación legacy/nuevo, reutilización mediante registro aprobado | docs/START_HERE.md, AGENTS.md, docs/LEGACY_AUDIT_RUNBOOK.md | COVERED | Repos separados; registro de reutilización (07-reuse-register.md) aprobado por Vanessa | Git status limpio en skillmatch; legacy intacto; matriz de reutilización documentada | Auditoría fase 0 completada | P0 | Ninguno (ya cumplido) |
| NFR-02 | Mantenibilidad: backend modular, type hints, lint, migraciones versionadas, README ejecución | docs/ARCHITECTURE.md; docs/LOCAL_DEVELOPMENT.md (incompleto) | PARTIAL | `pyproject.toml` o `setup.py` con lint, typecheck, Alembic; estructura modular definida | CI pasa lint/typecheck; README actualizado con instrucciones de ejecución | Esquema DB inicial, repositorio configurado | P0 | Falta archivo `LOCAL_DEVELOPMENT.md` completo y archivo de ejecución base |
| NFR-03 | Rendimiento vectorial: p95 <300 ms para retrieval top-k en datos/hardware documentados | docs/REQUIREMENTS.md (NFR-003); docs/ARCHITECTURE.md; docs/MATCHING_EVALUATION.md | PARTIAL | Benchmark reproducible; dataset definido; latencia separada por componente (retrieval, embedding, reranking) | Pruebas con datos sintéticos; registro p50/p95/p99 | Datos sintéticos; Qdrant configurado; embeddings definidos | P1 | Requisito no debe confundirse con latencia de generación LLM o parsing PDF; debe documentarse claramente |
| NFR-04 | Disponibilidad observable: health/readiness, logs estructurados, error IDs, métricas básicas | docs/ARCHITECTURE.md (logs mínimos); docs/OBSERVABILITY_RUNBOOK.md | COVERED | Logs sin PII; error IDs; métricas básicas; no prometer SLA productivo sin despliegue real | Pruebas de error; verificación de logs sin datos personales | Infraestructura desplegada | P1 | Ninguno |
| NFR-05 | Seguridad: autorización servidor, secretos seguros, límites de tasa, validación uploads, tests acceso indebido | docs/SECURITY.md; docs/ARCHITECTURE.md; docs/SECURITY_PRIVACY.md | COVERED (documental) | Autenticación y autorización implementadas; secrets fuera de código; tests negativos de acceso | Tests de seguridad; revisión de código | Auth implementado | P0 | Ninguno documental |
| NFR-06 | Privacidad: minimización, retención limitada, borrado, acceso por finalidad, datos sintéticos | docs/SECURITY.md; docs/SECURITY_PRIVACY.md; docs/AI_GOVERNANCE.md | COVERED | Datos sintéticos en tests; mecanismos de consentimiento y borrado definidos; minimización aplicada | Pruebas con datos sintéticos; verificación de borrado | Modelo de datos con consentimiento | P0 | Ninguno |
| NFR-07 | Equidad: auditoría de sesgos, variables/proxies, límites y mitigaciones documentadas | docs/AI_GOVERNANCE.md; docs/SECURITY.md | COVERED (documental) | Protocolo de auditoría documentado; variables sensibles no usadas como filtros sin base; resultados revisables | Auditoría con datos sintéticos; registro de decisiones | Datos sintéticos; evaluación del ranking | P0 | Requiere datos etiquetados para evaluación real; debe registrarse como riesgo |
| NFR-08 | Supervisión humana: resultados informativos, overrides registrables, no decisión laboral autónoma | docs/ARCHITECTURE.md; docs/AI_GOVERNANCE.md; docs/REQUIREMENTS.md (FR-010 nota) | COVERED | Score no es probabilidad de contratación; override humano posible y registrado; no envío automático | Pruebas de interacción humana; verificación de explicaciones | Modelo de ranking definido | P0 | Ninguno |
| NFR-09 | Reproducibilidad: dataset/modelos/prompts/configs/versionados; evaluación repetible | docs/REQUIREMENTS.md (NFR-009); docs/ARCHITECTURE.md | PARTIAL | Dataset sintético versionado; modelos/versiones documentados; evaluación repetible con mismo seed/config | Pruebas con datos sintéticos; registro de versiones | Datos sintéticos; embeddings/modelos definidos | P1 | Falta dataset sintético versionado; debe crearse |
| NFR-10 | CI/CD: CI para test/lint/typecheck/build y scan dependencias; deploy manual/protegido | docs/ROADMAP_6_WEEKS.md; docs/ARCHITECTURE.md; docs/REQUIREMENTS.md (NFR-010) | COVERED (documental); PARTIAL (no hay CI real aún) | `.github/workflows/` básico; build de imagen; deploy manual/protegido; registro de versión desplegada | CI pasa en máquina limpia | Repo configurado; Dockerfile creado | P0 | Brecha C: falta documento de despliegue completo y verificación funcional |
| NFR-11 | Accesibilidad/usabilidad: flujos principales en móvil/desktop; navegación teclado básica | docs/ARCHITECTURE.md; docs/REQUIREMENTS.md (NFR-011) | COVERED (como objetivo, no verificado) | UI probada en desktop/móvil; navegación básica con teclado | Pruebas manuales / Playwright | Frontend básico construido | P1 | Ninguno |

---

## Entregables oficiales del brief (trazabilidad)

| Entregable oficial | Documento SkillMatch | Estado doc. | Tarea en backlog | Criterio de verificación |
|---|---|---|---|---|
| Código modular con pruebas, tipado, documentación | docs/REQUIREMENTS.md; docs/ARCHITECTURE.md; docs/LOCAL_DEVELOPMENT.md | PARTIAL | P0: estructura modular + CI; P1: tests + tipado completo | CI pasa; código cubierto; README actualizado |
| Pipeline MLOps reproducible con CI y Docker | docs/ARCHITECTURE.md; docs/ROADMAP_6_WEEKS.md; docs/REQUIREMENTS.md (NFR-010) | COVERED (documental) | P0: Docker Compose; P1: Docker Hub + CI; P2: deploy funcional | Imagen construida; CI verde; imagen publicada; app accesible |
| Informe gobernanza, privacidad, auditoría sesgos y riesgos | docs/AI_GOVERNANCE.md; docs/SECURITY.md; docs/SECURITY_PRIVACY.md | COVERED | P1: documento actualizado; P2: evaluación con datos sintéticos | Documento revisado; auditoría documentada |
| Evaluación del matching/ranking y model card (si aplica modelo ML entrenado) | docs/MATCHING_EVALUATION.md; docs/REQUIREMENTS.md (FR-010) | PARTIAL | P1: evaluación con datos sintéticos; P2: model card si hay modelo entrenado | Dataset sintético; métricas documentadas; limitaciones claras |
| Demo funcional con datos sintéticos | docs/PROJECT_CHARTER.md (sección éxito); docs/ROADMAP_6_WEEKS.md | COVERED | P0-P6: demo reproducible en semana 6 | Demo funcional sin datos secretos; reproducible en máquina limpia |
| Informe auditoría legacy y decisión reconstrucción | docs/legacy-audit/* (01 a 09) | COMPLETED | P0: auditoría completa; registro reutilización aprobado | 9 informes presentes; legacy intacto; registro de reutilización documentado |

---

## Métricas de negocio oficiales (revisadas)

| Métrica oficial | Documento SkillMatch | Estado | Metodología | Evidencia necesaria | Estado medido (hipótesis vs. verificado) |
|---|---|---|---|---|---|
| Reducción 60% tiempo cribado inicial | docs/PROJECT_CHARTER.md (sección Éxito); docs/REQUIREMENTS.md (nota interpretación) | COVERED (como objetivo medible, NO como resultado garantizado) | Fórmula definida: `((tiempo referencia - tiempo SkillMatch) / tiempo referencia) × 100`; tiempo de referencia medido con datos sintéticos; comparación con baseline; limitaciones registradas | Estudio de referencia con datos sintéticos; medición con SkillMatch; registro porcentual; limitaciones documentadas | NO VERIFICADO (hipótesis pendiente de medición con datos sintéticos) |
