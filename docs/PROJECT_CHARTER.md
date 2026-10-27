# Project charter

## Identidad

- **Codename provisional:** SkillMatch.
- **Nombre de producto y repositorio definitivo:** pendiente de decisión de Vanessa (PO).
- **Producto:** plataforma bidireccional de matching de talento junior y empresas basada en competencias demostrables.
- **Horizonte:** proyecto de 6 semanas, 2 nov.–11 dic. 2026.
- **Repositorio legacy:** `https://github.com/luiselallali18-hub/TinderJob_Fork` — fuente de auditoría, no destino de desarrollo.
- **Estado:** fase 0, auditoría de legacy; arquitectura propuesta, no implementada.

## Problema

Los procesos de empleo junior suelen filtrar por títulos y años de experiencia e ignoran proyectos y habilidades demostrables. Candidatos y empresas deben descubrir compatibilidad, comprender por qué existe y solo poder contactar cuando haya interés mutuo.

## Objetivo

Construir una prueba de concepto demostrable donde perfiles junior y empresas tengan CRUD, las ofertas y proyectos se normalicen, el matching semántico sea explicable, el interés sea bidireccional, exista un asistente de preparación de entrevistas y las vistas iniciales puedan anonimizar identificadores.

## Usuarios y roles del producto

- Candidate: gestiona perfil, CV, proyectos/skills, preferencias, interés y candidaturas.
- Company member: administra empresa/ofertas, consulta perfiles anonimizados autorizados y expresa interés.
- Admin/operator: opera ingestión, atiende incidencias y revisa auditoría; acceso excepcional controlado.
- AI services: proponen análisis/explicaciones, no toman decisiones finales de empleo ni hacen acciones irreversibles.

## Principios no negociables

1. Competencias y evidencia antes que títulos/años.
2. Matching explicable, con incertidumbre y evidencia visible.
3. Interés mutuo antes de desbloquear datos de contacto.
4. Anonimización temprana con limitaciones documentadas.
5. La IA ayuda a personas; no decide contratación por sí sola.
6. Privacidad desde el diseño: minimización, propósito, retención, acceso y borrado.
7. Trazabilidad reproducible de fuentes, versiones de modelos/prompt, resultados y overrides humanos.
8. Integridad técnica: modularidad, pruebas, CI y documentación.
9. Separación de proyecto legacy y producto nuevo.

## Éxito y métricas

- Flujos CRUD completos para candidato y empresa.
- Oferta importada con fuente, fecha de adquisición, fecha de actualización y enlace original.
- Matching devuelve motivos rastreables (skills/evidencias/requisitos), no solo score.
- El contacto solo se desbloquea cuando ambas partes han expresado interés.
- CV/PDF y datos de repositorios se extraen con errores detectables y trazabilidad de fuente.
- Asistente responde con referencias a oferta/empresa autorizadas y reconoce cuando no sabe.
- Pipeline reproducible; CI ejecuta calidad y tests.
- Objetivo pedagógico del documento original: reducir 60% el tiempo de cribado inicial. Tratarlo como **hipótesis a medir**, no como resultado garantizado; diseñar estudio de tiempo base vs. prototipo.
- Target de latencia documentado en requisitos: p95 <300 ms para búsqueda vectorial en conjunto de pruebas definido; separar latencia de retrieval de parsing, embeddings y generación LLM remota.

## Alcance MVP

Incluido: auth/roles, CRUD, ingestión limitada/ética de ofertas, parsing básico de CV, GitHub API con consentimiento y rate limits, PostgreSQL, Qdrant, matching baseline explicable, interés mutuo, vista ciega, auditoría de acciones, RAG acotado, sugerencias de perfil/carta, dashboard mínimo, tests/CI/Docker y evaluación ética/documentación.

Posterior/condicionado: ranking supervisado solo si hay dataset etiquetado válido; extensión Apply Copilot en 1–2 formularios controlados como objetivo stretch; múltiples agentes autónomos, microservicios, Kafka, Spark, mobile app y scraping a gran escala fuera del MVP.

## Fuera de alcance

- Decisión automática de contratación/rechazo.
- Automatizar envío masivo de candidaturas o operar cuentas externas por el usuario.
- Eludir captchas, términos de portales o controles de acceso.
- Entrenar con CVs reales sin base jurídica, consentimiento y gobernanza adecuados.
- Prometer cumplimiento normativo sin evaluación legal competente.

## Restricciones y supuestos

- 6 semanas y recursos limitados: priorizar demo robusta y alcance honesto, no una arquitectura distribuida prematura.
- La calidad de legacy, derechos sobre datos y estado real del código permanecen `UNKNOWN` hasta la auditoría.
- Deben confirmarse acceso al fork, licencia, fuentes autorizadas, alojamiento y política de datos.
