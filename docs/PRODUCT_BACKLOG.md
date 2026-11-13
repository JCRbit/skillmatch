# Backlog de producto — MVP SkillMatch

Estado: snapshot de referencia | Última revisión: 13/11/2026 | Fuente: Propuesta Integral Bilateral MVP v5.0 §12 "Backlog priorizado" (10 nov. 2026; documento rector disponible en el canal del equipo)

Este documento es el **snapshot del backlog de la v5.0**: qué historias existen, con qué prioridad y con qué criterio de aceptación. **No es el tracker.** El trabajo vivo se gestiona en GitHub Issues + Projects (v5.0 §15: "GitHub Projects, Issues y Pull Requests deben ser la fuente visible del trabajo"). Este archivo se actualiza cuando la v5.0 cambie o cuando el PO reordene prioridades; no se usa para trackear el día a día.

## Definition of Ready (v5.0 §15.3)

Una historia entra en el tablero ("Esta semana") sólo si cumple las cuatro:

- **Usuario y necesidad claros:** la historia explica quién la usa y qué necesita.
- **Criterio de aceptación verificable:** se puede comprobar con una prueba, no con una opinión.
- **Dependencias conocidas:** se conocen las dependencias, la fuente de datos y el riesgo principal.
- **Tamaño acotado:** cabe en una tarea pequeña, idealmente 1–2 días.

## Resumen de prioridades (MoSCoW)

| Prioridad | Historias | Nº |
|---|---|---|
| `MUST` | `US-01`…`US-09`, `US-14`…`US-17` | 13 |
| `SHOULD` | `US-10`, `US-18` | 2 |
| `COULD` | `US-11` | 1 |
| `FUTURO` | `US-12`, `US-13` | 2 |
| | **Total** | **18** |

> Regla de la v5.0 §15.5: *una idea nueva entra en Backlog; para entrar en el MVP debe desplazar otra tarea de prioridad equivalente.* Ninguna `COULD`/`FUTURO` puede entrar en la entrega sin desplazar una `MUST`/`SHOULD` y sin que el PO lo registre.

## Backlog priorizado

| ID | Historia de usuario | Prioridad | Owner sugerido | Criterio de aceptación resumido |
|---|---|---|---|---|
| `US-01` | Como junior, quiero crear mi perfil con intereses y skills declaradas. | `MUST` | Isabela | Persistencia básica y separación de campos de identidad/talento. |
| `US-02` | Como junior, quiero aportar un proyecto o repositorio seleccionado. | `MUST` | Juan | Fuente y fecha; entrada manual de respaldo; no se ejecuta código. |
| `US-03` | Como junior, quiero revisar las evidencias detectadas. | `MUST` | Juan (con Isabela) | Cada señal se puede confirmar, corregir o retirar. |
| `US-04` | Como junior, quiero comparar perfiles profesionales. | `MUST` | Isabela | Muestra 3 role cards y evidencia/brechas; sin etiqueta vocacional. |
| `US-05` | Como junior, quiero un plan de 3 siguientes pasos. | `MUST` | Isabela | Cada acción se vincula a una brecha y explica qué evidencia generaría. |
| `US-06` | Como empresa, quiero introducir una vacante. | `MUST` | Luis (con Vanessa) | Esenciales, deseables, seniority y condiciones objetivas separados. |
| `US-07` | Como empresa, quiero revisar el encaje. | `MUST` | Isabela (con Luis) | Estados por requisito, fuentes, sin rechazo automático. |
| `US-08` | Como junior, quiero controlar mi visibilidad, mis evidencias y qué datos comparto. | `MUST` | Luis | Consentimiento granular, retirada y control de visibilidad; sin perfil compartido por defecto. |
| `US-09` | Como empresa, quiero expresar interés por un perfil seudonimizado. | `MUST` | Luis (con Isabela) | El interés queda registrado sin revelar contacto ni identidad. El servidor comprueba si existe interés previo del junior en esa oportunidad. |
| `US-10` | Como junior, quiero describir una experiencia transversal. | `SHOULD` | Isabela (con Vanessa) | Dos preguntas guiadas; contenido etiquetado como declaración. |
| `US-11` | Conector GitHub read-only. | `COULD` | Juan (con Luis) | Solo repositorio elegido; validación de URL, límites, timeout y fallback. |
| `US-12` | Como centro formativo, quiero ver brechas agregadas de competencias de una cohorte. | `FUTURO` | Juan (con validación legal) | Solo con base de tratamiento validada, tamaño mínimo de grupo y sin acceso por defecto a perfiles individuales. |
| `US-13` | Como empresa, quiero publicar un programa de prácticas o beca formativa. | `FUTURO` | Vanessa (con asesoría/entidad formativa) | La oportunidad incluye naturaleza, objetivos, tareas, duración, tutoría, condiciones y marco aplicable. |
| `US-14` | Como junior, quiero descubrir empresas y oportunidades compatibles. | `MUST` | Isabela (con Luis) | Solo aparecen oportunidades publicadas y perfiles de empresa visibles; la afinidad se explica. |
| `US-15` | Como empresa, quiero descubrir perfiles junior seudonimizados. | `MUST` | Isabela (con Luis) | Solo candidatos que han activado visibilidad para oportunidades; se ocultan contacto y URL identificativa. |
| `US-16` | Como junior, quiero expresar interés en una oportunidad. | `MUST` | Luis | La acción queda asociada a junior + oportunidad y puede retirarse antes del match. |
| `US-17` | Como junior, quiero saber cuándo hay interés mutuo y decidir sobre la liberación del contacto. | `MUST` | Luis (con Isabela) | El backend confirma doble interés; exige permiso específico para datos de contacto y registra la liberación. |
| `US-18` | Como empresa, quiero ver el estado de solicitudes y matches. | `SHOULD` | Isabela | Vista básica: pendientes, interés mutuo y conversación; no dashboard analítico. |

