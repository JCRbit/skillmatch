# Requisitos y trazabilidad

Estados permitidos: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `VERIFIED`, `DEFERRED`. No marcar `VERIFIED` sin evidencia de test o demo reproducible.

> **Nota de alcance (`[G-02]`, 20/11/2026):** Requisitos alineados con las decisiones aprobadas `D-01`–`D-11` (`DECISION_LOG.md`) y el backlog `M0`–`M4`. El scraping externo (`FR-005`), el análisis automático de CV PDF (`FR-006`) y Apply Copilot (`FR-020`) quedan fuera del MVP (`DEFERRED`).

## Funcionales

| ID | Requisito | Criterio de aceptación | Prioridad | Verificación inicial |
|---|---|---|---|---|
| FR-001 | Registro/autenticación y roles Candidate, Company, Admin | Pruebas de acceso válido/inválido y permisos por rol; endpoints rechazan acceso cruzado | P0 | Tests API |
| FR-002 | CRUD de perfil candidato | Crear, consultar, editar y eliminar/solicitar borrado; validación de datos | P0 | API + UI tests |
| FR-003 | CRUD de empresa y ofertas | Empresa solo modifica sus ofertas; otras cuentas no acceden | P0 | Tests de autorización |
| FR-004 | Ingestión y normalización de oferta | Esquema común con fuente, URL, fechas, identificador externo y estado de publicación | P0 | Fixture + integration test |
| FR-005 | Fuente ética/legal para ofertas | Cada conector tiene fuente, términos revisados, política de frecuencia y mecanismo de desconexión | P0 | Registro de fuentes |
| FR-006 | Análisis de CV PDF | Extrae texto/atributos con validación, errores controlados, eliminación del archivo según política | P0 | Fixtures sintéticas |
| FR-007 | Análisis de GitHub | Solo repos autorizados/públicos o acceso explícito; rate limits; registra referencias a evidencia | P0 | Fixtures/API mocked |
| FR-008 | Matching semántico candidato↔oferta | Top-k reproducible con filtros estructurados y semánticos | P0 | Dataset de evaluación |
| FR-009 | Explicación del matching | Cada resultado muestra factores, evidencia, incertidumbre y carencias; explicación coincide con datos usados | P0 | Tests de contrato y evaluación humana |
| FR-010 | Modelo/ranking evaluable | Línea base explícita; dataset, métricas, split, versión y limitaciones documentadas; solo llamar “entrenado” si hubo entrenamiento verificable | P1 | Informe de evaluación |
| FR-011 | Interés mutuo | Un solo interés no revela contacto; dos intereses válidos crean match de manera idempotente | P0 | Tests de estado/seguridad |
| FR-012 | Vista ciega temprana | API/UI/exports/logs no filtran campos bloqueados antes de etapa autorizada | P0 | Tests negativos de filtración |
| FR-013 | Canal de contacto tras match | Solo las dos partes del match pueden ver los datos definidos | P0 | Tests de autorización |
| FR-014 | RAG de empresa/oferta | Respuestas restringidas a contexto autorizado; referencias a fuentes; fallback de desconocimiento | P1 | Corpus sintético + tests adversariales |
| FR-015 | Asistente de preparación de entrevistas — flujo LangGraph (entrevista inicial + feedback personalizado) | Contexto autorizado; preparación de preguntas; recogida respuestas; feedback personalizado con fortalezas/mejoras/recomendaciones; distinción hechos/sugerencias; revisión humana; registro versión/fuentes/resultados; casos error/manipulación | P1 | Dataset sintético + evaluación del flujo + pruebas adversariales | No implementar sin datos y criterios; no tomar decisiones laborales automáticas |
| FR-015-ext | Agente de apoyo al perfil (mejoras + carta) | Borradores editables; sustento por datos del usuario; nunca envío automático; revisión humana | P1 | Pruebas con perfiles sintéticos |
| FR-016 | Sugerencias de perfil y carta | Borradores editables sustentados por datos del usuario; nunca envío automático | P1 | Pruebas con perfiles sintéticos |
| FR-017 | Dashboard empresa | Métricas de pipeline y estados agregados con supresión de grupos pequeños cuando proceda | P1 | Test UI + cálculos |
| FR-018 | Auditoría de acciones | Registra quién hizo qué, cuándo, entidad, resultado y versión relevante, sin guardar payloads sensibles innecesarios | P0 | Tests de auditoría |
| FR-019 | Gestión de consentimiento/datos | Explicar uso, permitir retirar consentimiento/borrado conforme a política; limpieza de índices derivados y backups según diseño | P0 | Tests de ciclo de vida |
| FR-020 | Apply Copilot (stretch) | Rellena campos estándar en sitios de prueba; propuesta revisable; no submit automático, no credenciales/cookies | P2 | Playwright fixtures/manual |

