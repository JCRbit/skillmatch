# Entregable 3 — Dependencias, licencias y reutilización legal

Estado: Completo (evidencia estática de requirements.txt; no se verificaron licencias individuales de cada librería en esta fase)

## Dependencias directas (requirements.txt, 15 líneas)

| Paquete | Versión | Estado | Notas |
|---|---|---|---|
| requests | 2.32.3 | Fijada | HTTP |
| beautifulsoup4 | 4.12.3 | Fijada | Parsing HTML |
| selenium | 4.21.0 | Fijada | (no usado en scraper verificado; posible uso en futuro) |
| webdriver-manager | 4.0.2 | Fijada | Selenium helper |
| pandas | >=2.3.3 | No fijada exacta | Riesgo de reproducibilidad |
| numpy | sin versión | Sin fijar | Riesgo |
| scipy | sin versión | Sin fijar | Riesgo |
| statsmodels | sin versión | Sin fijar | Riesgo |
| streamlit | sin versión | Sin fijar | Riesgo |
| matplotlib | sin versión | Sin fijar | Riesgo |
| seaborn | 0.13.2 | Fijada | |
| plotly | 5.22.0 | Fijada | |
| notebook | 7.2.0 | Fijada | |
| openpyxl | 3.1.4 | Fijada | |
| pdfplumber | 0.11.9 | Fijada | |

## Dependencias transitivas
No verificado (`pip freeze` no ejecutado por restricción de auditoría). Recomendación: ejecutar en entorno aislado y registrar en `docs/legacy-audit/generated/requirements.freeze.txt` cuando se autorice.

## Riesgos de licencia
- No hay archivo `LICENSE` en legacy verificado en esta auditoría.
- El README menciona "Uso educativo"; no hay licencia de código fuente explícita registrada.
- Datos de Tecnoempleo: scraping sin autorización explícita documentada; posible riesgo de uso de datos protegidos por términos del portal.
- Datos de DS Salaries y Stack Overflow: mencionados como fuentes; licencias no verificadas.
- No hay archivo que documente la licencia de los notebooks ni de los datos generados por scraping.

## Reutilización legal
- Código de scraping (`extract_tecnoempleo.py`): código propio del fork (modificaciones por Luis El Allali); se puede reutilizar como referencia, pero debe verificarse la licencia del repo original (`HelenDiMo/TinderJob`).
- Dependencias: uso de librerías de código abierto; requieren verificación de licencias individuales (MIT, BSD, Apache, etc.) cuando se copie o adapte código de terceros.
- Datos: los CSV generados por scraping contienen datos de ofertas de trabajo; deben tratarse como datos no confiables y no reutilizarse sin consentimiento o licencias correspondientes.

## Recomendación
- NO reutilizar datos de Tecnoempleo sin verificar derechos de uso.
- Verificar licencia del repo original (`HelenDiMo`) antes de considerar reutilización directa de módulos.
- Fijar versiones exactas de dependencias y registrar `requirements.lock` en SkillMatch.
