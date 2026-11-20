# ADR-0003 — PostgreSQL canónico y Qdrant derivado

- Estado: **Aprobado por PO (Vanessa) — 2026-11-20** (alineado con `D-06` y `[E-01]`)

PostgreSQL conserva entidades de negocio, relaciones, permisos, consentimiento, estados de matching y audit log. El índice vectorial derivado contiene embeddings y metadatos mínimos necesarios para recuperar candidatos/ofertas. No se toma ninguna decisión de autorización confiando en el índice vectorial: tras retrieval, revalidar acceso y estado contra datos canónicos.

Crear un proceso idempotente de indexación, seguimiento de versión de fuente/modelo, reindexado por lote, reparación de fallos y eliminación coordinada. No duplicar el perfil completo ni datos personales en el payload vectorial.

Alternativas consideradas: pgvector como diseño más simple si escala reducida; Qdrant o Pinecone si se aprueba servicio administrado post-MVP. La elección final debe reflejar capacidad operativa, licencia/hosting, requisitos del programa y benchmark.

> **Nota de alcance MVP (2026-11-20):** Para el MVP se aprueba el uso de un adaptador de embeddings ligero con índice vectorial embebido (`[E-01]`) como señal auxiliar normalizada en lugar de desplegar un servicio Qdrant separado, manteniendo PostgreSQL como única fuente de verdad canónica y sin almacenar PII en los metadatos del índice.
