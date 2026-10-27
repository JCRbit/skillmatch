# ADR-0001 — Separar el producto nuevo de legacy

- Estado: **Propuesto; PO debe aprobar**
- Fecha: 2026-10-27
- Owner: Vanessa (PO); Javi (SM) facilita

## Contexto

El repositorio existente parece centrarse en scraper, análisis y dashboard. La nueva plataforma tiene necesidades de API, roles, persistencia, matching, privacidad, trazabilidad y posible extensión. Mezclarlo en la misma raíz facilitaría imports accidentales, dependencias conflictivas y confusión sobre qué producto se ejecuta.

## Decisión propuesta

Mantener el fork existente como fuente legacy de solo lectura y crear un repositorio nuevo. Auditar primero y registrar cada transferencia de código/datos con estado, evidencia y licencia. Extraer módulos seleccionados tras aprobación; no copiar todo el árbol ni heredar la historia completa por defecto.

## Consecuencias

- Historia, dependencias, CI y documentación limpias para el producto nuevo.
- Es necesario mantener una referencia al commit legacy y las licencias de código/datos.
- Cualquier copia aprobada debe preservar avisos de copyright/licencia y pruebas de procedencia.
- El pipeline de datos existente puede servir como fuente, pero su reutilización no está confirmada hasta auditarlo.
