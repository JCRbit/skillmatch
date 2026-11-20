# Narrativa v0 — SkillMatch (Sesión transversal)

- **Issue:** `[R-03]` (Milestone `M1 · Esqueleto andante`)
- **Owner:** Vanessa García (Product Owner)
- **Estado:** `v0` (base para sesión transversal y evolución hacia el guion de demo v1 en `[R-05]`)
- **Referencias rectoras:** [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) · [`PRODUCT_BACKLOG.md`](PRODUCT_BACKLOG.md) · [`DECISION_LOG.md`](DECISION_LOG.md) · [`AI_GOVERNANCE.md`](AI_GOVERNANCE.md)

---

## 1. El problema: opacidad y filtro por credenciales en el acceso junior

En el mercado tecnológico actual, el primer empleo junior sufre una doble fricción que perjudica tanto a candidatos como a empresas:

1. **Cribado basado en años de experiencia y títulos:** Las ofertas junior suelen descartar talento antes de evaluar competencias demostrables, penalizando perfiles en transición profesional o recién titulados de bootcamps y ciclos formativos que aún no acumulan experiencia laboral formal.
2. **Asimetría de información y contacto prematuro:** Los candidatos desconocen qué evidencias concretas respaldan o debilitan su encaje frente a una vacante, mientras que la exposición temprana de datos identificativos (nombre, correo, enlaces personales) introduce riesgos de privacidad y sesgos inconscientes en el cribado inicial.
3. **Cajas negras algorítmicas:** Muchas herramientas de reclutamiento reducen a las personas a un porcentaje opaco de afinidad sin explicar qué requisito falta, qué evidencia lo sustenta ni cómo cerrar la brecha.

---

## 2. Propuesta de valor: matching bilateral basado en evidencia verificable

**SkillMatch** es una plataforma bidireccional de matching entre talento tecnológico junior (arquetipos **Backend**, **Frontend** y **QA Automation**) y empresas, diseñada bajo cuatro pilares verificables:

1. **Competencias y evidencia antes que credenciales (`D-02`, `D-03`, `US-01`–`US-04`):**
   - Los candidatos declaran sus habilidades normalizadas contra un catálogo local curado (~80 competencias con referencia ESCO) y aportan proyectos propios cuyas señales son **revisadas, confirmadas o retiradas explícitamente por el propio usuario**.
   - El motor híbrido evalúa cada vacante requisito por requisito (esenciales, deseables y condiciones objetivas) y devuelve una **ficha de encaje explicable** junto con un indicador de **cobertura de evidencia** (numerador/denominador) y un **plan accionable de 3 siguientes pasos** (`US-05`).
2. **Privacidad desde el diseño y descubrimiento seudonimizado (`D-09`, `US-08`, `US-15`):**
   - Ningún perfil es público por defecto. En la fase de descubrimiento, las empresas visualizan únicamente una **proyección seudonimizada por lista blanca (*allowlist*)** que oculta nombre, correo, enlaces identificativos y datos de contacto.
3. **Interés mutuo verificado y liberación controlada del contacto (`D-07`, `US-09`, `US-16`, `US-17`):**
   - Expresar interés de forma unilateral nunca desbloquea los datos personales. Solo cuando **ambas partes** han expresado interés verificado en servidor y el candidato autoriza explícitamente la liberación, se abre el canal de contacto y queda registrado en auditoría.
4. **Asistencia de IA acotada y supervisada por personas (`US-07`, `FR-014`, `FR-015`):**
   - La IA generativa se limita a dos apoyos con trazabilidad: un asistente **RAG acotado exclusivamente a la documentación autorizada de la oferta/empresa** (con citas y rechazo explícito cuando no hay contexto) y un **preparador de entrevistas** con revisión humana obligatoria.

---

## 3. Límites honestos y decisiones de alcance del MVP

Para garantizar un producto demostrable, seguro y auditable dentro del horizonte de 6 semanas (`2 nov.–11 dic. 2026`, feature freeze el `7 dic.` — `D-10`), SkillMatch establece explícitamente qué **no hace** y cuáles son sus límites actuales:

- **Sin decisiones automatizadas de contratación ni descarte:** SkillMatch no contrata, no rechaza candidaturas automáticamente ni calcula probabilidades de éxito laboral. Toda decisión final corresponde siempre a personas (`NFR-008`).
- **Sin porcentaje opaco de afinidad:** El sistema nunca muestra un "92 % de match"; expresa el encaje desglosado por requisito y como cobertura de evidencia confirmada (`FR-009`).
- **Sin scraping externo ni análisis automático de CV en PDF (`D-04`, `D-05`):** Las vacantes se registran mediante formulario estructurado de empresa (`US-06`) y las evidencias parten de proyectos aportados y revisados por el candidato (`US-02`, `US-03`), evitando riesgos legales de extracción no autorizada o errores silenciosos de parsing PDF.
- **Sin envío automático de candidaturas (*Apply Copilot* fuera del MVP):** La plataforma nunca opera cuentas externas ni envía solicitudes en nombre del usuario (`FR-020` diferido).
- **Datos 100 % sintéticos en la demostración:** Todos los perfiles, empresas, vacantes y métricas de evaluación (`Gold set`, auditoría de sesgos contrafactuales y prueba comparativa de tiempo de cribado) se ejecutan sobre datos sintéticos controlados; la hipótesis de reducción del 60 % del tiempo de cribado inicial se trata como experimento a medir, nunca como promesa garantizada.
- **Módulos institucionales diferidos (`D-11`, `D-12`):** El portal agregado para centros formativos (`US-12`) y la publicación de prácticas/becas (`US-13`) quedan fuera del MVP a la espera de validación jurídica específica.

---

## 4. Estructura sugerida para la sesión transversal (5–7 minutos)

| Bloque | Duración | Mensaje clave | Evidencia en producto / repo |
|---|---|---|---|
| **1. Problema real** | 1 min | El talento junior queda invisible tras filtros de años/títulos y pierde privacidad antes de saber si hay interés real. | [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) |
| **2. Solución SkillMatch** | 2 min | Matching bilateral por evidencias confirmadas, seudonimización temprana y contacto solo tras interés mutuo. | [`PRODUCT_BACKLOG.md`](PRODUCT_BACKLOG.md) (`US-01`–`US-17`) |
| **3. IA responsable y límites** | 1.5 min | Sin cajas negras ni decisiones autónomas: ficha por requisito, RAG con citas y supervisión humana. | [`DECISION_LOG.md`](DECISION_LOG.md) (`D-01`–`D-10`) |
| **4. Hoja de ruta y estado** | 1 min | Arquitectura modular (`FastAPI` + `PostgreSQL` + `React`), CI verificada y entrega por hitos (`M1`–`M4`). | [`ROADMAP_6_WEEKS.md`](ROADMAP_6_WEEKS.md) · [`CI.md`](CI.md) |