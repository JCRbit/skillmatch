# Roadmap de 6 semanas (2 nov.–11 dic. 2026)

> Plan base con corte de alcance. Apply Copilot y ranking supervisado son stretch, no deben bloquear la demo principal.

## Semana 0 / antes del 2 de noviembre (preparación si hay tiempo)

- Crear repo nuevo; instalar foundation pack.
- Confirmar accesos de solo lectura al legacy y al GitHub.
- Nombrar un issue por cada artefacto de auditoría.

## Semana 1 — 2–8 noviembre: auditoría y arquitectura

- Inventory SHA/branch/status y archivo de backup.
- Leer entrypoints, deps, licencias/datos, tests, notebooks, scraper y dashboard.
- Crear mapas de datos, hallazgos de seguridad, reuse register y unknowns.
- Vanessa acepta/rechaza alcance de reutilización; aprobar ADR 0001/0002.

**Salida:** GO/GO WITH CONDITIONS; backlog priorizado con no-go items visibles.

## Semana 2 — 9–15 noviembre: base de plataforma

- Repo limpio con CI, entorno local y configuración mínima.
- Esquema inicial de auth, roles, empresas, perfiles y ofertas.
- API docs, migraciones, tests de autorización.
- Frontend con los flujos principales vacíos pero navegables.

**Salida:** CRUD protegido y reproducible.

## Semana 3 — 16–22 noviembre: datos y matching baseline

- Importación controlada de las ofertas aprobadas.
- Parsing de CV de prueba y GitHub API con fixtures/rate limits.
- Embeddings y retrieval; primera línea base de ranking con explicaciones calculadas.
- Dataset sintético y evaluación retrieval/ranking.

**Salida:** demo de match con evidencia/factores y límites claros.

## Semana 4 — 23–29 noviembre: bidireccionalidad, blind hiring, dashboard

- Interés idempotente y match mutuo con tests negativos.
- Proyección ciega por allowlist y pruebas de no filtración.
- Dashboard inicial y logging/audit events.
- Inicio del documento de gobernanza/riesgos.

**Salida:** flujo candidate–company completo sin IA generativa obligatoria.

## Semana 5 — 30 noviembre–6 diciembre: RAG y asistentes

- RAG acotado a información de oferta/empresa autorizada; citas y refusals.
- Borrador de carta y preparación de entrevista, siempre editable.
- Redis + worker si hace falta para parsing/embeddings.
- Apply Copilot solo si milestones P0/P1 ya están estables: demo de formulario controlado y sin auto-submit.

**Salida:** asistente útil con evaluación adversarial mínima.

## Semana 6 — 7–11 diciembre: integración y defensa

- Regression tests, seguridad, privacidad y evaluación de sesgo.
- CI y Docker comprobados desde máquina limpia; seed sintético reproducible.
- Informe final de legacy/reutilización, arquitectura/ADRs, model card si aplica y runbook.
- Ensayo de demo/tribunal y límites conocidos.

**Salida:** demo reproducible que no depende de datos secretos ni de un proveedor que solo funciona en la máquina de una persona.

## Gating

Si al final de Semana 3 falla CRUD/auth o no hay datos aprobados, posponer Apply Copilot y agentes avanzados. No compensar retrasos introduciendo frameworks de streaming/distribución.
