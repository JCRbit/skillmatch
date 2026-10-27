# Prompt inicial para el agente — auditoría antes de reconstruir

Actúa como arquitecto de software y auditor de repositorios. Tenemos un checkout legacy del proyecto `TinderJob_Fork` y un repositorio nuevo separado cuyo codename provisional es `SkillMatch`.

**La única tarea de esta primera fase es auditar; no reconstruyas todavía.** Lee `AGENTS.md`, `START_HERE.md`, `docs/PROJECT_CHARTER.md`, `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md` y `.agents/skills/legacy-audit/SKILL.md`.

Legacy está en: `<RUTA_ABSOLUTA_AL_CHECKOUT_LEGACY>`
Nuevo repo está en: `<RUTA_ABSOLUTA_AL_REPO_NUEVO>`
URL/branch/SHA conocidos: `<COMPLETAR_O_VERIFICAR>`

## Instrucciones obligatorias

1. Confirma que legacy se encuentra limpio o registra los cambios existentes. No modifiques ningún archivo bajo esa ruta.
2. Trabaja por inspección estática primero. No ejecutes notebooks, scrapers, instalaciones, contenedores, migraciones o scripts que se conecten a internet o cambien datos antes de revisar su código y obtener autorización.
3. No muestres valores secretos ni datos personales; si encuentras posibles credenciales, informa solo ruta y tipo de riesgo.
4. Distingue código ejecutable verificado, configuración, datos, notebooks, README y afirmaciones todavía no comprobadas.
5. Recorre todos los módulos relevantes, manifiestos de dependencias, lockfiles, licencias, CI/CD, tests, scripts de ejecución y entrada/salida de datos.
6. Genera los nueve outputs definidos en ` .agents/skills/legacy-audit/SKILL.md` dentro del nuevo repo.
7. Propón un plan de reconstrucción por etapas y una tabla de componentes `REUSE_AS_IS / ADAPT / REFERENCE_ONLY / REWRITE / DO_NOT_REUSE / UNKNOWN`, justificando cada estado con evidencias.
8. Mapea hallazgos contra los IDs de `docs/REQUIREMENTS.md`; identifica requisitos no cubiertos, decisiones que necesitan PO y riesgos que bloquean la reconstrucción.
9. No cambies arquitectura, no copies código ni añadas dependencias. No marques una capacidad como implementada solo porque un README la describe.
10. Termina con recomendación `GO / GO WITH CONDITIONS / NO-GO`, los bloqueadores y una agenda de revisión de 30 minutos para Vanessa (PO) y Javi (SM).

## Respuesta final esperada

- Resumen ejecutivo máximo una página.
- Tabla de evidencia con ruta + símbolo/líneas o comando estático.
- Artefactos creados.
- Huecos/unknowns (sin inventar).
- Recomendación de qué reutilizar y qué no.
- Tests o comandos no ejecutados y por qué.
- Ningún commit de código ni edición del legacy.
