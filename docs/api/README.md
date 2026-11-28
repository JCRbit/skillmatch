# Contrato de la API v1 — congelado

Estado: `FROZEN` · Versión del contrato: **v1** · Issue: `C-01` (#45) · Responsable: Luis · Revisor: Isabela

Esta carpeta publica el contrato HTTP de SkillMatch para quien lo consume: el frontend, el backend
y cualquier cliente que se genere a partir de él. Mientras el contrato está congelado, el documento
es la fuente de verdad, no el código: si los dos discrepan, falla la CI.

## Contenido

| Archivo | Qué es |
|---|---|
| [`openapi-v1.json`](openapi-v1.json) | El documento OpenAPI 3.1 de la API v1, publicado. |
| [`examples/operations.json`](examples/operations.json) | Un ejemplo de petición y respuesta por operación, generado desde el documento. Sirve de mock. |
| `README.md` | Este documento: la política de freeze y cómo se cambia el contrato. |

Los tres artefactos se generan, no se escriben a mano:

```bash
# desde backend/
uv run python scripts/export_openapi.py              # regenera backend/openapi.json
cp openapi.json ../docs/api/openapi-v1.json          # publica el documento
uv run python scripts/generate_contract_examples.py  # regenera los ejemplos
```

## Política de freeze

**Tras el freeze, el contrato solo cambia por un PR aprobado por la PO (Vanessa) y por quien
consume el contrato.** Ese es el criterio de aceptación de `C-01` y la razón de que el documento
viva en el repositorio y no en la cabeza de nadie.

Qué se considera cambio compatible, y por tanto puede entrar con un PR normal:

- un endpoint nuevo;
- un código de respuesta nuevo;
- un campo **opcional** nuevo en una petición o en una respuesta;
- un campo que deja de ser obligatorio;
- un valor nuevo en un enum de salida (nunca en uno de entrada).

Qué es un **cambio incompatible** (`breaking`) y no puede entrar en la v1:

- quitar o renombrar un endpoint, un método o un campo;
- quitar un código de respuesta documentado;
- hacer obligatorio un campo que antes era opcional;
- quitar un valor de un enum;
- cambiar el tipo de un campo, o dejar de admitir `null` donde se admitía;
- cambiar el esquema al que apunta un campo;
- quitar el requisito de autenticación de una operación.

Un cambio incompatible se publica como **v2**, con su propio prefijo `/api/v2`, su propio
`openapi-v2.json` y su propio PR aprobado. La v1 se mantiene mientras haya un consumidor: retirarla
es una decisión de producto, no una consecuencia de haber añadido la v2.

## Cómo se comprueba en CI

El job `Contract · compatibilidad` ejecuta, desde `backend/`:

```bash
uv run python scripts/export_openapi.py --check              # openapi.json no está obsoleto
uv run python scripts/check_contract_compatibility.py        # el generado no rompe lo publicado
uv run python scripts/generate_contract_examples.py --check   # los ejemplos siguen al día
```

El primero detecta que alguien cambió un endpoint sin regenerar el documento. El segundo compara
el documento publicado con el que produce el código y falla si algo se ha estrechado; es el que
convierte "hay que aprobarlo" en algo que no depende de que alguien se acuerde. El tercero evita
que los mocks se queden atrás.

Cuando el check falla por un cambio incompatible, hay dos salidas legítimas: revertirlo, o abrir
la v2 con la aprobación de la PO y de quien consume el contrato.

## Cobertura actual

El contrato publicado recoge lo que el sprint B ha entregado: identidad y autenticación, perfil de
candidato con preferencias, visibilidad, skills y consentimientos granulares, la proyección
seudonimizada que lee una empresa, y el CRUD de empresa y vacantes.

Las operaciones del flujo de **interés y match mutuo** (`B-07`, #49) todavía no existen: su código
no está en `main`, así que no pueden congelarse. Cuando `B-07` se mergee, se regenera el documento
y esas rutas entran en la v1 con su PR, que es exactamente el procedimiento que describe este
documento. Este hueco es consciente y está registrado en la issue `C-01`.
