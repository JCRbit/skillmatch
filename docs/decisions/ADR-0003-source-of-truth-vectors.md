# ADR-0003 — PostgreSQL canónico y Qdrant derivado

- Estado: Propuesto

PostgreSQL conserva entidades de negocio, relaciones, permisos, consentimiento, estados de matching y audit log. Qdrant contiene embeddings y metadatos mínimos necesarios para recuperar candidatos/ofertas. No se toma ninguna decisión de autorización confiando en Qdrant: tras retrieval, revalidar acceso y estado contra datos canónicos.

Crear un proceso idempotente de indexación, seguimiento de versión de fuente/modelo, reindexado por lote, reparación de fallos y eliminación coordinada. No duplicar el perfil completo ni datos personales en el payload vectorial.

Alternativas consideradas: pgvector como diseño más simple si escala reducida; Pinecone si se aprueba servicio administrado. La elección final debe reflejar capacidad operativa, licencia/hosting, requisitos del programa y benchmark.
