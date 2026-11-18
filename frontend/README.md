# SkillMatch — Frontend

Aplicación web de SkillMatch, construida con React, TypeScript y Vite.

## Requisitos

- Node.js
- npm

---

## Instalación

Desde este directorio (frontend/):

```bash
npm ci
```

Este comando instala las dependencias utilizando las versiones fijadas en package-lock.json.

>> Nota: La carpeta node_modules/ no se incluye en el repositorio porque contiene dependencias descargadas automáticamente. Se genera localmente al instalar el proyecto.

---

## Configuración del entorno

Crear un archivo .env.local a partir de .env.example:

```bash
VITE_API_URL=http://localhost:8000
```

Esta variable indica la URL del backend.

Los archivos .env.local no deben subirse a GitHub.

---

## Desarrollo

```bash
npm run dev
```

---

## Comprobaciones

```bash
npm run lint
npm test
npm run build
```

Para comprobar los tipos de TypeScript:

```bash
npx tsc -b
```

---

## Generación de tipos API

Los tipos TypeScript se generan a partir del contrato OpenAPI del backend:

```bash
npm run api:types
```

El resultado se guarda en src/api/schema.d.ts.

El cliente HTTP se encuentra en src/api/client.ts y utiliza la API nativa fetch del navegador.

El contrato OpenAPI se encuentra en ../backend/openapi.json.

---

## Estructura

```bash
## Estructura del proyecto

```text
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts          # Cliente HTTP tipado
│   │   ├── client.test.ts     # Pruebas del cliente API
│   │   └── schema.d.ts        # Tipos generados desde OpenAPI
│   ├── App.test.tsx           # Pruebas del componente principal
│   ├── App.tsx                # Componente principal
│   ├── index.css              # Estilos globales
│   └── main.tsx               # Punto de entrada
├── .env.example               # Plantilla de variables de entorno
├── .gitignore                 # Archivos excluidos de Git
├── eslint.config.js           # Configuración de ESLint
├── index.html                 # Documento HTML principal
├── package.json               # Dependencias y scripts
├── package-lock.json          # Versiones bloqueadas
├── README.md                  # Documentación del frontend
├── tsconfig.json              # Configuración principal de TypeScript
├── tsconfig.app.json          # Configuración TypeScript de la aplicación
├── tsconfig.node.json         # Configuración TypeScript de Node
└── vite.config.ts             # Configuración de Vite y Vitest
```

---

## Cliente API

Los tipos TypeScript de la API se generan a partir del contrato OpenAPI del backend. La comunicación HTTP utilizará la API nativa fetch del navegador.

>> Consulta el contrato en ../backend/openapi.json