## Notas de ownership

- Los owners son **propuestos**, no asignados: la v5.0 §14 declara que "las asignaciones siguientes son propuesta y deben confirmarse según capacidades reales y disponibilidad".
- Responsabilidades de referencia (v5.0 §14): Vanessa (PO — prioridad, UX, criterios de aceptación, apoyo en frontend/flujo candidato) · Javi (SM/Platform — flujo, contratos de integración, CI/CD, entorno, arquitectura base) · Isabela (Skills & Matching — taxonomía, role cards, reglas de matching, explicabilidad) · Luis (Backend & Security — modelo relacional, API, control de acceso, consentimiento, identidad) · Juan (Data & Evidence — entrada de proyecto/repositorio, normalización, procedencia de evidencias, fixtures). (Fuente: Propuesta Integral Bilateral MVP v5.0 §14.)
- Reparto completo en [`RACI.md`](RACI.md) y [`TEAM_WORKING_AGREEMENT.md`](TEAM_WORKING_AGREEMENT.md).

## Dependencias y riesgos principales

| Historia | Depende de | Riesgo principal |
|---|---|---|
| `US-04`, `US-05`, `US-07`, `US-14` | `D-02` (perfiles), `D-03` (taxonomía), `D-06` (matching) | Un motor sin catálogo cerrado no puede explicar razones por requisito |
| `US-08`, `US-09`, `US-15`, `US-17` | `D-07` (interés bidireccional), `D-09` (privacidad) | Fuga de identificadores o liberación de contacto sin permiso |
| `US-02`, `US-11` | `D-04` (fuente de proyectos) | API externa que cambia o se bloquea → fallback manual obligatorio |
| `US-06` | `D-05` (fuente de vacantes) | Datos de vacante sin fuente legal clara |
| `US-10` | `D-03` (taxonomía) | Declaraciones transverse marcadas como evidencia observada |
| `US-12` | `D-11` (ecosistema partner) + base de tratamiento validada | Acceso de terceros a datos de personas sin base jurídica |
| `US-13` | `D-12` (checklist de calidad y validación legal) | Publicar prácticas/becas sin marco legal ni de calidad |

## Relación con el resto de la documentación

- **Decisiones:** [`DECISION_LOG.md`](DECISION_LOG.md) (`D-01`…`D-12`, todas `DECISION_PENDING` a 13/11/2026).
- **Definición de terminado:** [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md).
- **Puertas de calidad:** [`QUALITY_GATES.md`](QUALITY_GATES.md) · CI en [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).
- **Trazabilidad de requisitos:** [`REQUIREMENTS.md`](REQUIREMENTS.md) y [`REQUIREMENTS_TRACEABILITY.md`](REQUIREMENTS_TRACEABILITY.md) — `FR-015`, `FR-016` y `FR-020` (RAG, agentes, Apply Copilot) **no tienen historia equivalente** en este backlog: son candidatas a quedar fuera de esta iteración o a desplazar una historia `MUST`/`SHOULD` (v5.0 §15.5).
- **Metodología de trabajo:** v5.0 §15 — Kanban con objetivos semanales, tablero único (`Backlog` → `Esta semana` → `En curso` → `Revisión` → `Hecho`), tres hábitos (inicio de semana 30–45 min, seguimiento diario 10 min, cierre de semana 30–45 min). El detalle operativo vive en GitHub, no en `docs/`.
