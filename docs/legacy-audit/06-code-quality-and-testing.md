# Entregable 6 — Pruebas, calidad del código y deuda técnica

Estado: Completo

## Tests existentes
- No existen archivos `tests/` ni `test_*.py` en legacy.
- No hay archivo `pytest.ini`, `tox.ini`, ni configuración de tests.

## Calidad del código
- `extract_tecnoempleo.py`: funciones bien estructuradas (`extraer_datos_detalle`, `extraer_oferta`, `scrape_busqueda`, `main`). Uso de `requests.Session`. Manejo básico de errores (`try/except`). No hay tipado (`typing` no usado en archivo verificado).
- `clean_tecnoempleo_data.py`: funciones con nombres claros. Uso de `apply` y `re`. No hay tipado estricto. No hay docstrings detallados.
- `statistical_analysis.py`: archivo vacío.

## Deuda técnica
- No hay tipado estático (no `py.typed`, no `typing` sistemático).
- No hay manejo estructurado de errores (solo `try/except` básico).
- No hay logs estructurados.
- No hay documentación de API ni docstrings completos.
- No hay separación clara entre lógica de negocio y presentación (dashboard Streamlit contiene lógica de análisis según README).
- No hay CI (no hay `.github/workflows/`).

## Riesgos priorizados
1. Reproducibilidad baja (dependencias no fijadas, sin entorno aislado).
2. No hay regresión automatizada (sin tests).
3. Código con baja cobertura de errores (solo manejo básico en scraping).
4. No hay separación de datos sensibles ni control de acceso.
5. Datos sin esquema formal ni validación.
