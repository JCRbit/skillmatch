# Análisis de brechas — SkillMatch fase 0.1
Estado: `DECISION_REQUIRED` para Brecha A (scope) y Brecha B (data dependency); `COVERED` para Brecha C (documental) con tareas pendientes.
Fecha: 27/10/2026
Auditor: Agente

---

## Brecha A — Entrevista inicial con IA y feedback personalizado (LangGraph)

**Requisito oficial:** Sistema multiagente mediante LangGraph para entrevista inicial y feedback personalizado.
**Estado:** `DECISION_REQUIRED`

### Hallazgos
- `ARCHITECTURE.md` menciona `agent_assist`: sugerencias editables de perfil, carta y preparación de entrevista.
- `REQUIREMENTS.md` FR-015 (asistente preparación entrevista) y FR-016 (sugerencias perfil/carta) existen como P1.
- **Falta:** flujo específico de entrevista inicial que contemple: contexto autorizado → preparación preguntas → recogida respuestas → feedback personalizado (fortalezas/mejoras/recomendaciones) → distinción hechos/sugerencias → revisión humana → registro versión/fuentes → casos error/manipulación → restricción de no-decisiones-laborales-automáticas.

### Impacto
Si se omite o se reduce a chatbot RAG, no se cumple el requisito de entrevista inicial con feedback personalizado ni se documenta la supervisión humana adecuada.

### Recomendación
- **No eliminar ni convertir a opcional.** Marcar como P1 con riesgo de planificación.
- Crear `docs/INTERVIEW_AGENT_FLOW.md` con el flujo mínimo de LangGraph (nodos: get_context, prepare_questions, collect_answers, generate_feedback, human_review, save_result, error_handling).
- Actualizar `REQUIREMENTS.md` para incluir `FR-021` o extender `FR-015` con criterios de flujo LangGraph (ver matriz de trazabilidad).
- Justificar agentes/nodos adicionales si se proponen; no usar orquestación completa sin flujo verificable.
- Si el alcance temporal lo impide, elevar a Vanessa con propuesta de reducción del flujo (por ejemplo: preparación de preguntas + feedback básico en MVP, flujo completo en iteración posterior).

---

## Brecha B — Modelo de ranking entrenado

**Requisito oficial:** Motor de matching con embeddings semánticos y modelo de ranking entrenado; % afinidad y motivos explicables.
**Estado:** `DECISION_REQUIRED` (falta datos etiquetados y baseline explícito)

### Hallazgos
- `REQUIREMENTS.md` FR-010 requiere correctamente que solo se llame "entrenado" si hay entrenamiento verificable; `ARCHITECTURE.md` menciona "ranking aprobado" y línea base.
- `MATCHING_EVALUATION.md` debe actualizarse con metodología de evaluación.
- `ROADMAP_6_WEEKS.md` indica "ranking supervisado solo si hay dataset etiquetado válido" (condicionado, no obligatorio para MVP).

### Impacto
Si se presenta similitud coseno como "ranking entrenado" sin datos ni evaluación, se incumple el requisito y se genera riesgo de explicabilidad falsa.

### Recomendación
- Distinción explicita de capas (recuperación semántica / ranking / explicaciones / evaluación) documentada.
- Definir baseline explicable (por ejemplo: reglas deterministas sobre skills + experiencia demostrable) como referencia en MVP.
- Proponer dataset sintético para probar pipeline; no fingir que sustituye datos reales.
- Registrar en ADR que el ranking entrenado requiere datos etiquetados; si no existen, el MVP usa baseline con evaluación reproducible y el ranking supervisado queda como objetivo condicionado de semana 3+.
- Actualizar `REQUIREMENTS.md` y `MATCHING_EVALUATION.md` con criterios de evaluación, métricas y limitaciones.

---

## Brecha C — Pipeline MLOps, Docker Hub y despliegue funcional

**Requisito oficial:** Contenerización completa, CI con GitHub Actions, publicación en Docker Hub, aplicación desplegada y funcional.
**Estado:** `COVERED` documentalmente; `NOT_IMPLEMENTED` funcionalmente; tareas de implementación en backlog.

### Hallazgos
- `ARCHITECTURE.md` propone Docker Compose local; `REQUIREMENTS.md` NFR-010 requiere CI/build/test; `ROADMAP_6_WEEKS.md` requiere Docker comprobado y demo funcional.
- **Falta:** documento `docs/DEPLOYMENT.md` que diferencie claramente los 3 niveles (entorno local / CI / publicación y despliegue funcional) con criterios de etiquetado, rollback, health checks, registro de versión desplegada.
- No hay archivo `.github/workflows/` creado aún.

### Impacto
Si no se documenta claramente, puede confundirse "imagen construida" con "aplicación desplegada y funcional".

### Recomendación
- Crear `docs/DEPLOYMENT.md` con los 3 niveles y criterios de verificación para cada uno.
- Actualizar `REQUIREMENTS.md` NFR-010 para incluir criterios de despliegue funcional (versión accesible, no solo imagen construida).
- Asegurar que semana 6 de roadmap incluye verificación de despliegue funcional (no solo build).
- No publicar imagen ni desplegar sin autorización expresa y sin verificar ausencia de secretos o datos privados.

---

## Métrica de negocio — Reducción 60 % del cribado inicial

**Estado:** `NOT_VERIFIED` (hipótesis pendiente de medición)

- `PROJECT_CHARTER.md` define correctamente como objetivo medible (no resultado garantizado) con fórmula explícita.
- `REQUIREMENTS.md` incluye nota de interpretación correcta.
- **Falta:** metodología con datos sintéticos, medición de referencia, comparativa, registro porcentual y limitaciones.
- **Acción:** incluir estudio de referencia en backlog (P1); no declarar objetivo cumplido sin evidencia.

---

## Resumen de decisiones pendientes

| Brecha | Estado | Responsable | Acción inmediata |
|---|---|---|---|
| A — Entrevista/feedback LangGraph | DECISION_REQUIRED | Vanessa (PO) / Isabela (IA) | Decidir scope: flujo completo en MVP o básico + completo posterior; crear documento de flujo; actualizar requisitos |
| B — Ranking entrenado | DECISION_REQUIRED | Vanessa (PO) / Isabela (IA) | Decidir: baseline explicable en MVP + ranking supervisado condicionado; crear documento de evaluación; actualizar requisitos y ADR |
| C — Docker/CI/Deploy | COVERED doc / NOT_IMPLEMENTED func | Javi (SM) / Luis (backend) | Crear docs/DEPLOYMENT.md; actualizar requisitos NFR-010; asegurar semana 6 incluye verificación funcional |
| Métrica 60% | NOT_VERIFIED | Vanessa (PO) | Incluir estudio de referencia en backlog; medir con datos sintéticos; documentar limitaciones |

---

## Estado de legacy
- `TinderJob_Fork`: intacto. No se modificó ningún archivo del repositorio legacy durante fase 0 ni 0.1.
- `skillmatch`: nuevo repositorio independiente con documentación fundacional, auditoría completa y análisis de brechas.
