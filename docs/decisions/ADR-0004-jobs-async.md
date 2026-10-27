# ADR-0004 — Trabajos asíncronos

- Estado: Propuesto

Comenzar el CRUD síncrono sin cola. Cuando el parsing de CV, importación de fuente, lectura de GitHub o cálculo de embeddings requiera más que una petición corta, usar Redis + ARQ con `job_id`, estado, reintentos limitados e idempotencia.

Kafka no se justifica en el MVP: no hay evidencia de volumen/eventos multi-consumidor que requiera un broker distribuido. Spark tampoco: el conjunto de datos preliminar descrito es pequeño para procesamiento distribuido. Reabrir esta decisión solo con medición que pruebe el problema.
