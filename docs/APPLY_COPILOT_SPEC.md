# Apply Copilot — especificación del módulo opcional

Estado: stretch goal y separado del core. No empezarlo hasta que CRUD, matching base y seguridad estén estables.

## Objetivo

Reducir la fricción de repetir datos en formularios de candidatura. El candidato abre una página externa, pulsa “Rellenar con SkillMatch”, revisa campos prellenados y realiza manualmente el envío final.

## Principios obligatorios

- El usuario ve y confirma lo que se rellena; campos ambiguos requieren interacción.
- Nunca pulsa el botón final de enviar ni confirma una declaración legal automáticamente.
- No gestiona, extrae ni almacena contraseñas/cookies del portal; no sortea CAPTCHA, rate limits o barreras de acceso.
- No actúa contra términos del sitio. Cada ATS/portal debe revisarse individualmente; retirar el soporte si no hay permiso o seguridad suficiente.
- Minimizar permisos de la extensión y explicar a qué dominios accede.
- No enviar el CV/perfil completo a un LLM para clasificar un campo sencillo. Clasificación de campos preferentemente local/determinista.
- No rellenar preguntas sensibles o declaraciones de elegibilidad por inferencia. Pedir respuesta explícita.
- Registrar localmente un resumen de campos completados sin persistir valores sensibles ni contenido del formulario sin consentimiento.

## Arquitectura propuesta

- Browser Extension Manifest V3, TypeScript.
- `field-detector`: etiqueta, `name`, `id`, type, placeholder, context label.
- `field-classifier`: mapeo determinista de aliases a schema (`email`, `phone`, `portfolio_url`, etc.); scores de confianza y revisión.
- `profile-store`: minimizado y protegido; definir si sincroniza con backend y cómo se autentica.
- `filler`: solo campos permitidos, respeta inputs controlados y eventos requeridos.
- `review-ui`: lista propuesta, fuente del dato, confianza, valores faltantes y confirmación de usuario.
- `site-adapters`: solo portales aprobados; no hardcodear bypasses ni selectores frágiles como única estrategia.
- `application-tracker`: registra estado solo cuando el usuario confirma que envió la candidatura.

## MVP de extensión

1. Página/form fixture local de pruebas (sin cuenta de portal).
2. Campos de nombre, email, teléfono, URL portfolio y texto básico.
3. Detectar inputs, mapear con esquema, rellenar y mostrar un resumen revisable.
4. Pruebas para campos ambiguos, campos ocultos, select, radio, inputs controlados, cambios de DOM, datos faltantes y doble click.
5. Ningún envío automático ni procesamiento de captcha.

## Evaluación

- Exactitud de mapeo por campo/tipo.
- Falsos positivos (campo incorrecto rellenado) y omisiones.
- Porcentaje de campos revisados/corregidos por el usuario.
- Tests de no submit, no credenciales y no filtración cross-user.
- Test manual de accesibilidad y borrado de datos.

## Fuera de alcance

- Aplicación masiva automática.
- Guardar login de terceros.
- Manipular APIs privadas o términos de portal.
- Respuestas autónomas a preguntas de elegibilidad/legal.
