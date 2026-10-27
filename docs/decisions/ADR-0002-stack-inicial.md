# ADR-0002 — Stack inicial de aplicación

- Estado: **Propuesto, sujeto a auditoría y spike técnico**
- Fecha: 2026-10-27
- Owner: Luis (propuesta de backend/DB), Vanessa PO aprueba alcance

## Decisión propuesta

Monolito modular con FastAPI + Pydantic, SQLAlchemy/Alembic, PostgreSQL, React + TypeScript, Qdrant para vectores, Docker Compose local y GitHub Actions CI. Tareas largas pasan a Redis + ARQ al introducir ingestión/parsing/embeddings que deban sobrevivir al ciclo de una petición.

## Por qué

Cumple los requisitos técnicos, reduce variedad de herramientas y permite API REST documentada. Mantiene una sola fuente de verdad transaccional y un servicio vectorial especializado.

## No incluir por defecto

Kafka, Spark, Kubernetes, microservicios ni un segundo vector store. Polars solo tras medir; MLflow cuando existan experimentos de ranking reproducibles.

## Consecuencias y riesgos

- Qdrant requiere sincronización/deletion con PostgreSQL; definir reconciliación/rebuild.
- Redis/ARQ añade operación; activarlo cuando se necesite trabajo durable.
- El vector retrieval <300 ms se debe medir bajo una carga y hardware definidos.
- La selección de proveedor/modelo de embeddings queda tras benchmark en español e inglés.
