# Entregable 4 — Auditoría de seguridad y privacidad

Estado: Completo (inspección estática; no se encontraron secretos visibles en archivos leídos; no se ejecutaron scripts con efectos externos)

## Secretos y credenciales
- No se encontraron archivos `.env`, `.env.local`, `secrets/`, ni referencias a tokens/API keys en archivos leídos (`README.md`, `requirements.txt`, `extract_tecnoempleo.py`, `clean_tecnoempleo_data.py`).
- `HEADERS` en scraper usa User-Agent fijo; no es secreto.
- No hay archivo de configuración de API de GitHub ni de OpenAI en legacy.

## Datos personales y archivos (CV, datos de candidatos)
- El README menciona subida de CVs en PDF/texto plano para el módulo TinderMatch; no hay archivos de CV en directorio `data/` verificado.
- No hay sistema de autenticación ni roles (no hay `auth/`, no hay base de datos).
- Datos de Tecnoempleo contienen información de empresas, ubicaciones, salarios y ofertas; pueden incluir datos personales de candidatos indirectamente a través de descripciones; deben tratarse con cuidado.

## Scraping y uso de servicios externos
- Scraper realiza peticiones HTTP directas a `tecnoempleo.com` con delay de `time.sleep(1)` y `time.sleep(0.4)`. No es agresivo, pero es scraping sin autorización documentada.
- No se verificaron términos de uso de Tecnoempleo.
- No hay mecanismo de reintento ni manejo de bloqueos (solo `break` por código de error).

## Riesgos de ejecución de código
- `extract_tecnoempleo.py`: usa `BeautifulSoup` sobre HTML recibido; no hay deserialización insegura (no usa `pickle`, `yaml.load`, `eval`). Riesgo bajo.
- `clean_tecnoempleo_data.py`: usa `re` y `pandas`; no hay ejecución dinámica de strings. Riesgo bajo.
- No hay archivos `.py` con `subprocess`, `os.system` verificados.

## Protección frente a prompt injection
- No aplica directamente al legacy (no hay LLM ni RAG); pero si se reutiliza código para un sistema con LLM, debe implementarse defensa contra instrucciones maliciosas en datos recuperados (CVs, ofertas, repositorios).

## Privacidad y GDPR
- El legacy no implementa consentimiento, minimización ni derecho de supresión.
- No hay registro de decisiones ni auditoría de datos.
- No hay mecanismo de anonimización temprana (blind hiring).

## Recomendaciones de seguridad (para SkillMatch, no para modificar legacy)
- No ejecutar el scraper sin autorización explícita y sin verificar términos del portal.
- No incluir datos reales de candidatos en tests o repositorios.
- Implementar autenticación y autorización en API (FastAPI) desde el inicio.
- Separar datos identificativos de datos de competencias; implementar blind hiring.
- Usar datos sintéticos para pruebas y demos.
- Registrar audit logs sin datos personales innecesarios.
