# Proy práctica - Django clásico a una API



El repositorio comienza con dos aplicaciones independientes:

- `backend/`: Django, el modelo `Activity`, SQLite y una vista HTML clásica.
- `frontend/` o `frontend-astro`: Vite + React + TypeScript recién inicializado, todavía sin integración con Django.

## Puesta en marcha local

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_activities
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>.

### 2. Frontend

En otra terminal:

```bash
cd frontend-astro/
pnpm install
pnpm dev
```

Abrir <http://127.0.0.1:4321/>.

## Verificación rápida

```bash
cd backend
python manage.py test

cd ../frontend-astro
pnpm build
```

## Punto de partida didáctico
# Representaciones Web con Astro 

Este proyecto corresponde a la resolución de la Actividad 2 de la materia Arquitectura Web (TUDA 2026). El repositorio ilustra la evolución de un sistema monolítico hacia una arquitectura web desacoplada, implementando una API RESTful en el backend y un frontend con Astro.

Representación web: **SSG** (Static Site Generation) para el contenido estático y **CSR** (Client-Side Rendering) a través de la Arquitectura de Islas para las regiones interactivas.

---

## Estructura del Proyecto

El repositorio está dividido en dos aplicaciones independientes:

### 1. Backend (Django)
Provee la API y centraliza la lógica de negocio y persistencia de datos.
* **Base de Datos:** Emplea SQLite.
* **Datos Reproducibles:** Utiliza el comando `python manage.py seed_activities` para cargar el catálogo de actividades de prueba de forma segura y sin generar duplicados.
* **Patrón Despachador:** Para respetar el diseño de la API en los endpoints de inscripción, se utiliza una misma URL para los métodos `PUT` y `DELETE`. Esto se maneja de forma nativa en Django clásico centralizando el tráfico en una vista con el decorador `@require_http_methods(["PUT", "DELETE"])`, que luego delega la acción internamente mediante un bloque `if`.
* **CORS:** Se incorporó `django-cors-headers` para permitir peticiones seguras desde el origen `localhost:4321` y autorizar el uso del encabezado personalizado `X-Participant-Id`.

### 2. Frontend (Astro + React)
Reemplaza la inicialización original basada en Vite para implementar un enfoque híbrido de renderizado.
* **Parte A - SSG (Representación Estática):** 
  Las páginas `/activities` (listado) y `/activities/[id]` (detalle) consumen la API de Django exclusivamente durante el proceso de **build** (usando `getStaticPaths`). El resultado es HTML puro generado en el servidor antes de la petición del usuario, lo que congela los datos en el documento y reduce el tiempo de renderizado (LCP) a escasos milisegundos.
* **Parte B - CSR (Arquitectura de Islas):** 
  Para consultar y modificar inscripciones sin recargar la página, se creó la isla de React `EnrollmentIsland.jsx`. 
  *Ejemplo de uso:* Se incrusta en el HTML estático utilizando la directiva `<EnrollmentIsland client:load />`. Esto indica al navegador que solo debe descargar y ejecutar JavaScript para esta pequeña porción interactiva, manteniendo el resto del sitio rápido y ligero.

---

## 🚀 Puesta en Marcha y Ejecución

Para levantar el proyecto y recolectar la evidencia solicitada:

### Paso 1: Inicializar la API
Abre tu terminal (puedes utilizar cualquier emulador configurado con `bash` o `zsh`), ingresa a la carpeta `backend/` y ejecuta:

```bash
# Aplica las migraciones y puebla la base de datos
python manage.py migrate
python manage.py seed_activities

# Inicia el servidor en el puerto 8000
python manage.py runserver
```

La API quedará escuchando en <http://127.0.0.1:8000/>

### Paso 2: Generar y previsualizar el Frontend
En una nueva terminal, ingresa a la carpeta del proyecto de Astro (`frontend-astro/`) y ejecuta:

```bash
# Instala las dependencias del proyecto
pnpm install

# Genera los archivos estáticos HTML (Ejecuta la fase de Build)
pnpm build

# Levanta un servidor local ligero para ver el resultado de producción
pnpm preview
```

El frontend estará en <http://localhost:4321/>

### Evidencia de Renderizado
Al correr el proyecto con `pnpm preview`, se puede comprobar la naturaleza hibrida de la aplicación:
1. **Evidencia del Build (SSG):** Al inspeccionar el código fuente de la página de detalle (`Ctrl + U`), se observa que el titulo y la capacidad de la actividad ya vienen escritos desde el servidor en el HTML inicial.

2. **Evidencia del Navegador (CSR):** Al monitorear la pestaña Newtwork, de las herramientas de desarrollador, se ve la descarga de los script de React y del cliente de Astro. Inmediatamente después, se dispara un evento `fetch`hacia el backend para corroborar el estado de inscripción del usuario, demostrando que esta sección de la interfaz fue resuelta en tiempo de ejecución.