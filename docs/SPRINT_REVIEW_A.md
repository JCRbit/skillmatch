@'
# [V-01] Sprint Review A — Preparación y Acta (`M1 · Esqueleto andante`)

## 1. Propósito y alcance de la sesión

- **Hito:** `M1 · Esqueleto andante`
- **Duración prevista:** 30–45 minutos por bloque de revisión
- **Asistencia:** Equipo completo de SkillMatch junto con los *stakeholders* de **Eraneos** (técnico, transversal y apoyo)
- **Objetivo:** Presentar el esqueleto funcional del sistema, contrastar la arquitectura, el enfoque ético/transversal y la organización del equipo frente a los límites honestos de `M1`, y volcar el feedback recibido al backlog antes de avanzar hacia `M2 · Demo v1 del flujo completo`.

---

## 2. Calendario oficial de seguimiento con Stakeholders (Eraneos)

Las revisiones y seguimientos se organizan en **tres líneas diferenciadas**:

| Línea de seguimiento | Stakeholder (Eraneos) | Contacto | Franja horaria | Sesiones registradas (`M1` / arranque) | Próximas sesiones previstas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Técnico** | **Jesús Parra** | `jesus.parra@eraneos.com` | 09:30 – 10:30 | S1: `03/11/2026`<br>S2: `10/11/2026`<br>S3: `17/11/2026`<br>S4: `23/11/2026` | S5: `30/11/2026`<br>S6: `07/12/2026` *(si es necesario)* |
| **2. Transversal** | **Teresa Morón** | `teresa.moron@eraneos.com` | 13:30 – 14:30 | S1: `03/11/2026`<br>S2: `10/11/2026`<br>S3: `17/11/2026`<br>S4: `24/11/2026` | S5: `01/12/2026`<br>S6: `07/12/2026` *(si es necesario)* |
| **3. Apoyo** | **Adriana Narváez** | `adriana.narvaez@eraneos.com` | 09:00 – 10:00 | S1: `03/11/2026`<br>S2: `10/11/2026`<br>S3: `17/11/2026`<br>S4: `24/11/2026` | S5: `01/12/2026` *(figura como `01NOV26` en calendario original)* |

---

## 3. Preparación y guion común de la demo (`M1 · Esqueleto andante`)

### Qué se presenta en `M1`
1. **Bloque Técnico (Jesús Parra):** Estructura del repositorio (`backend` + `frontend`), modelo de datos inicial, contratos OpenAPI, autenticación/rutas protegidas y validaciones/checks de calidad. Organización del equipo, roles/RACI, ritmo de entrega por hitos (`M1` → `M4`), gestión de bloqueos y seguimiento de avances.
2. **Bloque Transversal (Teresa Morón):** Problema y propuesta de valor, narrativa `v0`, separación estricta entre requisitos esenciales, deseables y condiciones objetivas, privacidad por diseño y gobernanza IA (`GDPR` / `EU AI Act`).
3. **Bloque de Apoyo (Adriana Narváez):** Apoyo a las sesiones de Jesús Parra y Teresa Morón, y soporte para la posterior presentación del proyecto en nuestros portfolios.

### Límites honestos declarados en `M1`
- Se muestra un **esqueleto andante** y la base arquitectónica/documental, no el flujo completo extremo a extremo ni el motor definitivo de *matching* y evaluación de evidencia.

### Guion tipo por sesión (35–40 minutos)

| Tramo | Duración | Contenido |
| :--- | :--- | :--- |
| **1. Contexto y alcance de `M1`** | 5 min | Objetivo del hito, avances desde la sesión anterior y límites honestos actuales. |
| **2. Demo / revisión focalizada** | 15 min | Muestra práctica adaptada al foco del stakeholder (técnico, transversal o apoyo). |
| **3. Feedback y preguntas** | 12 min | Observaciones, riesgos detectados y recomendaciones del stakeholder. |
| **4. Acuerdos y vuelco al backlog** | 5–8 min | Priorización (`MUST` / `SHOULD`) y registro en el backlog / siguiente planning (`[G-04]`). |

---

## 4. Actas por Stakeholder (`M1 · Esqueleto andante`)

