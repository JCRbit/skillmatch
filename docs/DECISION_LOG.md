# Registro de decisiones de producto y proceso — SkillMatch

Estado: `DECISION_PENDING` en las 12 decisiones registradas | Última revisión: 13/11/2026 | Branch: `master` | Último commit: `6d03022`

Este log es la fuente de verdad de las **decisiones de producto y proceso** (qué hacemos, con qué alcance, quién decide y en qué condiciones). Las **decisiones de arquitectura y tecnología** viven en los ADR de [`decisions/`](decisions/); las **tareas** viven en el tracker (GitHub Issues/Projects), no aquí.

## Fuente de las decisiones

**Propuesta Integral Bilateral MVP v5.0** — versión 5.0, 10 de noviembre de 2026, 31 páginas. Las decisiones están en su §19 "Decisiones pendientes y registro".

- **Fuente:** Propuesta Integral Bilateral MVP v5.0 — documento rector de alcance y ejecución, disponible en el canal del equipo (no versionado en este repositorio por ser un PDF con datos de terceros).
- Formato de log recomendado por la v5.0 §19: *"ID, decisión, alternativas, razonamiento, responsable, fecha, impacto y estado (propuesta/aprobada/descartada)"*. Este log añade además **opciones**, **evidencia** y **trazabilidad** a la documentación interna del repo.
- Equivalencia de estados: `DECISION_PENDING` ≡ *propuesta* · `DECISION_APPROVED` ≡ *aprobada* · `SUPERSEDED` ≡ *descartada o superada*.

## Cómo mantenerlo

- Sólo el PO (Vanessa) o el SM (Javi) cambian el **estado** de una decisión. Un agente puede proponer texto, registrar evidencia y dejar la decisión en `DECISION_PENDING`, pero **nunca** marcar `DECISION_APPROVED` por su cuenta.
- Al aprobar se rellenan: estado, fecha de decisión, responsable y una línea de evidencia (enlace al issue/PR o al acta de la reunión).
- Si una decisión cambia, no se edita la fila: se marca `SUPERSEDED` y se añade una decisión nueva con el ID siguiente.
- Estas 12 decisiones **sustituyen** a las 12 preguntas previas del memo de stakeholders (§3) que rigieron este log hasta el 13/11/2026.

### Vocabulario de estados

| Estado | Significado |
|---|---|
| `DECISION_PENDING` | Cuestión abierta, con responsable y fecha de revisión; el equipo no avanza en lo que depende de ella. |
| `DECISION_APPROVED` | Aprobada por los responsables indicados, con evidencia registrada. |
| `DECISION_REQUIRED` | Falta información o criterio para decidir (no es lo mismo que "pendiente de reunión"). |
| `SUPERSEDED` | Reemplazada por una decisión posterior; se conserva para trazabilidad. |

## 1. Resumen de decisiones

