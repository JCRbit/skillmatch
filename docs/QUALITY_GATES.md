# Quality gates y CI

## Pull request checks (objetivo)

1. Validar formato, lint y type checking.
2. Ejecutar unit tests.
3. Ejecutar integration tests sobre PostgreSQL/Qdrant/Redis en jobs separados o fixtures controladas según alcance.
4. Frontend: lint, unit, build; Playwright smoke para journeys principales en PR/nightly.
5. Dependency vulnerability scan y secret scan.
6. Verificar migraciones en una DB temporal; jamás aplicar migraciones a producción desde PR.
7. Comprobar que los archivos de trazabilidad/ADRs siguen actualizados cuando se afecte comportamiento.

## Fase de auditoría

No se instala o ejecuta la aplicación legacy solo para tener CI verde. Los hallazgos registran si las pruebas son ejecutables, qué comandos requieren servicios o credenciales, y qué riesgo hay en ejecutar scripts.

## Objetivo de merge

- Required status checks aprobados.
- Como mínimo una revisión humana que no sea únicamente el agente autor.
- No secrets/vulnerabilidades críticas sin tratamiento/aceptación explícita.
- Sin cambios destructivos ni despliegue a producción desde agentes.
