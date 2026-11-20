# Project charter

## Identidad

- **Codename del proyecto:** SkillMatch (aprobado para desarrollo interno y defensa del proyecto formativo; sujeto a `PRODUCT_NAME_DECISION.md` antes de cualquier publicación comercial externa).
- **Producto:** plataforma bidireccional de matching de talento tecnológico junior y empresas basada en competencias demostrables y evidencias verificables.
- **Horizonte:** proyecto de 6 semanas, 2 nov.–11 dic. 2026 (Feature freeze: 7 dic.; Estabilización: 8–9 dic.; Demo y defensa: 10–11 dic. 2026 — `D-10`).
- **Repositorio legacy:** `https://github.com/luiselallali18-hub/TinderJob_Fork` — fuente histórica de solo lectura, auditoría cerrada (`M0`); no es destino de desarrollo.
- **Estado:** **Alcance MVP aprobado (`M0` cerrado)**; desarrollo activo sobre arquitectura modular (`FastAPI` + `PostgreSQL` + `React/TypeScript`).

## Problema

Los procesos de empleo junior suelen filtrar por títulos y años de experiencia previa, ignorando proyectos reales y habilidades demostrables. Candidatos y empresas necesitan descubrir compatibilidad explicable por requisito y desbloquear el contacto únicamente tras interés mutuo verificado.

## Objetivo

Construir una aplicación web demostrable donde perfiles junior (arquetipos Backend, Frontend y QA Automation) y empresas dispongan de CRUD protegido, las habilidades se normalicen contra un catálogo local curado con referencia ESCO, el matching híbrido explique cada requisito con evidencia y carencias, la vista inicial proteja la privacidad mediante seudonimización, exista un asistente de preparación de entrevistas con supervisión humana y el contacto se revele solo ante interés mutuo.

## Usuarios y roles del producto

- **Candidate:** gestiona perfil, declaración de skills, un proyecto manual (y conector GitHub opcional), revisión/confirmación de evidencias, visibilidad/consentimiento, descubrimiento de vacantes e interés bidireccional.
- **Company member:** administra empresa y vacantes mediante formulario estructurado, descubre perfiles seudonimizados autorizados, revisa fichas de encaje y expresa interés.
- **Admin/operator:** supervisa operación, datos semilla sintéticos y auditoría; acceso excepcional controlado.
- **AI services:** asisten en extracción de evidencias, señal semántica auxiliar, chat RAG acotado a documentos de oferta/empresa autorizados y preparación de entrevistas; nunca toman decisiones finales de empleo ni realizan acciones irreversibles.

## Principios no negociables

1. Competencias y evidencia confirmada antes que títulos/años.
2. Matching explicable por requisito, con incertidumbre y evidencia visible; sin score global opaco ni porcentaje de contratación.
3. Interés mutuo verificado en servidor antes de desbloquear datos de contacto.
4. Seudonimización temprana (allowlist) en vistas iniciales con limitaciones documentadas.
5. La IA ayuda a personas; no decide contratación por sí sola.
6. Privacidad desde el diseño (GDPR): minimización, propósito, consentimiento granular, acceso y borrado.
7. Trazabilidad reproducible de taxonomía, versiones de reglas/prompts, resultados y overrides humanos.
8. Integridad técnica: modularidad, pruebas, CI y documentación.
9. Separación estricta de proyecto legacy y producto nuevo.

## Éxito y métricas

- Flujos CRUD completos y protegidos por rol (`Candidate`, `Company`, `Admin`).
- Vacantes registradas por formulario estructurado con separación de skills esenciales, deseables, seniority y condiciones objetivas.
- Matching devuelve ficha de encaje por requisito e indicador de **cobertura de evidencia** (numerador/denominador), nunca porcentaje de contratación.
- El contacto solo se desbloquea cuando ambas partes han expresado interés verificado en servidor.
- Proyectos manuales y evidencias revisadas con trazabilidad de fuente y fecha.
- Asistente RAG responde con citas a documentos de oferta/empresa autorizados y reconoce explícitamente cuando no sabe.
- Pipeline reproducible con Docker Compose; CI ejecuta calidad, seguridad y tests.
- **Hipótesis pedagógica (−60 % tiempo de cribado inicial):** tratada explícitamente como **hipótesis experimental** medida sobre datos sintéticos (`[E-06]`), no como resultado garantizado.
- **Rendimiento:** latencia p95 documentada mediante benchmark reproducible en local (`[E-01]`) sobre el índice vectorial embebido.

## Alcance MVP

- **Incluido (`MUST`):** auth/roles, CRUD candidato/empresa/vacante (formulario manual), taxonomía local curada (~80 skills con referencia ESCO) y normalizador, alta manual de proyecto + revisión de evidencias, PostgreSQL canónico + índice vectorial embebido (`[E-01]`), matching híbrido explicable por requisito + cobertura de evidencia, interés mutuo y liberación controlada de contacto, vista seudonimizada por allowlist, consentimiento granular, auditoría de acciones (`audit_log`), plan de 3 siguientes pasos, RAG acotado con citas y refusals, flujo de entrevista en LangGraph con revisión humana, tests/CI/Docker y evaluación ética/gobernanza (GDPR / EU AI Act).
- **Posterior / condicionado (`SHOULD` / `COULD`):** experiencia transversal (`[S-10]`), vista de estado de solicitudes (`[F-11]`), estudio comparativo de cribado (`[E-06]`), prueba de usabilidad (`[E-07]`), conector GitHub read-only opcional (`[S-09]`), experimento de ranker sobre sintéticos etiquetado como demostración (`[E-03]`) y borrador editable de carta (`[A-07]`).
- **Fuera de alcance:** scraping de portales de empleo (`D-05`), parsing automático de CV PDF (`D-04`), Apply Copilot (`FR-020`), portal de centros formativos (`D-11`), publicación de prácticas/becas sin marco legal validado (`D-12`), base vectorial externa (Qdrant) y arquitecturas distribuidas (Kafka, Spark, Kubernetes, microservicios).

## Fuera de alcance (guardrails éticos y legales)

- Decisión automática de contratación/rechazo o descarte por falta de evidencia.
- Automatizar envío masivo de candidaturas o operar cuentas externas por el usuario.
- Eludir captchas, términos de portales o controles de acceso.
- Entrenar con CVs reales sin base jurídica, consentimiento y gobernanza adecuados.
- Prometer cumplimiento normativo sin evaluación legal competente.

## Restricciones y supuestos

- 6 semanas y recursos limitados: priorizar demo robusta y alcance honesto, sin infraestructura distribuida prematura.
- Todos los datos de prueba, perfiles y vacantes de la demo son 100 % sintéticos (`[S-04]`, `[S-08]`).