| ID | Decisión | Propuesta v5.0 | Responsable de validación | Estado | Fecha de revisión |
|---|---|---|---|---|---|
| `D-01` | Claim y segmento | Talento tecnológico junior / primeras oportunidades | Vanessa + Jesús | `DECISION_PENDING` | 13/11/2026 |
| `D-02` | Perfiles de demo | Backend, Frontend y QA Automation Junior | Vanessa + Isabela | `DECISION_PENDING` | 13/11/2026 |
| `D-03` | Taxonomía | ESCO como referencia; catálogo local curado para tres rutas | Isabela + Juan | `DECISION_PENDING` | 13/11/2026 |
| `D-04` | Fuente de proyectos | Un proyecto manual; repositorio GitHub seleccionado como conector opcional | Juan + Luis | `DECISION_PENDING` | 13/11/2026 |
| `D-05` | Fuente de vacantes | Formulario manual; sin scraping | Vanessa + Javi | `DECISION_PENDING` | 13/11/2026 |
| `D-06` | Matching | Matching híbrido mínimo: criterios obligatorios/objetivos + similitud semántica ligera; razones por requisito; sin porcentaje de contratación ni vector DB | Isabela + Jesús | `DECISION_PENDING` | 13/11/2026 |
| `D-07` | Interés bidireccional | Ambas partes pueden expresar interés; el servidor calcula el match y controla liberación de contacto | Vanessa + Isabela | `DECISION_PENDING` | 13/11/2026 |
| `D-08` | Selección tecnológica | Arquitectura agnóstica; elegir stack tras auditar el repo. React/FastAPI/PostgreSQL son una opción, no un mandato | Javi + Luis | `DECISION_PENDING` | 13/11/2026 |
| `D-09` | Privacidad | Identidad separada, seudonimización y control de compartición | Luis + Vanessa | `DECISION_PENDING` | 13/11/2026 |
| `D-10` | Feature freeze | 7 de diciembre; estabilización 8–9 diciembre | Vanessa + Javi | `DECISION_PENDING` | 13/11/2026 |
| `D-11` | Ecosistema partner | Añadir bootcamps/centros y programas de primeras oportunidades al roadmap; no a la entrega técnica del MVP | Vanessa + Jesús | `DECISION_PENDING` | 13/11/2026 |
| `D-12` | Publicación de prácticas/becas | Definir checklist de calidad y validación legal antes de admitir estos tipos de oportunidad | Vanessa + asesoría/entidad formativa | `DECISION_PENDING` | 13/11/2026 |

## 2. Detalle por decisión

### `D-01` — Claim y segmento

- **Propuesta v5.0 (§19):** Talento tecnológico junior / primeras oportunidades.
- **Valida:** Vanessa + Jesús.
- **Contexto (§2.3):** el usuario prioritario es el candidato junior o egresado de bootcamp; la empresa (recruiter/tech lead) es la contraparte activa. Los centros formativos son *partner futuro* y el mentor/orientador es secundario.
- **Alternativas:** la v5.0 no documenta alternativas descartadas para esta decisión; sí acota que centros y mentores no requieren cuenta ni portal en el MVP.
- **Implicación en el repo:** coherente con [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) ("plataforma bidireccional de matching de talento junior y empresas") y con sus principios 1 y 3. Requiere precisar en el charter que el segmento es *junior técnico* y que "primeras oportunidades" abre la puerta a prácticas/becas (que sólo pueden publicarse tras `D-12`).
- **Impacto si no se decide:** el claim de la demo y de la defensa queda abierto; cada historia nueva hereda un alcance no validado.
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-02` — Perfiles de demo

- **Propuesta v5.0 (§19):** Backend, Frontend y QA Automation Junior.
- **Valida:** Vanessa + Isabela.
- **Contexto (§4.2):** cada perfil lleva ejemplos de competencias técnicas y un uso en la demo (comparar proyectos orientados a lógica/servicios/datos, construcción de interfaces, y mostrar que el perfil técnico no es sólo programar producto). La v5.0 los define como *arquetipos de demostración*, no como definiciones exhaustivas del mercado, y exige contrastarlos con vacantes reales elegidas para la demo.
- **Alternativas:** la v5.0 no documenta alternativas descartadas; la decisión sustituye a la lista abierta de `US-04` ("3 role cards") como catálogo cerrado de tres rutas.
- **Implicación en el repo:** [`PRODUCT_BACKLOG.md`](PRODUCT_BACKLOG.md) hereda los tres perfiles en `US-04`; [`DATA_MODEL.md`](DATA_MODEL.md) debe versionar el conjunto de skills esenciales/deseables por ruta.
- **Impacto si no se decide:** las "role cards" quedan como 3 huecos sin contenido verificable y el catálogo de skills no se puede cerrar.
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-03` — Taxonomía

