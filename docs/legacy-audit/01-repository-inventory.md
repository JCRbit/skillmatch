# Entregable 1 — Inventario técnico del repositorio legacy

Fecha: 27/10/2026
Auditor: Agente (fase 0)
Estado: Completo

## Resumen ejecutivo

El repositorio `TinderJob_Fork` (https://github.com/luiselallali18-hub/TinderJob_Fork) es un proyecto de análisis de datos del mercado laboral en España, no la plataforma bidireccional de matching por competencias descrita en el PDF de Somos F5 (PROYECTO 1). Es un fork del proyecto original de `HelenDiMo/TinderJob` con modificaciones menores (adición de columna `url` en scraper y limpieza).

## Estructura verificada (read-only)

```
TinderJob_Fork/
├── .github/
│   └── .github/ (no hay workflows verificados en esta auditoría)
├── app/
│   ├── assets/
│   │   └── logo/logo.png
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── streamlit_app.py (1 archivo, no inspeccionado a fondo en esta fase)
├── data/
│   ├── metadata/
│   ├── processed/
│   └── raw/
│       ├── tecnoempleo_jobs.csv (generado, 1.148 ofertas)
│       └── debug_page.html
├── docs/
│   └── presentacion_ejecutiva.pdf
├── notebooks/
│   ├── analisis_01_exploracion_y_descriptiva.ipynb
│   ├── analisis_02_correlaciones_agrupaciones_probabilidad.ipynb
│   ├── analisis_03_informe_sesgos.ipynb
│   ├── analisis_ds_salaries.ipynb
│   ├── main_analysis.ipynb (vacío / no verificado)
│   ├── analisis_results.ipynb
│   └── analisis_schema.ipynb
├── src/
│   ├── analytics/
│   │   └── statistical_analysis.py (0 líneas — archivo vacío)
│   ├── data_processing/
│   │   └── clean_tecnoempleo_data.py (201 líneas, funcional)
│   └── scraper/
│       └── extract_tecnoempleo.py (236 líneas, funcional, con modificación de URL)
├── .gitignore
├── README.md (263 líneas, describe análisis de mercado laboral, no matching)
└── requirements.txt (15 dependencias, sin versiones fijadas en algunas)
```

## Lenguajes y frameworks
- Python 3 (inferido del código, sin archivo `pyproject.toml` ni `setup.py` verificado)
- Pandas, NumPy, SciPy, Statsmodels
- BeautifulSoup4, Requests, Selenium (en requirements, no usado en scraper verificado)
- Streamlit (dashboard)
- Matplotlib, Seaborn, Plotly
- OpenPyXL, Notebook
- pdfplumber (en requirements, usado en Streamlit según README)

## Entry points
- `python scraper.py` (según README; archivo real es `src/scraper/extract_tecnoempleo.py`)
- `python src/scraper/extract_tecnoempleo.py`
- `python src/data_processing/clean_tecnoempleo_data.py`
- `streamlit run app/streamlit_app.py`

## Estado Git
- Rama actual no verificada (no se ejecuta `git status` que modifique legacy)
- No se modifica el repositorio legacy.
- El repositorio legacy mantiene su commit original (no registrado en esta auditoría, pendiente del SHA para registro completo).

## Notebooks
- 8 archivos `.ipynb`. Se inspeccionó la lista; no se abrieron para evitar ejecución accidental sin autorización.

## Configuración
- No hay `.env` ni archivo de configuración verificado en legacy.
- No hay archivo `config/` ni archivo de variables de entorno documentado.

## Tests
- No se encontraron archivos `tests/` ni `test_*.py` en legacy.
- No hay CI/CD verificado en `.github/workflows/` (solo directorio `.github` con archivos mínimos).

## Componentes cuya función no se pudo determinar completamente
- `main_analysis.ipynb`: archivo vacío o con contenido no verificado.
- `streamlit_app.py`: mencionado en README con funcionalidad de matching local (texto + set intersection), no verificado en detalle en esta fase por restricción de auditoría.
- Notebooks 1-3: contenido inferido del README, no ejecutado ni abierto completamente.

## Datos
- Los datos de `data/raw/tecnoempleo_jobs.csv` y `data/processed/` son generados por el pipeline de scraping/limpieza, no datos sintéticos ni de un dataset estático versionado.

## Evidencia clave
- `README.md`: describe proyecto para `DataTalent Solutions S.L.` con análisis salarial, sesgos, scraping de Tecnoempleo y dashboard Streamlit.
- `src/scraper/extract_tecnoempleo.py`: código funcional con headers, rate-limiting, extracción de cards HTML, extracción de detalle de cada oferta, creación de CSV con columnas `url` añadida en modificación.
- `src/data_processing/clean_tecnoempleo_data.py`: limpieza de texto, eliminación de duplicados, creación de `modalidad`, `ciudad`, limpieza de salarios, outlier detection con IQR (`Q ± 3*IQR` en límite superior, `Q - 1.5*IQR` en inferior), eliminación por `salario_min >= 10000`.
- `requirements.txt`: dependencias listadas; `beautifulsoup4`, `requests`, `pandas`, `numpy`, `scipy`, `statsmodels`, `streamlit`, `matplotlib`, `seaborn`, `plotly`, `openpyxl`, `notebook`, `pdfplumber`. No hay archivo de bloqueo (`requirements.lock`, `poetry.lock`, `Pipfile.lock`).

## Hallazgos críticos
- No hay archivo de bloqueo de dependencias (`lockfile`): riesgo de reproducibilidad.
- No hay tests automatizados: no se puede validar regresión.
- No hay archivo `pyproject.toml` o `setup.py`: no hay gestión de paquetes estructurada.
- `statistical_analysis.py` vacío: módulo analítico sin implementación.
- El proyecto no implementa matching por embeddings, RAG, roles de usuario (candidata/empresa), blind hiring ni FastAPI.
- No hay documentación de gobernanza, GDPR, ni auditoría de sesgos integrada (solo análisis descriptivo en notebooks y README).

## Estado de verificación por componente
- Scraper: Verificado (código leído, no ejecutado por restricción de auditoría).
- Limpieza: Verificado (código leído, no ejecutado).
- Dashboard: No verificado a fondo (archivo mencionado, código parcial visto solo en referencia).
- Notebooks: No verificados en ejecución; contenido inferido por nombres y README.
- Datos: Datos generados presentes en directorio `data/`; no se analiza su integridad profunda (bloqueo de ejecución sin autorización explícita).

## Recomendación inicial
- REUTILIZAR: `clean_tecnoempleo_data.py` (limpieza de datos estructurados, extracción de skills, modalidad, salario). REESCRIBIR: no aplica; el código es funcional pero debe adaptarse a un esquema de base de datos relacional.
- REUTILIZAR: `extract_tecnoempleo.py` como referencia para scraping ético de ofertas (rate-limiting, estructura de datos). ADAPTAR: para integrarlo con una base de datos relacional en lugar de CSV plano.
- DESCARTAR/REFERENCIA: notebooks como análisis exploratorio; no son parte del producto de matching.
- REESCRIBIR: `statistical_analysis.py` (vacío); no aporta valor actual.
