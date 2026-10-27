# Requisitos y trazabilidad

Estados permitidos: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `VERIFIED`, `DEFERRED`. No marcar `VERIFIED` sin evidencia de test o demo reproducible.

## Funcionales

| ID | Requisito | Criterio de aceptación | Prioridad | Verificación inicial |
|---|---|---|---|---|
| FR-001 | Registro/autenticación y roles Candidate, Company, Admin | Pruebas de acceso válido/inválido y permisos por rol; endpoints rechazan acceso cruzado | P0 | Tests API |
| FR-002 | CRUD de perfil candidato | Crear, consultar, editar y eliminar/solicitar borrado; validación de datos | P0 | API + UI tests |
| FR-003 | CRUD de empresa y ofertas | Empresa solo modifica sus ofertas; otras cuentas no acceden | P0 | Tests de autorización |
| FR-004 | Ingestión y normalización de oferta | Esquema común con fuente, URL, fechas, identificador externo y estado de publicación | P0 | Fixture + integration test |
| FR-005 | Fuente ética/legal para ofertas | Cada conector tiene fuente, términos revisados, política de frecuencia y mecanismo de desconexión | P0 | Registro de fuentes |
| FR-006 | Análisis de CV PDF | Extrae texto/atributos con validación, errores controlados, eliminación del archivo según política | P0 | Fixtures sintéticas |
| FR-007 | Análisis de GitHub | Solo repos autorizados/públicos o acceso explícito; rate limits; registra referencias a evidencia | P0 | Fixtures/API mocked |
| FR-008 | Matching semántico candidato↔oferta | Top-k reproducible con filtros estructurados y semánticos | P0 | Dataset de evaluación |
| FR-009 | Explicación del matching | Cada resultado muestra factores, evidencia, incertidumbre y carencias; explicación coincide con datos usados | P0 | Tests de contrato y evaluación humana |
| FR-010 | Modelo/ranking evaluable | Línea base explícita; dataset, métricas, split, versión y limitaciones documentadas; solo llamar “entrenado” si hubo entrenamiento verificable | P1 | Informe de evaluación |
| FR-011 | Interés mutuo | Un solo interés no revela contacto; dos intereses válidos crean match de manera idempotente | P0 | Tests de estado/seguridad |
| FR-012 | Vista ciega temprana | API/UI/exports/logs no filtran campos bloqueados antes de etapa autorizada | P0 | Tests negativos de filtración |
| FR-013 | Canal de contacto tras match | Solo las dos partes del match pueden ver los datos definidos | P0 | Tests de autorización |
| FR-014 | RAG de empresa/oferta | Respuestas restringidas a contexto autorizado; referencias a fuentes; fallback de desconocimiento | P1 | Corpus sintético + tests adversariales |
| FR-015 | Asistente de preparación de entrevistas | Sugiere preguntas y preparación basadas en oferta, sin inventar requisitos/empresa | P1 | Set de evaluación |
| FR-016 | Sugerencias de perfil y carta | Borradores editables sustentados por datos del usuario; nunca envío automático | P1 | Pruebas con perfiles sintéticos |
| FR-017 | Dashboard empresa | Métricas de pipeline y estados agregados con supresión de grupos pequeños cuando proceda | P1 | Test UI + cálculos |
| FR-018 | Auditoría de acciones | Registra quién hizo qué, cuándo, entidad, resultado y versión relevante, sin guardar payloads sensibles innecesarios | P0 | Tests de auditoría |
| FR-019 | Gestión de consentimiento/datos | Explicar uso, permitir retirar consentimiento/borrado conforme a política; limpieza de índices derivados y backups según diseño | P0 | Tests de ciclo de vida |
| FR-020 | Apply Copilot (stretch) | Rellena campos estándar en sitios de prueba; propuesta revisable; no submit automático, no credenciales/cookies | P2 | Playwright fixtures/manual |

## No funcionales

| ID | Requisito | Criterio de aceptación | Prioridad |
|---|---|---|---|
| NFR-001 | Separación legacy/nuevo | Repos separados; legacy read-only durante auditoría; reutilización mediante registro aprobado | P0 |
| NFR-002 | Mantenibilidad | Backend modular, type hints, lint, migraciones versionadas, README de ejecución | P0 |
| NFR-003 | Rendimiento vectorial | p95 <300 ms en retrieval top-k sobre dataset y hardware documentados; medir con datos/consulta definida y warm/cold separado | P1 |
| NFR-004 | Disponibilidad observable | Health/readiness, logs estructurados, error IDs y métricas básicas; no prometer SLA productivo sin despliegue | P1 |
| NFR-005 | Seguridad | Autorización del servidor, gestión segura de secretos, límites de tasa, validación de uploads, tests de acceso indebido | P0 |
| NFR-006 | Privacidad | Minimización, retención limitada, derecho de borrado, acceso por finalidad, datos de prueba sintéticos | P0 |
| NFR-007 | Equidad | Protocolo de auditoría de sesgos, variables/proxies considerados, límites y mitigaciones documentados | P0 |
| NFR-008 | Supervisión humana | Resultados informativos, overrides y revisión humana registrables; no decisión laboral autónoma | P0 |
| NFR-009 | Reproducibilidad | Dataset/versiones/modelos/prompts/configs/versionadas; evaluación repetible | P1 |
| NFR-010 | CI/CD | CI para test/lint/typecheck/build y scan de dependencias; deploy manual/protegido | P0 |
| NFR-011 | Accesibilidad/usabilidad | Flujos principales probados en móvil/desktop y navegación por teclado básica | P1 |

## Entregables de evaluación

- Código modular con pruebas unitarias/integración, tipado y documentación.
- Pipeline MLOps reproducible con CI y Docker.
- Informe de gobernanza, privacidad, auditoría de sesgo y riesgos.
- Evaluación del matching/ranking y model card si se desarrolla un modelo ML entrenado.
- Demo funcional y guion con datos sintéticos.
- Informe de auditoría legacy y decisión de reconstrucción.

## Notas de interpretación

- “Porcentaje de afinidad” no debe presentarse como probabilidad de contratación. Definir escala/normalización, calibración y limitaciones.
- “Modelo de ranking entrenado” no es demostrable sin datos etiquetados, metodología, baseline y evaluación. Si no existe, entregar baseline explicable y registrar qué datos faltan.
- El umbral de 300 ms debe aclarar qué se mide: retrieval vectorial no incluye extracción PDF, generación de embeddings ni tiempo de respuesta LLM.
