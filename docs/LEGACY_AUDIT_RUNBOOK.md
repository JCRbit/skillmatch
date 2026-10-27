# Runbook de auditoría legacy

## Objetivo

Determinar qué existe realmente, qué funciona, qué datos produce y qué puede reutilizarse legal/técnicamente. El reporte anterior que describe unas 1.148 ofertas y un dashboard de análisis se toma como hipótesis inicial hasta verificar archivos y commit.

## Fases de inspección

### 1. Identidad y estado

Registrar remote URL, branch, commit SHA, tags, fechas, worktree status, submodules, tamaño de repo y LFS si aplica. No cambiar ni resetear el árbol.

### 2. Estructura y tecnología

Listar archivos rastreados, lenguajes, manifests/lockfiles, Docker, CI, datos, notebooks, notebooks outputs, artefactos grandes, tests y entrypoints. Identificar duplicaciones, versiones, datos personales y archivos con secretos probables.

### 3. Reproducibilidad

Leer instrucciones de instalación y ejecución. Antes de correr nada, inspeccionar comandos, acceso a internet, escritura de datos, credentials, scraping y coste. Si se autoriza ejecución, preferir una copia aislada/sandbox con datos sintéticos y variables dummy. Registrar comando, entorno, retorno y logs redacted.

### 4. Data pipeline

Para cada etapa documentar fuente, schema raw, transform, dedupe, errores, output, reproducibilidad, idempotencia, licencias, terms of source, fechas de frescura y validación. Calcular data quality si se puede hacerlo sin exponer datos personales.

### 5. Seguridad y privacidad

Inspección estática de `.env` names, configuración, API keys, auth, permisos, uploads, llamadas externas y logs. Usar `gitleaks` si está instalado y autorizado; tratar el output como sensible y no incluir secretos en el informe.

### 6. Licencias y derechos de datos

Separar licencia del código, licencia del dataset, términos del portal, datos derivados y assets. `No license` no significa permiso para copiar código. La presencia de ofertas en el repo no prueba derecho a redistribuirlas.

### 7. Evaluación y decisión

Cada componente recibe estado de reuse y tareas para convertirlo en mantenible. Marcar dependencias de infraestructura/datos que bloqueen el MVP. PO decide y documenta excepción.

## Template de hallazgo

- ID / título:
- Severidad: critical / high / medium / low / info
- Confianza: high / medium / low
- Evidencia (commit SHA, ruta, función/líneas, comando estático):
- Riesgo/impacto:
- Acción recomendada:
- Prioridad y esfuerzo:
- Bloquea reconstrucción: yes/no
- Owner:
