# Entregable 8 — Diagnóstico de arquitectura objetivo y ADRs propuestos

Estado: Completo
Fecha: 27/10/2026

## Comparación: Legacy observado vs. Objetivo SkillMatch

| Aspecto | Legacy observado | Objetivo SkillMatch |
|---|---|---|
| Frontend | Streamlit (monolito) | React + TypeScript |
| Backend | No hay API REST | FastAPI + SQLAlchemy |
| Persistencia | CSV en disco | PostgreSQL (principal) + Qdrant (vectores) |
| Embeddings / Matching | No existe | BGE-Large / OpenAI; ranking explicable |
| RAG / Asistente | No existe | LangChain / LlamaIndex; fuentes autorizadas |
| Multi-agente | No existe | LangGraph (solo cuando sea necesario) |
| Roles | No existe | Candidata + Empresa + Admin (CRUD con permisos) |
| Blind hiring | No existe | Separación de datos identificativos; revisión humana |
| Datos | Scraping CSV + análisis | Datos sintéticos para pruebas; scraping ético con autorización |
| CI/CD | No existe | GitHub Actions + Docker |
| Observabilidad | No existe | Logs estructurados + trazabilidad |
| Evaluación / Auditoría | Notebooks descriptivos | Evaluación reproducible, auditoría de sesgos, gobernanza |
| Privacidad | No existe | GDPR: consentimiento, minimización, supresión; datos sintéticos en pruebas |

## ADRs propuestos (referencia a docs/decisions/)

- ADR-0001 (repo-boundary): Separación de legacy y producto nuevo. Estado: Aprobado por proceso.
- ADR-0002 (stack-inicial): FastAPI + React + PostgreSQL + Qdrant + Docker + GitHub Actions. Estado: Propuesto; pendiente de validación con evidencia de rendimiento y compatibilidad.
- ADR-0003 (source-of-truth-vectors): Qdrant almacena vectores derivados; PostgreSQL es fuente de verdad para datos transaccionales. Estado: Propuesto.
- ADR-0004 (jobs-async): Worker + Redis cuando se requiera procesamiento asíncrono (CV, embeddings, scraping). Estado: Propuesto; evaluar si es necesario para MVP.
- ADR-0005 (matching-explicabilidad): El score no es probabilidad calibrada; es indicador de compatibilidad con evidencia vinculada. Estado: Propuesto; requiere validación con datos sintéticos.
- ADR-0006 (agent-harness): No implementar agentes complejos hasta tener flujo verificado y requisitos cubiertos. Estado: Propuesto; no usar LangGraph en MVP sin evidencia de necesidad.

## Recomendación de arquitectura

- Monolito modular (FastAPI con módulos separados: auth, profiles, offers, matching, rag, dashboard) en lugar de microservicios, salvo evidencia concreta.
- PostgreSQL para datos transaccionales; Qdrant para vectores; no duplicar datos transaccionales en Qdrant.
- Redis como cache / cola solo si se demuestra necesidad de procesamiento asíncrono; no incluir por defecto.
- No incluir Kafka ni Spark en MVP; evaluar solo si la escala lo requiere con evidencia.
- Usar Polars solo si se demuestra mejora de rendimiento sobre Pandas en el pipeline existente.
- La extensión Apply Copilot debe ser un módulo independiente, no parte del core del producto, y debe tener restricciones claras (no envía automáticamente, no maneja credenciales).

## Riesgos técnicos
- El matching semántico requiere datos etiquetados y un dataset de evaluación; no existe en legacy.
- El legacy no tiene API ni base de datos; todo debe reconstruirse.
- No hay evidencia de rendimiento del motor de embeddings en el contexto de esta aplicación; debe medirse con benchmarks.