- **Propuesta v5.0 (§19):** ESCO como referencia; catálogo local curado para tres rutas.
- **Valida:** Isabela + Juan.
- **Contexto (§6.5):** cada skill tiene identificador, nombre canónico, alias, categoría, descripción operacional y, cuando aplique, relación con un concepto ESCO. Ejemplo: "Postgres" → "PostgreSQL"; Java no se fusiona con JavaScript. Los perfiles de rol son un conjunto pequeño y versionado de skills esenciales y deseables.
- **Alternativas:** la v5.0 descarta implícitamente un catálogo abierto y sin control de alias (normalización por equivalencias controladas), pero no documenta una alternativa explícita de catálogo.
- **Implicación en el repo:** coherente con [`DATA_MODEL.md`](DATA_MODEL.md) ("canonical skill taxonomy IDs plus observed raw terms and evidence"). Hay que **añadir la referencia ESCO** al modelo de datos y a [`REQUIREMENTS.md`](REQUIREMENTS.md), que hoy no la menciona.
- **Impacto si no se decide:** el matching no puede explicar razones por requisito (depende de `D-06`) y la comparabilidad entre vacante y perfil se queda en coincidencia textual.
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-04` — Fuente de proyectos

- **Propuesta v5.0 (§19):** Un proyecto manual; repositorio GitHub seleccionado como conector opcional.
- **Valida:** Juan + Luis.
- **Contexto (§5.1, §16):** el MVP usa una sola fuente/proyecto por candidato, con entrada manual como baseline; el conector de repositorio es opcional, con fixtures locales y fallback manual si la API externa falla o se bloquea.
- **Alternativas:** se descarta el scraping y la ingesta masiva; el conector GitHub pasa de "incluido" a "opcional" (coherente con `US-11` en prioridad `COULD`).
- **Implicación en el repo:** [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) incluye "GitHub API con consentimiento y rate limits" en el alcance MVP; [`REQUIREMENTS.md`](REQUIREMENTS.md) y la trazabilidad deben degradar ese bloque a *stretch* si `D-04` se aprueba.
- **Impacto si no se decide:** se construye una integración con API externa que puede bloquearse y que la v5.0 considera accesoria.
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-05` — Fuente de vacantes

- **Propuesta v5.0 (§19):** Formulario manual; sin scraping.
- **Valida:** Vanessa + Javi.
- **Contexto (§5.2):** la empresa registra una vacante por formulario (seniority, modalidad, condiciones objetivas, competencias esenciales y deseables); una empresa y una oportunidad de demo.
- **Alternativas:** se descarta el scraping de portales de empleo, que pasa a ser explícitamente no-MVP (la v5.0 además mantém "eludir captchas, términos de portales o controles de acceso" fuera de alcance).
- **Implicación en el repo:** **conflicto directo** con la hoja de ruta propuesta previa Fase 2 ("Pipeline de scraping ético … integrado a `ingestion`", `FR-005`) y con [`ROADMAP_6_WEEKS.md`](ROADMAP_6_WEEKS.md) semana 3. Ver §3.
- **Impacto si no se decide:** el equipo construye una pipeline de scraping que la propuesta v5.0 ha dejado fuera, consumiendo días del calendario de 4 semanas.
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-06` — Matching

- **Propuesta v5.0 (§19):** Matching híbrido mínimo: criterios obligatorios/objetivos + similitud semántica ligera; razones por requisito; sin porcentaje de contratación ni vector DB.
- **Valida:** Isabela + Jesús.
- **Contexto (§7.1, §7.3):** secuencia de 6 pasos (validar vacante → normalizar términos → construir estado por competencia con fecha y fuente → comprobar condiciones objetivas por separado → generar ficha de encaje → registrar versión de reglas/taxonomía y permitir revisión humana). §7.3 descarta expresamente el **porcentaje global de "calidad del candidato"** y la **probabilidad de contratación**; si se muestra una cifra debe llamarse **"cobertura de evidencia"** con numerador, denominador y estados, y no puede compensar un requisito esencial no cubierto. *Guardrail:* la ausencia de evidencia **no** genera rechazo automático ("pendiente de revisión / evidencia", no "no apto").
- **Alternativas:** se descartan el score global, el porcentaje de contratación, la base vectorial y la señal semántica como componente dominante; se admite una **señal auxiliar normalizada**, siempre explicada.
- **Implicación en el repo:** **conflicto directo** con [`ARCHITECTURE.md`](ARCHITECTURE.md) y [`decisions/ADR-0003-source-of-truth-vectors.md`](decisions/ADR-0003-source-of-truth-vectors.md) (Qdrant en el MVP), con [`MATCHING_EVALUATION.md`](MATCHING_EVALUATION.md) (capas de retrieval con embeddings) y con la métrica de latencia "búsqueda vectorial p95 <300 ms" del [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md). Ver §3.
- **Impacto si no se decide:** se mantiene una infraestructura de vectores no necesaria para la demo y se corre el riesgo de presentar una cifra que se interprete como probabilidad de contratación (prohibido por [`AGENTS.md`](../AGENTS.md)).
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-07` — Interés bidireccional

