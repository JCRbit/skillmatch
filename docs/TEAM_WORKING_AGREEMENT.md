# Acuerdo de equipo y reparto inicial

Equipo conocido: Juan Manuel, Vanessa, Isabela, Luis y Javier (“Javi”). El reparto técnico es **provisional** porque no se ha documentado aún la especialización de cada persona. En el kickoff se ajusta por experiencia/disponibilidad, pero los roles PO/SM quedan fijados como se indica.

## Roles

### Vanessa — Product Owner (PO)

- Custodia problema, alcance, orden de backlog y criterios de aceptación.
- Decide prioridades funcionales, acepta/rechaza historias y resuelve trade-offs de producto.
- Aprueba la salida de auditoría legacy, el alcance de reutilización, el nombre provisional/definitivo y los cortes de MVP.
- Mantiene un registro de decisiones de producto y protege el objetivo; nuevas ideas se anotan y priorizan, no se incorporan automáticamente a mitad de sprint.
- No es responsable única de implementación ni de cumplir todos los acuerdos por sí sola.

### Javier (“Javi”) — Scrum Master (SM)

- Facilita planning, refinamiento, daily/check-in, review y retrospectiva.
- Hace visibles bloqueos, dependencias y riesgos; protege foco del sprint.
- Asegura que las historias tengan criterios de aceptación y que el equipo registre pruebas y acuerdos.
- Facilita que los agentes trabajen con scope y sin pisarse entre sí.
- No decide unilateralmente prioridad de producto ni sustituye al PO.
- También contribuye a tareas técnicas acordadas; SM no equivale a “solo reuniones”.

### Juan Manuel — propuesta inicial: datos y auditoría legacy

- Coordinar inventario de pipeline, fuentes, notebooks, limpieza y calidad de datos.
- Mantener registro de fuentes, derechos, actualizaciones y deduplicación.
- Ayudar con fixtures y pruebas reproducibles de ingestion.

### Isabela — propuesta inicial: frontend y flujos de usuario

- Mapear journeys candidato/empresa, formularios, vistas ciegas y dashboard.
- Definir componentes/UI y tests de flujo con criterios de aceptación del PO.
- Colaborar en accesibilidad y pruebas de usabilidad.

### Luis — propuesta inicial: backend, persistencia e integración

- Proponer/implementar API, modelo relacional, migraciones, permisos y contratos.
- Mantener servicios locales, CI y documentación de ejecución conjuntamente con el equipo.
- Integrar matching/RAG con revisión cruzada.

### Tareas compartidas

- Matching, evaluación, gobernanza, tests, documentación y demo final no pertenecen a una única persona; debe haber pairing/revisión cruzada.
- Reasignar tras una sesión de capacidad: las personas son responsables de entregar juntos, no dueños exclusivos de subsistemas.

## Cadencia sugerida

- Inicio del sprint: objetivo único, issues estimados, acceptance criteria, riesgo y dueño.
- Check-in diario breve: progreso, siguiente paso, bloqueo (facilitado por Javi).
- Dos sesiones stakeholder por semana según guía del programa; documentar feedback del técnico/transversal.
- Review al final de sprint con demo ejecutable y evidencia de requisitos; Vanessa acepta contra criterios.
- Retro: una mejora concreta de proceso por sprint.

## Acuerdos de trabajo con agentes

- Toda tarea de agente referencia un issue y requisito.
- Una persona humana es dueña del diff y de la revisión final.
- No se aceptan cambios “mágicos” sin explicaciones, pruebas o registro de decisión.
- No subir CVs, credenciales, datasets personales ni capturas de formularios privados.
- El PO aprueba prioridades; el SM facilita flujo; el equipo entero comparte calidad y resultado.
