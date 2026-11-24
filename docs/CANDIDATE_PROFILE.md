# Perfil de candidato: CRUD, skills declaradas, preferencias y visibilidad (B-03)

Cubre **FR-002** (CRUD de perfil de candidato) y la parte de servidor de **US-01**. La autenticación y la
autorización son las de B-02 ([AUTHENTICATION.md](AUTHENTICATION.md)); aquí solo se **reutilizan**. Código:
`backend/src/skillmatch/modules/candidates` (modelos, esquemas, repositorio, servicio) y
`backend/src/skillmatch/api/candidates.py` (endpoints).

## Endpoints

Todos exigen `Authorization: Bearer <token>` de una cuenta **`talento`** activa. Cualquier otro rol (`empresa`,
`admin`) recibe `403 permission_denied`; sin credencial válida, `401`. Los errores son RFC 9457
(`application/problem+json`). El contrato vive en `backend/openapi.json`.

| Endpoint | Efecto | Errores propios |
|---|---|---|
| `POST /api/v1/candidates/me` | Crea el perfil (privado y sin preferencias) → `201` | `409 candidate_profile_already_exists`, `422` |
| `GET /api/v1/candidates/me` | Perfil + preferencias + flags de visibilidad | `404 candidate_profile_not_found` |
| `PATCH /api/v1/candidates/me` | Actualización parcial: solo cambia lo enviado | `404`, `422` |
| `DELETE /api/v1/candidates/me` | Borra perfil y skills (la cuenta se conserva) → `204` | `404` |
| `PUT /api/v1/candidates/me/preferences` | Reemplaza **todas** las preferencias | `404`, `422` |
| `PUT /api/v1/candidates/me/visibility` | Fija los dos flags de visibilidad | `404`, `422` |
| `GET /api/v1/candidates/me/skills` | Lista de skills declaradas, por nombre | `404` |
| `POST /api/v1/candidates/me/skills` | Declara una skill → `201` | `404`, `409 skill_already_declared`, `409 skill_limit_reached`, `422` |
| `PATCH /api/v1/candidates/me/skills/{skill_id}` | Cambia nombre y/o nivel | `404 not_found`, `409`, `422` |
| `DELETE /api/v1/candidates/me/skills/{skill_id}` | Elimina la skill → `204` | `404 not_found` |

## Decisiones de diseño

| Tema | Decisión | Por qué |
|---|---|---|
| Identidad del propietario | No hay ningún identificador de candidato en URLs ni cuerpos: el recurso es siempre `/me`, resuelto con `CurrentUserDep` vía `require_roles(UserRole.TALENTO)`. Los cuerpos usan `extra="forbid"`, así que `user_id`, `id`, `email` o `role` dan `422` | "Nunca usar identificadores del cliente como prueba de identidad o propiedad" |
| Único id del cliente | `skill_id`. Se comprueba con `verify_resource_ownership(..., hide_if_unauthorized=True)` y, además, la consulta de escritura filtra por `user_id` (doble barrera) | Acceso entre cuentas |
| 403 vs 404 | Perfil y colecciones: no hay forma de apuntar al de otro. Skills ajenas: **404**, con el mismo `code`, `title` y `detail` que una skill inexistente | Evita enumerar ids |
| Separación identidad/perfil | Tabla propia `candidate_profiles` con `user_id` (FK única, `ON DELETE CASCADE`). No duplica email, rol ni estado; `users` no cambia. La respuesta nunca incluye identidad | `DATA_MODEL.md`, D-09 |
| Pseudónimo | `display_name` es el nombre que muestra el candidato (no se pide nombre real) | Modo ciego, minimización |
| Privado por defecto | `discoverable=false`, `show_location=false` y preferencias vacías al crear. `PUT visibility` exige **ambos** booleanos estrictos (`"yes"`, `1` o `null` dan `422`) | US-08: sin perfil compartido por defecto |
| `PUT` completo | Preferencias y visibilidad requieren todos los campos. Las listas vacías representan ausencia de preferencias; si falta algún campo, la petición se rechaza con 422 y no modifica los datos existentes. | Evita pérdida accidental de datos |
| `PATCH` parcial | Solo cambia lo enviado; `summary` y `city` admiten `null` para borrarse; `display_name` y `languages` no | Semántica clara |
| Skills | `name` conserva lo escrito (espacios normalizados), `name_key` es su `casefold()` y es único por candidato; nivel `beginner/intermediate/advanced` **autodeclarado**, con `CHECK` en base de datos; máximo 50 por candidato | Sin duplicados `Python`/`python`; perfil acotado |
| Borrado | Borrado real del perfil y sus skills (FR-002 "eliminar/solicitar borrado"); la cuenta sigue y puede crear otro perfil | Derecho de supresión; el borrado de documentos, vectores y logs llegará con sus módulos |
| Carreras | Si dos peticiones pasan la comprobación previa, la restricción única de la base de datos las convierte en `409`, no en `500` | Corrección bajo concurrencia |
| Listas | Preferencias y lenguas se guardan como `JSON` (portables entre PostgreSQL y SQLite de tests) | Sin dependencias nuevas |
| Errores | Los mensajes de validación no repiten el dato enviado | NFR-005, datos personales |
| Dependencias | Ninguna nueva | `AGENTS.md` |