### 4.1. Bloque 1 — Stakeholder Técnico: Jesús Parra (`jesus.parra@eraneos.com`)

- **Fechas de revisión `M1`:** `03/11/2026` (S1) · `10/11/2026` (S2) · `17/11/2026` (S3)
- **Franja:** 09:30 – 10:30
- **Asistentes:** Equipo SkillMatch + Jesús Parra (Eraneos)
- **Temas revisados en la demo técnica:**
  - Arquitectura base del esqueleto (`backend` y `frontend`), contratos de API y autenticación/autorización por rol (`talento` / `empresa`).
  - Definición completa del proyecto, marcar hitos esenciales (`MUST`) y documentación del proyecto.
- **Acuerdos y feedback técnico volcado al backlog:**

| ID | Feedback / Observación técnica | Prioridad | Acción / Issue en backlog | Responsable | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TEC-01` | Se replantea el proyecto | MUST | Redefinición de alcance e hitos `M1` (*Esqueleto andante*) en backlog | Equipo SkillMatch | En curso |

---

### 4.2. Bloque 2 — Stakeholder Transversal: Teresa Morón (`teresa.moron@eraneos.com`)

- **Fechas de revisión `M1`:** `03/11/2026` (S1) · `10/11/2026` (S2) · `17/11/2026` (S3)
- **Franja:** 13:30 – 14:30
- **Asistentes:** Equipo SkillMatch + Teresa Morón (Eraneos)
- **Temas revisados en la demo transversal:**
  - Claridad del problema y propuesta de valor, enfoque junior, explicabilidad sin caja negra y límites éticos/legales (`GDPR` / `EU AI Act`).
  - Revisamos con Teresa el nuevo enfoque del proyecto y validamos la viabilidad de la nueva dirección.
- **Acuerdos y feedback transversal volcado al backlog:**

| ID | Feedback / Observación transversal | Prioridad | Acción / Issue en backlog | Responsable | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TRV-01` | Se emplaza a próximas reuniones debido al cambio de dirección del proyecto | MUST | Ajuste de narrativa `v0` y alcance de `M1` (*Esqueleto andante*) | Equipo SkillMatch | En curso |

---

### 4.3. Bloque 3 — Stakeholder de Apoyo: Adriana Narváez (`adriana.narvaez@eraneos.com`)

- **Fechas de revisión `M1`:** `03/11/2026` (S1) · `10/11/2026` (S2) · `17/11/2026` (S3)
- **Franja:** 09:00 – 10:00
- **Asistentes:** Equipo SkillMatch + Adriana Narváez (Eraneos)
- **Temas revisados en el seguimiento de apoyo:**
  - Dinámica del equipo, organización por hitos (`M1` → `M4`), gestión de dependencias y seguimiento de avances.
  - Concretamos que la dirección correcta de estas sesiones será dar soporte a las otras partes del proyecto y apoyo en la parte emocional del mismo, revisando semanalmente la estabilidad del proyecto y los posibles inconvenientes.
- **Acuerdos y acciones de seguimiento:**

| ID | Observación / Punto de apoyo | Prioridad | Acción acordada en equipo / backlog | Responsable | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `APO-01` | Aparte del soporte al proyecto, nos reforzará la parte de exposición y gestión en nuestros portfolios | SHOULD | Seguimiento semanal de estabilidad, bloqueos y preparación de portfolio (`[G-04]`) | Equipo SkillMatch | En curso |

---

## 5. Síntesis de cierre de `M1` y paso a `M2`

- Todos los hallazgos de las tres líneas de *stakeholders* (**Jesús Parra**, **Teresa Morón** y **Adriana Narváez**) quedan consolidados para alimentar **`[G-04]` (`Sprint Planning B`)** y orientar el alcance de **`M2 · Demo v1 del flujo completo`**.
'@ | Set-Content -Path "docs/SPRINT_REVIEW_A.md" -Encoding UTF8

git status
git add docs/SPRINT_REVIEW_A.md
git commit -m "docs(V-01): add Sprint Review A preparation and stakeholder minutes"
git push -u origin docs/V-01-sprint-review-a