- **Propuesta v5.0 (§19):** Ambas partes pueden expresar interés; el servidor calcula el match y controla liberación de contacto.
- **Valida:** Vanessa + Isabela.
- **Contexto (§5.2, §5.3):** la empresa solicita conversación y el candidato recibe la solicitud y decide si acepta; el contacto se habilita según los permisos del piloto.
- **Alternativas:** se descarta el contacto directo o unidireccional (empresa → candidato) y la liberación automática de datos de contacto.
- **Implicación en el repo:** coherente con los principios 3 y 4 del [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) y con `FR-011`/`FR-013` de [`REQUIREMENTS.md`](REQUIREMENTS.md). Concreta la regla de [`AGENTS.md`](../AGENTS.md): "el contacto se revela sólo tras interés mutuo verificado por servidor".
- **Impacto si no se decide:** se implementa un flujo de contacto sin verificación de doble interés, que es el riesgo de privacidad más alto del producto.
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-08` — Selección tecnológica

- **Propuesta v5.0 (§19):** Arquitectura agnóstica; elegir stack tras auditar el repo. React/FastAPI/PostgreSQL son una opción, no un mandato.
- **Valida:** Javi + Luis.
- **Contexto (§1.1):** la especificación técnica v0.1 de Javi ya propone FastAPI, React, PostgreSQL, modelo de datos, consentimiento, matching y trazabilidad; la v5.0 lo trata como **punto de partida** y pide auditar antes de fijar.
- **Alternativas:** se descarta tratar el stack heredado como decisión cerrada; la elección queda abierta hasta la auditoría.
- **Implicación en el repo:** **conflicto directo** con [`ARCHITECTURE.md`](ARCHITECTURE.md) (`PROPOSED`: FastAPI + React + PostgreSQL + Qdrant) y con [`decisions/ADR-0002-stack-inicial.md`](decisions/ADR-0002-stack-inicial.md). Ver §3.
- **Impacto si no se decide:** se sigue construyendo sobre un stack no validado; el coste real de cambiar es mayor cuanto más pronto se parasite código.
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-09` — Privacidad

- **Propuesta v5.0 (§19):** Identidad separada, seudonimización y control de compartición.
- **Valida:** Luis + Vanessa.
- **Contexto (§16):** riesgo alto si un repositorio o URL permite reidentificar → ocultar enlaces y usernames en la vista inicial, revisión de PII y compartir sólo bajo permiso.
- **Alternativas:** se descarta la exposición de identidad, URL de repositorio y contacto en la vista inicial; se descarta el acceso por defecto de terceros a perfiles individuales.
- **Implicación en el repo:** coherente con los principios 4 y 6 del [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md), con [`SECURITY_PRIVACY.md`](SECURITY_PRIVACY.md) y con el límite de modo ciego de [`AGENTS.md`](../AGENTS.md). Es la base técnica de `US-08`, `US-09`, `US-15` y `US-17`.
- **Impacto si no se decide:** el diseño de datos y de API se construye sin separación entre identidad y talento, y la seudonimización se aplica como parche tardío.
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-10` — Feature freeze

- **Propuesta v5.0 (§19):** 7 de diciembre; estabilización 8–9 diciembre.
- **Valida:** Vanessa + Javi.
- **Contexto (§13):** la v5.0 planifica un ciclo de 4 semanas, con el freeze de funcionalidad al inicio de la última semana útil de desarrollo.
- **Alternativas:** se descarta seguir añadiendo funcionalidad en la semana de defensa.
- **Implicación en el repo:** **conflicto directo** con [`ROADMAP_6_WEEKS.md`](ROADMAP_6_WEEKS.md) (semana 6 = 7–11 dic.: integración, regresión, informe final, demo y defensa) y con el horizonte "2 nov.–11 dic. 2026" del [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md). Ver §3.
- **Impacto si no se decide:** la demo y la defensa sesolapan con el desarrollo; el equipo entra en la semana de cierre sin criterio para cortar.
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-11` — Ecosistema partner

