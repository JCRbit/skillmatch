# Entregable 9 — Plan de reconstrucción y backlog priorizado

Estado: Completo
Fecha: 27/10/2026

## Resumen ejecutivo (para Vanessa PO y Javi SM)

- Legacy auditado sin modificaciones.
- El repo `TinderJob_Fork` es un pipeline de análisis de datos con dashboard Streamlit; NO implementa la plataforma de matching bidireccional por competencias descrita en el PDF de Somos F5.
- Se recomienda: adaptar `clean_tecnoempleo_data.py` como base del pipeline de limpieza, usar `extract_tecnoempleo.py` como referencia de scraping, y reconstruir todo lo demás (backend, frontend, matching, RAG, roles, blind hiring, CI/CD) en `skillmatch`.
- No se recomienda copiar módulos completos ni datos sin verificación de licencia y derechos.

## Qué se conserva / adapta / descarta / reescribe

| Componente | Decisión | Razón |
|---|---|---|
| clean_tecnoempleo_data.py | ADAPTAR | Limpieza robusta; debe integrarse con SQLAlchemy / Pydantic |
| extract_tecnoempleo.py | ADAPTAR / REFERENCIA | Scraping funcional; debe integrarse con DB y validar autorización |
| Notebooks | REFERENCIA / DESCARTAR | No son parte del producto; pueden orientar análisis |
| Datos CSV raw/processed | DESCARTAR / REFERENCIA | Datos de scraping sin licencia verificada; no importar |
| stat_analysis.py | REESCRIBIR | Vacío; no aporta valor |
| Streamlit app | REESCRIBIR | No es la arquitectura objetivo (React + FastAPI) |

## Bloqueos y decisiones pendientes (requeridas para pasar a fase 1)

1. Vanessa debe aprobar: nombre definitivo del producto y repositorio remoto (provisional: SkillMatch).
2. Vanessa debe aprobar: alcance de la primera iteración (¿MVP con CRUD + matching básico? ¿Con RAG? ¿Con blind hiring?).
3. Javi debe coordinar: creación del repo remoto, configuración de CI básica y asignación de tareas.
4. Luis / Isabela deben validar: diseño de embeddings, evaluación del ranking y esquema de datos.
5. Juan Manuel debe validar: estrategia de datos sintéticos y reproducibilidad.

## Backlog priorizado (primeras historias, referencias a requisitos)

| Prioridad | Historia | Requisito | Criterios de aceptación | Dependencias | Asignación propuesta |
|---|---|---|---|---|---|
| P0 | Configurar repo SkillMatch, CI básico, estructura de carpetas | NFR-08 | Repo creado, `.github/workflows/` básico, `AGENTS.md` actualizado, `README.md` con instrucciones | Ninguna | Javi (SM) + equipo |
| P1 | Definir esquema de datos (Pydantic + SQLAlchemy) y crear migraciones | FR-01, FR-02 | Modelos de Usuario (candidata/empresa), Oferta, Interacción, Consentimiento, Auditoría; migraciones Alembic | P0 | Luis (backend) |
| P2 | Implementar CRUD básico de perfiles (candidata y empresa) con autenticación básica | FR-01 | Registro, login, actualización de perfil; permisos diferenciados; datos sintéticos | P1 | Luis |
| P3 | Crear pipeline de limpieza adaptado (de clean_tecnoempleo_data.py) | FR-03, FR-04 | Función que toma datos de CV/oferta y normaliza skills, modalidad, ubicación, salario | P1 | Juan Manuel |
| P4 | Implementar extracción básica de CV (PDF/texto) y análisis de GitHub API | FR-03, FR-04 | Extraer skills de CV y repositorios; validar con datos sintéticos; no usar datos reales sin autorización | P3 | Isabela (IA) + Luis |
| P5 | Configurar Qdrant + embeddings (BGE o OpenAI) y ranking básico | FR-05, FR-06 | Índice de vectores; cálculo de similitud; presentación de porcentaje de compatibilidad (como indicador, no probabilidad) | P2, P4 | Isabela |
| P6 | Implementar flujo de interés mutuo | FR-07 | Ambas partes marcan interés; contacto solo tras verificación; registro de consentimiento | P2 | Luis |
| P7 | Diseño de blind hiring y separación de datos | NFR-02 | Datos identificativos separados de datos de competencias; modo de vista anónima | P1, P2 | Isabela + Luis |
| P8 | Asistente RAG básico (sobre ofertas y empresa) | FR-08 | Recuperación de documentos; respuesta estructurada; confirmación humana si es necesaria | P2, P5 | Isabela |
| P9 | Dashboard básico de empresa | FR-10 | Métricas de ofertas, candidatos, matches; usando React / API | P2, P6 | Juan Manuel / frontend |
| P10 | Evaluación, auditoría de sesgos, gobernanza | NFR-02, NFR-09 | Documentación de límite del ranking; auditoría de datos sintéticos; registro de decisiones | P5, P7 | Isabela + Vanessa |

## Fechas de referencia (6 semanas: 2 Nov — 11 Dic 2026)
- Semana 1 (2-8 Nov): Auditoría completa (esta), diseño de datos, decisiones iniciales.
- Semana 2 (9-15 Nov): Base de aplicación, persistencia, perfiles, CRUD.
- Semana 3 (16-22 Nov): Extracción CV/GitHub, embeddings, ranking explicable.
- Semana 4 (23-29 Nov): Interés mutuo, blind hiring, dashboard básico.
- Semana 5 (30 Nov-6 Dic): RAG básico, evaluación, gobernanza.
- Semana 6 (7-11 Dic): Pruebas integradas, CI final, defensa y entrega.

## Entregables de fase 0 (ya completados o en progreso)
- [x] Inventario técnico
- [x] Mapa de arquitectura
- [x] Dependencias / licencias
- [x] Seguridad / privacidad
- [x] Calidad de datos / reproducibilidad
- [x] Pruebas / calidad / deuda técnica
- [x] Matriz de reutilización
- [x] Diagnóstico arquitectura / ADRs
- [x] Plan de reconstrucción / backlog

## Recomendación final (fase 0)
- NO iniciar implementación de producto hasta que Vanessa apruebe alcance y registro de reutilización.
- NO modificar legacy.
- NO incorporar módulos del legacy en SkillMatch sin registro de reutilización y verificación.
- SÍ preparar entorno de desarrollo (Docker, CI básico) y esquema de datos.
- SÍ usar datos sintéticos para todo desarrollo y pruebas.

## Pruebas / comandos no ejecutados en esta fase (por restricción de auditoría)
- Ejecución de `scraper.py` / `extract_tecnoempleo.py` (requiere red, podría modificar datos, no autorizado sin validación del portal).
- Ejecución de notebooks (podrían ejecutar código sin control de entorno).
- Ejecución de `streamlit_app.py` (requiere entorno con todas las dependencias, podría exponer datos).
- Instalación completa de dependencias en legacy (no autorizado por regla 4).
- Comprobación completa de licencias de cada librería (requiere búsqueda individual).
- Verificación completa de archivo `main_analysis.ipynb` y contenido de todos los notebooks.