## No funcionales

| ID | Requisito | Criterio de aceptación | Prioridad |
|---|---|---|---|
| NFR-001 | Separación legacy/nuevo | Repos separados; legacy read-only durante auditoría; reutilización mediante registro aprobado (`ADR-0001`, `[R-02]`) | P0 |
| NFR-002 | Mantenibilidad | Backend modular (`FastAPI`), type hints (`mypy`), lint (`ruff`), migraciones versionadas (`Alembic`), README de ejecución (`ADR-0002`) | P0 |
| NFR-003 | Rendimiento de índice vectorial embebido | Benchmark p95 documentado sobre índice vectorial embebido y dataset sintético definido (`ADR-0003`, `[E-01]`) | P1 |
| NFR-004 | Disponibilidad observable | Endpoints `/health`, `/ready`, `/version`, logs JSON estructurados con `request-id` (`[P-05]`) | P0 |
| NFR-005 | Seguridad | Autorización en servidor, gestión segura de secretos, rate limiting y batería de tests IDOR/cross-tenant (`[B-09]`, `[E-05]`) | P0 |
| NFR-006 | Privacidad | Minimización, seudonimización por allowlist, consentimiento granular y datos de prueba 100 % sintéticos (`D-09`) | P0 |
| NFR-007 | Equidad y gobernanza IA | Auditoría de sesgos contrafactual (`[E-04]`), registro de sistema IA, GDPR/EU AI Act, matriz ética y model card (`[R-01]`) | P0 |
| NFR-008 | Supervisión humana | Resultados informativos, overrides y revisión humana registrables; prohibida cualquier decisión laboral autónoma | P0 |
| NFR-009 | Reproducibilidad | Seed idempotente (`[S-05]`), versiones de taxonomía/reglas/prompts documentadas y evaluación repetible | P1 |
| NFR-010 | CI/CD | CI en GitHub Actions (`ruff`, `mypy`, `pytest`, `vitest`, `build`, `pip-audit`/`npm audit`, `gitleaks`) y despliegue protegido (`[P-04]`, `[P-06]`, `[P-07]`) | P0 |
| NFR-011 | Accesibilidad/usabilidad | Flujos principales probados en móvil/desktop y navegación por teclado básica (`[E-07]`) | P1 |


## Taxonomía de skills — D-03

- El producto utiliza un catálogo local curado y versionado de aproximadamente 80 skills, con ESCO como referencia externa cuando existe una correspondencia aplicable.
- Cada entrada del catálogo contiene identificador canónico, nombre, alias, categoría y descripción operacional. La referencia ESCO es opcional y no sustituye la identificación local.
- La normalización debe resolver los alias a un único identificador canónico, mantener Java y JavaScript como skills independientes y conservar el término original observado.

>> **Verificación de S-01:** catálogo de 80 skills cargable desde el paquete, identificadores únicos, ausencia de colisiones entre alias de distintas skills y pruebas que demuestren que Java y JavaScript se resuelven por separado.


## Entregables de evaluación

- Código modular con pruebas unitarias/integración, tipado y documentación.
- Pipeline MLOps reproducible con CI y Docker.(`compose.yaml`, `Dockerfile`).
- Informe de gobernanza, privacidad, auditoría de sesgo y riesgos.(`[R-01]`, `[E-04]`, `[E-05]`)
- Evaluación del matching/ranking (`Gold set` + métricas) y model card si se desarrolla un modelo ML entrenado.(`[E-02]`, `[R-01]`).
- Demo funcional y guion con datos sintéticos.(`[R-05]`, `[R-10]`).
- Informe de auditoría legacy y decisión de reconstrucción.(`[R-02]`).

## Notas de interpretación

- “Porcentaje de afinidad” no debe presentarse como probabilidad de contratación. Definir escala/normalización, calibración y limitaciones.
- “Modelo de ranking entrenado” no es demostrable sin datos etiquetados, metodología, baseline y evaluación. Si no existe, entregar baseline explicable y registrar qué datos faltan.
- El umbral de 300 ms debe aclarar qué se mide: retrieval vectorial no incluye extracción PDF, generación de embeddings ni tiempo de respuesta LLM.


