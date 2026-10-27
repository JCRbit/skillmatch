# Observabilidad, operaciones y recuperación

## Desde el MVP

- Logs JSON con timestamp, nivel, service, request/correlation ID, evento y error category.
- Nunca incluir secrets, CV completo, prompts con datos personales ni payloads de formulario.
- Endpoints de health/readiness separados, con readiness que comprueba dependencias críticas sin revelar detalles internos.
- Métricas: request count/latency/errors, queue depth/age/retries, ingestions success/fail, vector index lag, deletion job status, LLM calls/tokens/cost bucket (si aplica).
- Dashboards y alertas solo cuando se despliegue a un ambiente persistente.

## Fallos operativos

- Fallo de Qdrant: el core CRUD debe seguir disponible si es seguro; matching se degrada con un error explícito.
- Fallo de LLM: mostrar fallback o error, no inventar la respuesta.
- Worker retry: idempotencia con clave de trabajo; no duplicar intereses/matches.
- Error al borrar usuario: bloquear afirmación de borrado completado hasta reconciliar PostgreSQL, archivos, Qdrant, caché, exports y políticas de backup.
- Fuente externa caída/ToS cambia: deshabilitar con source flag y mantener último estado/fecha, sin scraping agresivo.

## Antes de despliegue real

- Backup automático y restore test.
- Migraciones revisadas, ventana de ejecución y rollback plan.
- Secret rotation y plan de incidente.
- Monitor de CVE y versiones soportadas.
- Límites de coste, requests y tamaño de archivos.
- Runbook con responsable humano on-call (aunque sea horario limitado para una demo).
