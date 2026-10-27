# Definition of Done

Un issue no está terminado hasta que:

- [ ] Cumple criterios de aceptación verificables.
- [ ] Trazabilidad a requisitos actualizada.
- [ ] Tests adecuados añadidos/actualizados; comandos y resultados reportados.
- [ ] Lint/typecheck/build relevantes sin error o excepción documentada.
- [ ] Revisión de permisos, privacidad, datos externos, secretos y errores.
- [ ] Migraciones revisadas y testadas si cambia DB.
- [ ] No se introdujeron dependencias sin justificación/versión/aviso de licencia.
- [ ] Documentación y ADR actualizados si el comportamiento/arquitectura cambia.
- [ ] Diff limitado y limpio; sin datos reales, secrets, notebooks outputs voluminosos ni archivos temporales.
- [ ] Reviewer humano aprobó. Agente no mergea/despliega por su cuenta.
- [ ] Demo/feature flags/fallback definidos cuando aplica.

Para componentes AI además:
- [ ] Dataset/corpus y versión registrados.
- [ ] Tests de grounding, prompt injection, fugas cross-user y salida no sustentada.
- [ ] Explicabilidad/fuentes y fallback revisados.
- [ ] Métricas y limitaciones anotadas; no confundir score con probabilidad.
- [ ] Supervisión humana y punto de override probados.
