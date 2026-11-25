# Estrategia de despliegue — SkillMatch (3 niveles)
Estado: `PROPOSED` (Nivel 1 y Nivel 3 pendientes de `[P-07]`); Nivel 2 implementado en `[P-06]`. No publicar sin autorización y verificación de ausencia de secretos.
Fecha: 27/10/2026

## Nivel 1 — Entorno local reproducible
- `docker-compose.yml` con servicios: app (FastAPI + React build servido estáticamente o vía proxy), PostgreSQL, Qdrant, Redis (opcional), worker (cuando se requiera).
- Datos sintéticos para pruebas; sin datos reales de candidatos ni empresas.
- Instrucciones en `docs/LOCAL_DEVELOPMENT.md`.
- Verificación: `docker compose up` arranca; tests pasan; datos sintéticos cargados.

## Nivel 2 — Integración y entrega continua (GitHub Actions)
- Workflow `ci.yml`: lint / typecheck / tests / scan de dependencias / validación de compose y **build + smoke test de la imagen de producción** en cada PR (job `Infra`). Detalle en [`CI.md`](CI.md).
- Workflow `publish-image.yml` (`[P-06]`, issue #58): publica la imagen en Docker Hub. Solo se lanza a mano (`workflow_dispatch`), solo desde `main`, solo si `CI · gate` está en verde para ese commit, y el job que publica espera la aprobación del entorno `docker-hub` (revisores obligatorios).
- Tag inmutable = **SHA completo del commit** (`<namespace>/<repositorio>:<sha>`). No se publica `:latest`; el workflow se niega a sobrescribir un tag existente.
- La imagen probada es la imagen publicada: se construye una vez, se prueba con `scripts/smoke_test_image.sh` (usuario no root, sin dependencias de desarrollo, `/health`, docs desactivadas, label de revisión) y solo entonces se hace `docker push`.
- Secretos configurados en GitHub (no en código), como *environment secrets* del entorno `docker-hub`: `DOCKER_HUB_USERNAME`, `DOCKER_HUB_TOKEN` (access token de Docker Hub con permiso de escritura sobre un único repositorio, nunca la contraseña). Variable `DOCKER_HUB_IMAGE` = `<namespace>/<repositorio>`; variable opcional `UV_VERSION` para fijar la versión de uv.
- Verificación: el job `Infra` pasa en la PR; el workflow publica en una ejecución de prueba; `docker inspect` muestra el SHA en el label `org.opencontainers.image.revision`; la imagen no contiene datos sensibles ni CVs (solo `src/`, `alembic/` y dependencias de runtime).

### Puesta en marcha (una sola vez, requiere admin del repositorio)
1. *Settings → Environments → New environment* `docker-hub`: **Required reviewers** (un compañero distinto de quien lanza el workflow; activar *Prevent self-review*) y **Deployment branches** limitado a `main`.
2. En ese entorno: secretos `DOCKER_HUB_USERNAME` y `DOCKER_HUB_TOKEN`, y variable `DOCKER_HUB_IMAGE`. El namespace sigue siendo una decisión pendiente (ver abajo): no se inventa ninguno.
3. En Docker Hub, crear el repositorio y, si el plan lo permite, activar la inmutabilidad de tags como segunda barrera (el workflow ya comprueba que el tag no exista).
4. Lanzar *Actions → Publish image → Run workflow* en `main`, aprobar el entorno y comprobar el resumen de la ejecución (tag, digest y commit).

### Contenido de la imagen y trazabilidad
- Etapa `production` de `backend/Dockerfile`: Python slim, entorno virtual con dependencias de runtime bloqueadas por `uv.lock` (`--locked --no-dev`), paquete instalado sin modo editable, sin `uv` ni tests, usuario `app` (UID 10001), `HEALTHCHECK` sobre `/health`, `SKILLMATCH_ENVIRONMENT=production` por defecto (docs de la API desactivadas; la validación de ajustes rechaza `debug` y CORS `*`).
- Labels OCI `revision` (SHA), `created`, `source`, `title` y `description`, más la variable `SKILLMATCH_GIT_SHA` para que `[P-05]` pueda exponer la versión desplegada.
- Incluye `alembic.ini` y `alembic/` para ejecutar las migraciones desde la misma imagen: `docker run --rm --env-file <env> <imagen> alembic upgrade head` (el despliegue y su orden pertenecen a `[P-07]`).

## Nivel 3 — Publicación y despliegue funcional
- Construcción de imagen identificable con tag de commit / versión; publicación en Docker Hub (o registro privado) con tag específico (implementado en `[P-06]`, ver Nivel 2).
- Despliegue a entorno accesible para demo/tribunal (no producción comercial).
- Health check, gestión básica de errores, registro de versión desplegada y commit de origen.
- Migraciones de DB controladas (Alembic); no destruye datos sin respaldo.
- Rollback: desplegar el tag SHA anterior conocido (todos los tags publicados son inmutables); no eliminar datos de DB sin plan.
- Evidencia requerida: URL accesible; demo funcional con datos sintéticos; no hay datos personales ni secretos expuestos.

## Decisiones pendientes
- Nombre definitivo de repositorio remoto y organización; namespace de Docker Hub; entorno de alojamiento para demo.
- Confirmar que la imagen no incluye datos reales ni credenciales antes de publicar.
- Confirmar con Vanessa (PO) que despliegue funcional es parte del alcance obligatorio para defensa, no solo build de imagen.

## Restricciones
- No publicar ni desplegar sin autorización expresa.
- No inventar credenciales, URLs ni namespaces.
- No incluir datos reales ni secreto en la imagen.

## Trazabilidad
- Requisito: NFR-010 ([`REQUIREMENTS.md`](REQUIREMENTS.md)); brecha C de [`REQUIREMENTS_TRACEABILITY.md`](REQUIREMENTS_TRACEABILITY.md).
- Tareas: `[P-06]` (Dockerfile de producción y publicación), `[P-07]` (despliegue accesible con rollback).

## Limitaciones conocidas de `[P-06]`
- Solo `linux/amd64`. Multi-arquitectura, SBOM y atestación de procedencia quedan fuera de alcance (la imagen se publica con `docker push` para garantizar que lo publicado es exactamente lo probado).
- Solo la imagen del backend. La imagen del frontend (build de Vite servido estáticamente o vía proxy) la decide `[P-07]`.
- La inmutabilidad real del tag depende de la configuración de Docker Hub; el workflow solo evita sobrescribir al publicar.