Datos que **no** hay en este módulo, a propósito: consentimientos con fecha y retirada (B-05), proyección
seudonimizada para empresas y sus tests de no filtración (B-06), taxonomía canónica de skills y evidencias
(S-xx). Los flags de B-03 son la entrada de B-05/B-06; **por sí solos no publican nada**.

## Esquema físico

Migración `5d1e7a3c9b24` (encadena con `2ccafd5b8547`).

| Tabla | Columnas | Restricciones |
|---|---|---|
| `candidate_profiles` | `id`, `user_id`, `display_name(80)`, `summary`, `city(100)`, `languages`, `work_modes`, `contract_types`, `preferred_locations`, `interests`, `discoverable`, `show_location`, `created_at`, `updated_at` | PK `id`; FK `user_id → users.id` `ON DELETE CASCADE`; índice **único** `ix_candidate_profiles_user_id` |
| `candidate_skills` | `id`, `candidate_id`, `name(60)`, `name_key(60)`, `level(20)`, `created_at`, `updated_at` | PK `id`; FK `candidate_id → candidate_profiles.id` `ON DELETE CASCADE`; único `uq_candidate_skills_candidate_id_name_key`; `CHECK ck_candidate_skills_level` |

## Criterios de aceptación y dónde se prueban

| Criterio (issue #30) | Pruebas |
|---|---|
| Crear y consultar el propio perfil | `test_a_candidate_can_create_and_read_their_profile`, `test_a_new_profile_is_private_and_has_no_preferences` |
| Actualizar el propio perfil | tests `PATCH` en `tests/api/test_candidate_profile.py` |
| CRUD de skills declaradas | `test_a_candidate_can_declare_and_list_skills`, `test_a_skill_can_be_updated`, `test_a_skill_can_be_deleted`, duplicados, límite y validación |
| Preferencias y visibilidad persisten | `test_preferences_can_be_replaced_…`, `test_visibility_flags_can_be_set_and_persist`, `test_changes_persist_and_stay_linked_to_the_authenticated_account` |
| Identidad y perfil separados | `tests/unit/test_candidate_models.py`, `test_the_profile_never_exposes_identity_data`, `test_the_identity_record_is_not_modified_by_profile_operations`, `test_the_candidate_contract_has_no_identity_fields` |
| Todo usa la identidad autenticada de B-02 | `test_every_endpoint_requires_authentication`, `test_a_forged_token_is_rejected_on_every_endpoint`, `test_a_spoofed_identity_header_is_ignored`, `test_the_client_cannot_choose_the_owner_of_a_profile` |
| Un candidato no accede a datos de otro | bloque "cross-account isolation" de `test_candidate_profile.py` (ver, modificar y borrar skills ajenas; 404 indistinguible de inexistente) |
| Roles no autorizados bloqueados | `test_only_candidates_reach_the_candidate_endpoints` (empresa y admin, los 10 endpoints) |
| Persistencia comprobada en base de datos | helpers `stored_profile` / `stored_skills` leen la base de datos con una sesión distinta de la de la petición |
| Pruebas negativas y de concurrencia | `test_candidate_service_races.py`, parametrizaciones de entradas inválidas |
| Contrato OpenAPI | `test_the_candidate_endpoints_are_documented_and_protected`, `test_the_committed_contract_matches_the_application` |

## Limitaciones conocidas

| Limitación | Nota |
|---|---|
| El administrador no gestiona perfiles ajenos | Los endpoints son exclusivos del rol `talento`; un `admin` recibe `403`. Si el PO quiere moderación, se añade una tarea con auditoría (`audit_events`) |
| Sin auditoría de cambios | Llega con el módulo `audit` |
| Sin límite de peticiones | Tarea B-09 |
| Sin versión/`ETag` | Dos `PATCH` simultáneos del mismo campo: gana el último (es el mismo candidato) |
| `languages` son códigos ISO 639 de 2–3 letras en minúscula | No se valida contra la lista oficial |
| Las skills no están ligadas a la taxonomía canónica | Tarea posterior; `name_key` permitirá mapear sin cambiar el contrato |
| Concurrencia PostgreSQL | La serialización de altas concurrentes de skills mediante `SELECT FOR UPDATE` está diseñada para PostgreSQL, pero todavía no dispone de una prueba de integración con transacciones concurrentes reales. Las pruebas actuales verifican escenarios de carrera mediante simulaciones |
