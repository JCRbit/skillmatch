# Roadmap de 6 semanas (2 nov.–11 dic. 2026)

> Plan alineado con los milestones de GitHub (`M0`–`M4`) y la decisión `D-10` (Feature freeze: 7 de diciembre; Estabilización: 8–9 de diciembre; Demo y defensa: 10–11 de diciembre de 2026). Apply Copilot, scraping externo, parsing de CV PDF y Qdrant/Redis quedan fuera del MVP.

## M0 (Semanas 1–2) — 2–15 noviembre: auditoría legacy y cierre de alcance

- Crear repositorio nuevo (`JCRbit/skillmatch`) e instalar foundation pack.
- Auditoría read-only de `TinderJob_Fork` (`docs/legacy-audit/`): inventario, seguridad, calidad de datos, reuse register y unknowns.
- Aprobación de alcance MVP (`D-01`–`D-11`), alineación de documentos rectores (`[G-02]`) y cierre del contrato de arquitectura (`ADR-0001`–`ADR-0006`).

**Salida:** `GO` con alcance acotado y backlog priorizado (`MUST` / `SHOULD` / `COULD`).

## M1 (Semana 3) — 16–22 noviembre: esqueleto andante

- Base de plataforma: modelo de datos inicial y migraciones Alembic (`[B-01]`), stack local Docker Compose (`[P-03]`), CI (`[P-04]`), logs y healthchecks (`[P-05]`).
- Autenticación y autorización por roles (`Candidate`, `Company`, `Admin`) en backend (`[B-02]`) y shell/rutas protegidas en frontend (`[F-01]`).
- CRUD base de candidato (`[B-03]`, `[F-02]`), empresa y vacante mediante formulario estructurado (`[B-04]`, `[F-03]`).
- Taxonomía local curada (~80 skills con referencia ESCO) (`[S-01]`), normalizador (`[S-02]`), perfiles de rol (`[S-03]`), dataset sintético v1 (`[S-04]`) y seed idempotente (`[S-05]`).
- Narrativa v0 (`[R-03]`), README v1 (`[R-06]`) y Sprint Review A (`[V-01]`).

**Salida:** esqueleto andante end-to-end con CRUD protegido y seed reproducible.

## M2 (Semana 4) — 23–29 noviembre: demo v1 del flujo completo

- Alta manual de proyecto y revisión de evidencias (`[S-06]`, `[S-07]`, `[F-04]`).
- Motor de ficha de encaje por requisito y API de matching con cobertura de evidencia (`[M-01]`, `[M-02]`), más comparador de 3 role cards (`[F-05]`).
- Consentimiento granular (`[B-05]`), proyección seudonimizada por allowlist y tests de no-filtración (`[B-06]`).
- Interés idempotente, match mutuo y liberación de contacto verificada en servidor (`[B-07]`, `[F-06]`, `[F-07]`, `[F-08]`, `[F-09]`).
- Banco de preguntas y rúbrica de entrevista (`[A-04]`), guion de demo v1 (`[R-05]`) y Sprint Review B (`[V-02]`).

**Salida:** flujo bidireccional completo candidato ↔ empresa con privacidad y explicabilidad sin IA generativa obligatoria.

## M3 (Semana 5) — 30 noviembre–7 diciembre: evaluación de IA, RAG y feature freeze

- Índice vectorial embebido + señal semántica auxiliar explicada (`[E-01]`, `[M-03]`) y plan de 3 siguientes pasos (`[F-10]`).
- Dataset sintético v2 (`[S-08]`), Gold set (≥60 pares) con harness `Recall@k / NDCG / MRR` (`[E-02]`) y auditoría de sesgo contrafactual (`[E-04]`).
- RAG acotado sobre ofertas/empresa autorizadas con citas y refusals (`[A-01]`, `[A-02]`), flujo de entrevista en LangGraph con revisión humana (`[A-03]`, `[A-05]`) y pruebas adversariales (`[A-06]`).
- Rate limiting, batería IDOR/cross-tenant e informe de seguridad (`[B-09]`, `[E-05]`), prueba E2E Playwright (`[Q-01]`) y documento de gobernanza GDPR / EU AI Act (`[R-01]`).
- **Hito de corte (`D-10`):** **7 de diciembre — Feature freeze** (no entran nuevas funcionalidades tras esta fecha).

**Salida:** funcionalidades MVP congeladas con evaluación adversarial, métricas de retrieval y gobernanza documentada.

## M4 (Semana 6) — 8–11 diciembre: estabilización, release candidate y defensa

- **8–9 de diciembre (Estabilización):** corrección de bugs previos al freeze (`[Q-03]`), estabilización de datos de demo (`[Q-04]`), despliegue accesible por URL con rollback (`[P-07]`), prueba en máquina limpia y runbook (`[P-08]`), informe final de reutilización (`[R-02]`) y cierre de documentación (`[R-07]`–`[R-14]`).
- **10–11 de diciembre (Ensayos y defensa):** ensayos cronometrados con plan B sin LLM (`[R-09]`, `[R-10]`), checklist go/no-go y defensa final ante tribunal.

**Salida:** demo reproducible con datos 100 % sintéticos y plan de contingencia sin dependencias frágiles.

## Gating

Si al cierre de `M2` (29 nov.) falla algún flujo P0 de CRUD, seudonimización o match mutuo, se recortan automáticamente las tareas `SHOULD` y `COULD` (`[S-09]`, `[S-10]`, `[E-03]`, `[A-07]`) para proteger la estabilidad del feature freeze del 7 de diciembre. No compensar retrasos introduciendo infraestructura distribuida ni servicios externos adicionales.