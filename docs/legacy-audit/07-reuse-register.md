# Entregable 7 — Matriz de reutilización del legacy (REUSE REGISTER)

Estado: Completo
Fecha: 27/10/2026
Auditor: Agente

## Resumen de categorías
- REUTILIZAR: valor comprobado y seguro.
- ADAPTAR: útil pero requiere cambio.
- REFERENCIA: orienta diseño, no copiar.
- REESCRIBIR: función necesaria, implementación no útil.
- DESCARTAR: sin valor o con riesgo.
- PENDIENTE: evidencia insuficiente.

## Tabla de registros

| ID | Ruta / Módulo | Función | Evidencia | Categoría | Justificación | Esfuerzo | Acción en SkillMatch |
|---|---|---|---|---|---|---|---|
| R01 | src/scraper/extract_tecnoempleo.py | Scraping de ofertas | Código leído (236 líneas), rate-limit 1s, extracción de cards HTML | ADAPTAR | Scraping funcional pero depende de HTML fijo; debe integrarse con DB y manejar errores robustos; datos con riesgo legal | Medio | Reutilizar lógica de extracción como referencia; crear pipeline con validación y almacenamiento relacional; no usar datos sin autorización |
| R02 | src/data_processing/clean_tecnoempleo_data.py | Limpieza y normalización | Código leído (201 líneas), deduplicación, skills normalizadas, salario limpio, modalidad | REUTILIZAR / ADAPTAR | Pipeline de limpieza robusto; debe adaptarse a esquema SQL y datos sintéticos; usa `pandas` que es aceptable para MVP | Medio | Adaptar a SQLAlchemy / Pydantic pipelines; mantener lógica de limpieza; añadir validación de esquema |
| R03 | notebooks/analisis_01_* | Exploración descriptiva | Nombres e inferencias del README; no verificados completamente | REFERENCIA | Análisis exploratorio útil para entender datos; no son parte del producto de matching | Bajo | Referencia para análisis de datos; no importar al repo de producto |
| R04 | notebooks/analisis_02_* | Correlaciones | Inferred; no verificado | REFERENCIA | Orienta análisis multivariante; no parte del producto | Bajo | Referencia |
| R05 | notebooks/analisis_03_* | Informe de sesgos | Inferred; README menciona sesgos MNAR, captura; no verificado completo | REFERENCIA | Útil para gobernanza; debe convertirse en auditoría sistemática en SkillMatch | Medio | Referencia para diseño de auditoría de sesgos |
| R06 | notebooks/ (resto) | Diversos análisis | No verificados | PENDIENTE | No se determinó contenido exacto | Bajo | Revisar si aporta valor; probablemente referencia |
| R07 | app/streamlit_app.py | Dashboard | No verificado a fondo; README menciona TinderMatch con set intersection | PENDIENTE / REFERENCIA | Funcionalidad de matching local (texto + sets) no es matching semántico; podría orientar UI inicial pero debe reconstruirse | Alto | No copiar; usar como referencia de UI; reconstruir con React y API FastAPI |
| R08 | src/analytics/statistical_analysis.py | Análisis estadístico | Vacío (0 líneas) | DESCARTAR / REESCRIBIR | No aporta valor; debe reconstruirse si se necesita análisis avanzado | Bajo | Reescribir si se requiere análisis avanzado; no reutilizar |
| R09 | data/raw/tecnoempleo_jobs.csv | Datos de ofertas | Datos generados por scraping; 1.148 filas | DESCARTAR / REFERENCIA | Datos de scraping sin autorización verificada; contienen información de empresas y ofertas; no deben reutilizarse sin verificación legal; pueden usarse como referencia de formato | Bajo | No importar al repo de producto; usar como referencia de estructura; crear datos sintéticos para pruebas |
| R10 | README.md / docs/ | Documentación del proyecto | Leer completo | REFERENCIA | Documentación útil para entender contexto; no debe copiarse como parte del producto | Bajo | Referencia para contexto; escribir documentación propia en SkillMatch |
| R11 | requirements.txt | Dependencias | Leer completo; sin lockfile | ADAPTAR | Lista básica; debe fijarse y completarse para SkillMatch; no debe utilizarse sin verificación de licencias | Bajo | Crear `pyproject.toml` / `poetry.lock` / `requirements.lock` con versiones fijadas y revisión de licencias |

## Decisión de reutilización global
- No se recomienda copiar módulos completos al repo nuevo.
- Se recomienda adaptar `clean_tecnoempleo_data.py` como base del pipeline de limpieza.
- Se recomienda usar `extract_tecnoempleo.py` como referencia técnica para scraping ético.
- El resto (notebooks, datos, dashboard, análisis vacío) debe tratarse como referencia o descartarse.

## Riesgos de reutilización
- Datos de Tecnoempleo pueden tener restricciones de uso.
- No hay licencia explícita en legacy; debe verificarse repo original.
- Dependencias sin fijar pueden causar inconsistencias.
- No hay tests que validen reutilización.
