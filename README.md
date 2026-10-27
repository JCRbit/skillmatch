# SkillMatch — fundación del producto (codename provisional)

Paquete documental para reconstruir una plataforma de matching profesional bidireccional para perfiles junior. El repositorio nuevo debe permanecer separado de `TinderJob_Fork`, que se conserva como fuente legacy auditable.

## Fuente de verdad

1. `AGENTS.md`: reglas para cualquier agente que trabaje en el repo.
2. `docs/PROJECT_CHARTER.md`: producto, alcance y actores.
3. `docs/REQUIREMENTS.md`: requisitos identificados y criterios de aceptación.
4. `docs/ARCHITECTURE.md`: arquitectura objetivo y límites.
5. `docs/decisions/`: ADRs; las decisiones aprobadas no se cambian en silencio.
6. `docs/legacy-audit/`: evidencia del análisis del fork antiguo.
7. `docs/TEAM_WORKING_AGREEMENT.md`: equipo, PO/SM y colaboración.

## Estado

**Fase 0 — Auditoría legacy, aún no autorizada la reconstrucción.** No afirmamos que la arquitectura objetivo o la calidad de legacy estén verificadas. Todo lo que no tenga evidencia se registra como `UNKNOWN`.

## Entorno objetivo propuesto

- Backend/API: Python + FastAPI, SQLAlchemy, Alembic, Pydantic.
- Frontend web: React + TypeScript.
- Persistencia transaccional: PostgreSQL.
- Vector search: Qdrant (índice derivado, reconstruible desde fuentes canónicas).
- Tareas largas: Redis + ARQ cuando se habilite ingesta/parsing/embeddings en segundo plano.
- CI: GitHub Actions; Docker Compose solo para desarrollo e integración local.

Kafka y Spark no forman parte del MVP por defecto. Ver `docs/TECH_STACK.md` y ADRs.

## Inicio

Lee primero `START_HERE.md`; no despliegues ni ejecutes nada contra sistemas reales desde este paquete.
