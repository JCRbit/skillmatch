# Empieza aquí — paquete fundacional de SkillMatch

> **Codename provisional:** `SkillMatch`. No es una decisión de marca. Vanessa (PO) debe aprobar el nombre final y el nombre de los repositorios antes de publicar nada.
> **Fuente legacy:** `luiselallali18-hub/TinderJob_Fork` (auditar; no modificar durante la fase 0).
> **Plazo del proyecto formativo:** 2 de noviembre–11 de diciembre de 2026.

## La decisión clave: no mezclar repositorios

Mantén el fork antiguo como fuente de solo lectura y crea un repositorio nuevo para el producto. No sueltes este paquete dentro del árbol legacy.

```text
workspace/
├── tinderjob-legacy/       # clone del fork; solo lectura durante la auditoría
│   └── ...                 # notebooks, dashboard y pipeline existentes
└── skillmatch/             # nuevo repositorio Git; aquí se descomprime este paquete
    ├── AGENTS.md
    ├── docs/
    ├── scripts/
    └── ...
```

El nombre `skillmatch` es provisional. Si el nombre definitivo cambia, renombra el directorio y actualiza `PROJECT_NAME` en `docs/PROJECT_CHARTER.md`, no la carpeta legacy.

## Pasos para el equipo

1. **Congelar y conservar legacy.** No borrar, mover ni reformatear nada del fork. Registrar URL, branch, commit SHA, fecha, `git status` y una copia de respaldo accesible.
2. **Crear un repositorio nuevo vacío** —por ejemplo, `skillmatch-platform`— bajo la organización/cuenta que decida el equipo. No lo crees como una rama nueva dentro del repositorio legacy.
3. **Clonar el repositorio nuevo y descomprimir aquí el paquete.** Añadir estos archivos al nuevo repo; revisar el nombre provisional antes del primer commit.
4. **Clonar el fork al lado, no dentro del nuevo repo.** El agente debe tener acceso de lectura a ambos directorios.
5. **Ejecutar la auditoría en modo read-only.** Usa `scripts/legacy_inventory.sh ../tinderjob-legacy` desde la raíz del repo nuevo. El script no debe modificar legacy; la salida se guarda en `docs/legacy-audit/generated/`.
6. **Pedir al agente la auditoría completa** usando `.agents/skills/legacy-audit/SKILL.md` (o `AUDIT_FIRST_PROMPT.md`). No autorizar implementación todavía.
7. **Revisar el inventario, evidencias, riesgos y registro de reutilización.** Vanessa acepta el alcance; Javi facilita la sesión y registra bloqueos/acuerdos.
8. **Aprobar arquitectura y ADRs** antes de copiar cualquier módulo desde legacy.
9. **Extraer selectivamente** solo componentes aprobados, con pruebas y procedencia/licencia documentadas. No hacer un `cp -r` del proyecto antiguo al nuevo.

## Comandos iniciales sugeridos

```bash
mkdir -p ~/workspace
cd ~/workspace
# Repositorio antiguo: clónalo como referencia y no trabajes aquí.
git clone https://github.com/luiselallali18-hub/TinderJob_Fork.git tinderjob-legacy

# Crea primero el repo nuevo en GitHub (vacío) con el nombre aprobado.
git clone <URL_DEL_REPO_NUEVO> skillmatch
cd skillmatch
unzip <RUTA>/skillmatch-foundation-pack.zip
# Revisa nombre, URLs, permisos y archivos antes de commitear.
git status --short
git add .
git commit -m "docs: add project foundation and agent workflow"
```

Si el clone del fork falla por permisos, visibilidad o URL, **no improvises ni crees un clon ficticio**: pide acceso o usa el checkout local existente y registra la ruta real en el informe de auditoría.

## Primera instrucción al agente

Usa el texto de `AUDIT_FIRST_PROMPT.md`. Su alcance es solo inventariar y analizar. No instala dependencias, no ejecuta notebooks, no importa el legacy como módulo, no cambia configuración ni aplica migraciones. Debe producir informes con evidencia, no iniciar la reconstrucción.

## Qué contiene este paquete

- `AGENTS.md` y adaptadores de instrucciones para Claude Code, Cursor y GitHub Copilot.
- Skills reutilizables para auditoría legacy, revisión de arquitectura, implementación acotada y privacidad.
- Requisitos trazables, arquitectura propuesta, decisiones ADR, modelo de datos, evaluación y gobernanza.
- Reparto propuesto con Vanessa como PO y Javi como SM.
- Runbooks, plantillas para issues/PR, checklist de calidad, inventario scriptable y especificación de Apply Copilot.

## Criterio de salida de la fase de auditoría

No comenzar la reconstrucción hasta tener: inventario, mapa de ejecución, dependencias/licencias, problemas de seguridad, pruebas ejecutables, calidad de datos, lista de componentes reutilizables y una decisión explícita de Vanessa sobre el alcance de la primera iteración.
