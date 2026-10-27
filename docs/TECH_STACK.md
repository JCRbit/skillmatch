# Stack recomendado y herramientas que NO añadir por defecto

La meta es un MVP reproducible que pueda evolucionar, no acumular tecnología por moda. Las versiones exactas se fijan en lockfiles tras la auditoría y una prueba de compatibilidad. Ver decisiones ADR.

## Base recomendada

| Capa | Elección inicial | Razón / condición |
|---|---|---|
| Lenguaje backend | Python 3.12/3.13 compatible con dependencias seleccionadas | Ecosistema NLP, parsers, FastAPI. Confirmar versión en instalación limpia. |
| API | FastAPI + Pydantic 2 | API tipada, validación y OpenAPI. |
| ORM/migraciones | SQLAlchemy 2 + Alembic | Esquema revisable/versionado; no crear tablas silenciosamente en runtime. |
| DB relacional | PostgreSQL | Fuente canónica para CRUD, transacciones, auditoría, filtros, estados e integridad. |
| Vector DB | Qdrant | Motor dedicado de retrieval semántico/híbrido. Guardar solo metadatos mínimos; aplicar permisos. |
| Embeddings | Adaptador configurable; evaluar `BAAI/bge-m3` (multilingüe) contra `bge-large` requerido y/o API comercial | El idioma español y recursos hardware importan. Benchmark primero; nunca acoplar negocio a un proveedor. |
| RAG / workflow agente | LangChain para integración RAG y LangGraph para flujos con estado/human-in-the-loop si se necesitan | Usar uno o dos flujos acotados; no implementar multiagente generalista en MVP. |
| Background jobs | Redis + ARQ, cuando ingestion/PDF/embeddings sean tareas durables | Retries, estado y cola fuera de la petición web. `FastAPI BackgroundTasks` no es una cola durable. |
| Frontend | React + TypeScript + Vite | Separa frontend/API, buen soporte de tests, menos despliegue SSR que Next si no se necesita. |
| Formularios/validación | React Hook Form + Zod (opcional, validar compatibilidad) | Validación coherente y formularios de roles. |
| Testing backend | pytest + HTTPX; tests de DB con PostgreSQL de test | Tests unitarios e integración. |
| Testing frontend | Vitest + Testing Library; Playwright para E2E | Probar flujos e interacción, no solo componentes aislados. |
| Entorno Python | `uv` o herramienta única acordada + lockfile | No mezclar gestores de paquetes. La auditoría detecta lo existente antes de elegir. |
| Calidad | Ruff, mypy (gradual), pre-commit | Formato/lint/types consistentes. |
| Dev/local | Docker Compose | Reproducir servicios; compose local no es automáticamente configuración de producción. |
| CI | GitHub Actions | lint, type, test, build, dependency/security scans. No desplegar en cada PR a producción. |
| Observabilidad | logs JSON, correlation/request ID, health/readiness, métricas básicas; OpenTelemetry al crecer | Diagnosticar errores sin volcar PII; añadir plataforma de telemetría por necesidad. |
| Secrets/deps | `.env` local excluido, GitHub Actions secrets, Dependabot, gitleaks, `pip-audit`, `npm audit` | Evitar tokens en código y dependencias vulnerables. |

## Kafka, Spark y Polars

### PostgreSQL — sí, MVP

Necesario para los datos transaccionales. Usar transacciones/migraciones/constraints, backups y restore tests. PostgreSQL también tiene full-text search, por lo que podéis combinar una búsqueda textual inicial con Qdrant.

### Qdrant — sí, si se mantiene requisito vectorial

Es la base vectorial especializada elegida. Definir payload schemas e índices para los filtros usados; asegurar aislamiento por usuario/empresa y borrar vectores al suprimir la fuente. No almacenar PII que no sea necesaria para retrieval.

### Redis + ARQ — condicional pero probable

Introducir cuando haya parsing de PDF, ingestión externa y generación de embeddings en segundo plano. No hace falta para el primer prototipo de CRUD. Si se activa, incluir reintentos con límite, deduplicación, idempotencia, dead-letter/manual recovery básico y monitorización.

### Polars — opcional, según benchmark

La canalización legacy podría usar pandas y ser suficiente para unos miles/décenas de miles de ofertas. Mantén pandas inicialmente si funciona. Migra a Polars solo si el volumen/memoria o la velocidad de transformación lo justifican con una prueba comparable; no uses pandas y Polars como capas duplicadas para lo mismo.

### Kafka — no para MVP

No se justifica por un proyecto de seis semanas ni por las 1.148 ofertas referidas en la auditoría preliminar. Kafka añade broker, particiones, offsets, replay, operación y monitorización. Considerarlo si hay múltiples productores/consumidores independientes, alto volumen continuo, replay fiable de eventos o necesidades de streaming demostradas.

### Spark — no para MVP

No hay evidencia de procesamiento distribuido a escala que lo requiera. El conjunto actual descrito parece manejable con SQL y librerías single-node. Considerar Spark solo si los datos exceden claramente la capacidad y perfil de rendimiento de una canalización local o aparecen requisitos distribuidos reales.

### MLflow — solo si habrá entrenamiento/evaluación con artefactos

Útil para reproducir y versionar experimentos del ranking si hay dataset etiquetado y modelos entrenados. En ausencia de entrenamiento, comienza con experiment tracking simple y versionado de evaluación; no añadir un servidor MLflow como decoración.

### ¿Pinecone o pgvector?

No usar tres almacenes vectoriales. La recomendación inicial es Qdrant por el requisito de base vectorial y por desacoplarla del sistema transaccional. pgvector podría ser alternativa válida para una arquitectura más simple/pequeña; decidirlo mediante ADR y benchmark antes de crear dependencias a ambos.

## Evitar en el MVP

- Kubernetes/microservicios para un monolito modular pequeño.
- Spark/Kafka sin evidencia de necesidad.
- Dos frameworks de RAG en paralelo.
- Agentes autónomos con herramientas de escritura amplia.
- Auto-submit de candidaturas.
- Fine-tuning del LLM sin dataset, evaluación y necesidad probada.
- Añadir servicios SaaS con pago/PII antes de aprobar privacidad y presupuesto.

## Decisiones previas a producción

Fijar versiones soportadas, images por digest/tag estable, inventario SBOM, escaneo CVE, TLS, política de backup/restauración, límites de costes/tasas, rate limiting, gestión de archivos y claves, entorno de staging, migraciones hacia delante/atrás, alertas, retención y runbook de incidentes. Esta fundación no declara que el sistema ya esté listo para producción.
