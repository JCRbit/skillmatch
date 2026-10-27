# Estrategia de despliegue — SkillMatch (3 niveles)
Estado: `PROPOSED`. No implementar sin autorización y verificación de ausencia de secretos.
Fecha: 27/10/2026

## Nivel 1 — Entorno local reproducible
- `docker-compose.yml` con servicios: app (FastAPI + React build servido estáticamente o vía proxy), PostgreSQL, Qdrant, Redis (opcional), worker (cuando se requiera).
- Datos sintéticos para pruebas; sin datos reales de candidatos ni empresas.
- Instrucciones en `docs/LOCAL_DEVELOPMENT.md`.
- Verificación: `docker compose up` arranca; tests pasan; datos sintéticos cargados.

## Nivel 2 — Integración y entrega continua (GitHub Actions)
- Workflow: lint / typecheck / tests / build imagen / scan dependencias / construcción de imagen con tag inmutable (`skillmatch/app:${GITHUB_SHA}`).
- No publicar imagen sin pasar todos los pasos; no usar `:latest` como tag de producción.
- Secretos configurados en GitHub (no en código): `DOCKER_HUB_USERNAME`, `DOCKER_HUB_TOKEN` (o equivalente), variables de entorno de servicio.
- Verificación: workflow pasa en rama limpia; imagen construida; no contiene datos sensibles ni CVs.

## Nivel 3 — Publicación y despliegue funcional
- Construcción de imagen identificable con tag de commit / versión; publicación en Docker Hub (o registro privado) con tag específico.
- Despliegue a entorno accesible para demo/tribunal (no producción comercial).
- Health check, gestión básica de errores, registro de versión desplegada y commit de origen.
- Migraciones de DB controladas (Alembic); no destruye datos sin respaldo.
- Rollback: usar imagen anterior conocida; no eliminar datos de DB sin plan.
- Evidencia requerida: URL accesible; demo funcional con datos sintéticos; no hay datos personales ni secretos expuestos.

## Decisiones pendientes
- Nombre definitivo de repositorio remoto y organización; namespace de Docker Hub; entorno de alojamiento para demo.
- Confirmar que la imagen no incluye datos reales ni credenciales antes de publicar.
- Confirmar con Vanessa (PO) que despliegue funcional es parte del alcance obligatorio para defensa, no solo build de imagen.

## Restricciones
- No publicar ni desplegar sin autorización expresa.
- No inventar credenciales, URLs ni namespaces.
- No incluir datos reales ni secreto en la imagen.
