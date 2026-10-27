# Contribuir

## Git

- `main` protegida; no commit directo salvo acuerdo del equipo.
- Branches: `feat/<issue>-short-name`, `fix/<issue>-short-name`, `docs/<issue>-short-name`, `audit/<scope>`.
- Commits semánticos sencillos: `feat: ...`, `fix: ...`, `test: ...`, `docs: ...`, `chore: ...`.
- PR describe requisitos, criterio de aceptación, decisión relevante, riesgo, tests exactos y capturas/demos con datos sintéticos.
- Un issue debe tener scope finito, owner humano, acceptance criteria y exclusiones.

## Para tareas realizadas con agentes

- Asignar un único agente implementador por área writable; investigación y revisión pueden paralelizarse read-only.
- Inspeccionar `git diff` antes de aceptar. El agente no se autoaprueba.
- Nunca incluir archivos de otros worktrees, secrets, datos reales ni outputs enormes.
- No permitir que el agente cierre issues, mergee o despliegue sin autorización explícita.

## Convención de requisitos

Usar IDs de `docs/REQUIREMENTS.md` en issues y commits/PR cuando aplique. Si un issue cambia la arquitectura, actualizar ADR antes/durante implementación.
