# ADR-0006 — Harness portable para desarrollo con agentes

- Estado: Propuesto

Usar `AGENTS.md` como fuente canónica portable. Añadir adaptadores finos para Claude Code (`CLAUDE.md` + `.claude/skills/`), Cursor (`.cursor/rules/`) y GitHub Copilot (`.github/copilot-instructions.md`). Mantener procedimientos largos en Skills versionadas; usar MCP solo para integraciones que necesiten fuentes/acciones y aplicar permisos mínimos.

Los agentes pueden proponer e implementar issues acotados en ramas/worktrees. La persona responsable revisa diffs, pruebas y riesgo. No permitir que un agente despliegue, haga cambios irreversibles, maneje secretos ni envíe candidaturas. Los hooks/permisos del harness se usan como barreras deterministas para comandos sensibles; instrucciones de texto solas no son una barrera de seguridad.

No estandarizar un proveedor único de agente. Ver `docs/HARNESS_AND_AGENT_WORKFLOW.md`.
