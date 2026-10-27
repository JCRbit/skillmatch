# Harness de agentes, herramientas y flujo de trabajo

## Principio

El harness es el entorno que controla instrucciones, herramientas, permisos, contexto, pruebas y ejecución de agentes. No basta con pedirle al modelo que “tenga cuidado”. Las restricciones críticas deben reforzarse con permisos del sistema, hooks deterministas, sandbox, revisión humana y CI.

## Compatibilidad recomendada

| Harness | Archivos del repo | Uso |
|---|---|---|
| OpenAI Codex | `AGENTS.md`, `.agents/skills/*/SKILL.md` | Principal/alternativo; el flujo de skills se versiona y el agente debe releer docs tras compactación. |
| Claude Code | `CLAUDE.md`, `.claude/skills/*/SKILL.md` | CLAUDE delega a AGENTS; skills para auditoría y review. Hooks/permisos locales son responsabilidad de cada entorno, revisar antes de habilitar. |
| Cursor | `.cursor/rules/*.mdc`, `AGENTS.md` | Reglas globales pequeñas; procedimientos largos van a skills. |
| GitHub Copilot | `.github/copilot-instructions.md`, `AGENTS.md` según harness | Instrucciones compartidas; las pruebas se hacen en CI. |

Las funciones exactas varían por versión y configuración de cada harness; validar el descubrimiento de archivos con un test de humo después de instalar/actualizar herramienta.

## Diseño de roles para agentes

- **Coordinator / lead agent:** recibe issue aprobado, mantiene scope, solicita revisión cuando hay ambigüedad y prepara resumen.
- **Legacy audit agent (solo lectura):** inventario, dependencias, arquitectura, datos y reutilización; nunca edita legacy.
- **Implementation agent:** trabaja en una rama/worktree sobre un issue pequeño.
- **Test/reviewer agent:** revisa diff y añade tests de aceptación/seguridad; no revisa un cambio que él mismo haya hecho sin segunda revisión humana.
- **Privacy/security reviewer:** requerido para CV, matching, RAG, blind hiring, GitHub, browser extension, datos sensibles o autorización.

No lanzar varios agentes a editar simultáneamente las mismas rutas. Paralelizar investigación read-only o tareas en rutas claramente independientes. Resolver conflictos con el maintainer humano.

## MCP y conectores

MCP puede dar a agentes acceso a documentación, repositorios, issues o servicios; habilitar solo servidores conocidos, de menor privilegio y necesarios. No conectar secretos/producción para una tarea local. Documentar por servidor: propietario, URL, scopes, permisos de escritura, datos expuestos y cómo desconectarlo.

MCP de documentación oficial recomendado cuando se use API OpenAI: `https://developers.openai.com/mcp` (solo documentación). No es obligatorio elegir OpenAI como proveedor de embeddings/LLM.

## Práctica de ejecución segura

- Inicio: `git status`, commit SHA, branch y leer instructions.
- Fase 0: repositorio legacy con permisos filesystem de solo lectura, si el entorno lo permite; sin ejecución de código de proyecto.
- Implementación: branch/worktree propio, tests locales, diff revisado.
- CI: test/lint/typecheck/security scan con versiones bloqueadas.
- Acciones sensibles (deploy, migración destructiva, acceso a datos reales, coste de proveedor, submit externo): requieren confirmación humana explícita.
- No copiar prompts/secretos de una sesión a otra; contexto de proyecto reside en archivos versionados.

## Skills a usar

- `.agents/skills/legacy-audit/SKILL.md`
- `.agents/skills/architecture-review/SKILL.md`
- `.agents/skills/implement-issue/SKILL.md`
- `.agents/skills/privacy-review/SKILL.md`

## Señales de mala práctica

- “He terminado” sin tests o sin enseñar diff.
- Modificar legacy durante auditoría.
- Añadir Kafka/Spark/microservicios sin medida de necesidad.
- Dar por legal un scraper por ser técnicamente posible.
- Dejar el agente como administrador de shell/DB/producción sin sandbox.
- Confiar en texto libre para exigir reglas que podrían imponerse por permisos/hooks.
