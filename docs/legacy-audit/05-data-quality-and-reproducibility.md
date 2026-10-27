# Entregable 5 — Calidad de datos y reproducibilidad

Estado: Completo

## Formatos
- Entrada: HTML (Tecnoempleo) → CSV crudo; CSV limpio → notebooks / Streamlit.
- Salida: CSV procesado; visualizaciones PDF/HTML (no verificado en ejecución).

## Esquemas
No hay archivo de esquema formal (`schema.json`, `sqlalchemy` models). El esquema se infiere de `clean_tecnoempleo_data.py`: columnas `titulo`, `empresa`, `ubicacion`, `salario`, `tipo_contrato`, `skills`, `busqueda`, `url` (en raw); adicionales `modalidad`, `ciudad`, `salario_min`, `salario_max`, `salario_medio`, `es_outlier` (en processed).

## Duplicados y valores ausentes
- Scraper: `drop_duplicates` por `titulo` + `empresa` (en `extract_tecnoempleo.py`).
- Limpieza: `drop_duplicates` por `titulo`, `empresa`, `ubicacion`, `salario`, `tipo_contrato` (más estricto).
- Valores nulos: no hay tratamiento sistemático de nulos en `skills`; se asume que `skills` puede ser `None`; `limpiar_skills` maneja `pd.isna`.

## Proveniencia y frescura
- Datos generados por scraping en momento de ejecución; no hay timestamp ni versión de fuente.
- No hay control de versiones en datos (solo en código Git).

## Dependencias de rutas locales
- `raw_data = 'data/raw/tecnoempleo_jobs.csv'` y `clean_data = 'data/processed/clean_tecnoempleo_jobs.csv'`: rutas relativas; dependen de directorio de ejecución.
- No hay configuración de rutas (no `os.path.dirname(__file__)`).

## Reproducibilidad
- No hay `Dockerfile` ni entorno aislado definido para ejecución completa.
- No hay archivo de bloqueo (`requirements.lock`); versiones de `pandas`, `numpy`, etc. no fijadas.
- No hay script de ejecución que orqueste todo (scraper + limpieza + análisis + dashboard) en secuencia reproducible.
- No hay datos de prueba sintéticos ni dataset de referencia.

## Recomendación
- Fijar dependencias y crear `Dockerfile` o `docker-compose.yml` en SkillMatch.
- Crear dataset sintético para pruebas reproducibles.
- Documentar esquemas formalmente (Pydantic / SQLAlchemy / JSON Schema).