- **Propuesta v5.0 (§19):** Añadir bootcamps/centros y programas de primeras oportunidades al roadmap; no a la entrega técnica del MVP.
- **Valida:** Vanessa + Jesús.
- **Contexto (§2.6, §2.3):** la relación con un centro es de validación y distribución, sin portal ni acceso individual en el MVP; una entidad formativa **no** obtiene acceso a los datos individuales de sus alumnos por defecto.
- **Alternativas:** se descarta el portal de centros y el acceso por defecto a datos individuales en el MVP.
- **Implicación en el repo:** coherente con las prioridades `FUTURO` de `US-12` y `US-13` en [`PRODUCT_BACKLOG.md`](PRODUCT_BACKLOG.md) y con [`AI_GOVERNANCE.md`](AI_GOVERNANCE.md). No altera el alcance técnico mientras siga fuera de la entrega.
- **Impacto si no se decide:** los partners seamaan a convertir el MVP en un marketplace de formación, que es el riesgo de *scope creep* nº1 de la v5.0 (§16).
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

### `D-12` — Publicación de prácticas/becas

- **Propuesta v5.0 (§19):** Definir checklist de calidad y validación legal antes de admitir estos tipos de oportunidad.
- **Valida:** Vanessa + asesoría/entidad formativa.
- **Contexto (`US-13`, §12):** la oportunidad de prácticas o beca incluye naturaleza, objetivos, tareas, duración, tutoría, condiciones y marco aplicable; es `FUTURO`.
- **Alternativas:** se descarta admitir prácticas/becas como un tipo más de vacante sin marco de validación.
- **Implicación en el repo:** coherente con "Fuera de alcance: prometer cumplimiento normativo sin evaluación legal competente" del [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md). Depende de `D-01` (si "primeras oportunidades" incluye prácticas) y habilita `US-13`.
- **Impacto si no se decide:** se publican ofertas con duración, tutoría y condiciones sin marco legal ni de calidad, que es la exposición regulatoria más alta del roadmap.
- **Estado:** `DECISION_PENDING` · revisión 13/11/2026.

## 3. Conflictos con la documentación vigente del repo

Estos conflictos aparecen al contrastar la v5.0 con los documentos internos. **No se resuelven solos**: son cambios de documento que la PO debe autorizar al aprobar la decisión correspondiente.

| Decisión | Documento en conflicto | Qué dice hoy | Acción propuesta |
|---|---|---|---|
| `D-05` | la hoja de ruta propuesta previa Fase 2 · [`ROADMAP_6_WEEKS.md`](ROADMAP_6_WEEKS.md) semana 3 · `FR-005` | "Pipeline de scraping ético integrado a `ingestion`" | Retirar el scraping del MVP (o registrarlo como excepción explícita con responsable) |
| `D-06` | [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`decisions/ADR-0003-source-of-truth-vectors.md`](decisions/ADR-0003-source-of-truth-vectors.md) · [`MATCHING_EVALUATION.md`](MATCHING_EVALUATION.md) · [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) (Qdrant en alcance MVP, métrica de "búsqueda vectorial") | Embeddings + Qdrant + retrieval vectorial como capa central | Reescribir el matching como ficha por requisito + señal auxiliar; revisar ADR-0003 y el alcance del charter |
| `D-08` | [`ARCHITECTURE.md`](ARCHITECTURE.md) (`PROPOSED`) · [`decisions/ADR-0002-stack-inicial.md`](decisions/ADR-0002-stack-inicial.md) | Stack FastAPI + React + PostgreSQL + Qdrant asumido | Marcar ADR-0002 como provisional hasta la auditoría; no añadir tecnologías nuevas mientras tanto |
| `D-10` | [`ROADMAP_6_WEEKS.md`](ROADMAP_6_WEEKS.md) (semana 6 = 7–11 dic.) · [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) (horizonte 2 nov.–11 dic.) | Integración, regresión, informe final, demo y defensa entre el 7 y el 11 | Re calendarizar: freeze 7 dic., estabilización 8–9 dic., demo/defensa 10–11 dic. |
| `D-04` | [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) (alcance MVP: "GitHub API con consentimiento y rate limits") | Integración GitHub dentro del alcance MVP | Degradar el bloque GitHub a *stretch* (`US-11` = `COULD`) |
| — | [`REQUIREMENTS.md`](REQUIREMENTS.md) (`FR-014` RAG, `FR-015`/`FR-016` agentes, `FR-020` Apply Copilot) | Requisitos P1/stretch sin historia equivalente en el backlog de la v5.0 | Aplicar la regla de la v5.0 §15.5: cada funcionalidad nueva desplaza a otra de prioridad equivalente, o se marca como fuera del alcance de esta iteración |

## 4. Trazabilidad con otras fuentes

- **Propuesta v5.0:** documento rector (disponible en el canal del equipo) — §19 (decisiones), §12 (backlog `US-01`…`US-18`), §14 (organización del equipo y RACI), §15 (metodología ligera, DoR/DoD), §16 (riesgos), §17–§18 (demo y recorrido).
- **Backlog de producto:** [`PRODUCT_BACKLOG.md`](PRODUCT_BACKLOG.md) — snapshot del backlog de la v5.0; el tracker vivo está en GitHub Issues/Projects.
- **Decisiones de arquitectura:** [`decisions/`](decisions/) (`ADR-0001`…`ADR-0006`) — no se duplican aquí, pero `D-06` y `D-08` las affects (`ADR-0002`, `ADR-0003`).
- **Análisis de brechas previo:** [`REQUIREMENTS_GAP_ANALYSIS.md`](REQUIREMENTS_GAP_ANALYSIS.md) (Brechas A/B/C) — la v5.0 **reordena** el alcance: la Brecha B (ranking entrenado) queda absorbida en `D-06` (baseline explicable, sin score global) y la Brecha C (CI/Docker/deploy) se mantiene como trabajo de plataforma.

## 5. UNKNOWNS y pruebas de resolución

| ID | Incertidumbre | Cómo se resuelve | Responsable |
|---|---|---|---|
| `U-01` | Ninguna de las 12 decisiones tiene confirmación registrada en el repositorio a 13/11/2026 (último commit `6d03022`, sin remoto). El resultado de la reunión que aprobó la v5.0 no es verificable desde el repo. | Registrar aquí estado, fecha y evidencia en el momento de la validación; el log es el asiento. | Vanessa / Javi |
| `U-02` | El estado de ejecución real desde el 28/10/2026 no es verificable desde este repositorio: no hay código, ni datos sintéticos, ni remoto. | Contrastar con el tracker (GitHub Issues/Projects) y con el repositorio remoto cuando exista. | Javi |

## 6. Registro de cambios

| Fecha | Cambio | Autor |
|---|---|---|
| 13/11/2026 | Creación del log con `D-01`…`D-12` a partir de las 12 preguntas previas del memo de stakeholders (§3); todas en `DECISION_PENDING`. | Agente (propuesta, sin aprobación) |
| 13/11/2026 | Sustituidas las 12 decisiones previas por las 12 decisiones oficiales de la **Propuesta Integral Bilateral MVP v5.0** (§19). Se añade el apartado §3 con los conflictos con la documentación vigente del repo. | Agente (propuesta, sin aprobación) |
| 13/11/2026 | Se retira la versión del PDF rector del repositorio (contiene datos de terceros; el repo es compartido) y se referencian sus decisiones y backlog como fuente externa del equipo. | Agente (propuesta, sin aprobación) |
