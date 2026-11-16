# Proy práctica - De Django clásico a una arquitectura contenerizada

El repositorio documenta la evolución progresiva de un sistema monolítico hacia una arquitectura web desacoplada, observable y contenerizada.

**Estado inicial (Monolito):**
- `backend/`: Django, el modelo `Activity`, SQLite y una vista HTML clásica.
- `frontend-astro`: Vite + React + TypeScript recién inicializado, sin integración con Django.

**Estado actual (Actividades 2, 4, 5 y 6):**
- `backend/`: API RESTful con Django + Gunicorn + PostgreSQL + Middleware de Observabilidad.
- `frontend-astro`: SSG + CSR mediante Arquitectura de Islas (Astro + React).
- **Infraestructura:** Docker Compose orquestando 4 servicios con Nginx como reverse proxy.

---

## Puesta en marcha

### Opción A: Con Docker (Recomendado - Estado actual)

```bash
docker compose up --build
```

El reverse proxy (Nginx) en el puerto `80` enrutará automáticamente:
- **`/`** → Frontend Astro (puerto interno 4321)
- **`/api/`** → Backend Django (puerto interno 8000)

Abrir <http://localhost/>.

### Opción B: Desarrollo local sin Docker

#### 1. Backend

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

#### 2. Frontend

En otra terminal:

```bash
cd frontend-astro/
pnpm install
pnpm dev
```

Abrir <http://127.0.0.1:4321/>.

---

## Verificación rápida

```bash
cd backend
python manage.py test

cd ../frontend-astro
pnpm build
```

---

## Punto de partida didáctico

# Evolución de la Arquitectura Web

Este proyecto corresponde a la resolución de las Actividades 2, 4, 5 y 6 de la materia Arquitectura Web (TUDA 2026). El repositorio ilustra la transición de un monolito clásico a una arquitectura web moderna con renderizado híbrido, contenedores, bases de datos persistentes y observabilidad estructural.

---

## Estructura del Proyecto

El repositorio está organizado en dos aplicaciones principales y una capa de infraestructura orquestada:

### 1. Backend (Django + Gunicorn + PostgreSQL)
Provee la API RESTful y centraliza la lógica de negocio y persistencia.
* **Base de Datos:** PostgreSQL 16 (reemplaza a SQLite), configurado con healthchecks en Docker para garantizar disponibilidad antes del arranque del backend.
* **Datos Reproducibles:** El comando `python manage.py seed_activities` se ejecuta automáticamente al iniciar el contenedor para poblar la base de datos sin duplicados.
* **Patrón Despachador:** Para respetar el diseño de la API en los endpoints de inscripción, se utiliza una misma URL para los métodos `PUT` y `DELETE`, manejado con `@require_http_methods(["PUT", "DELETE"])` y delegado internamente.
* **CORS:** `django-cors-headers` permite peticiones seguras desde el frontend y autoriza el encabezado `X-Participant-Id`.
* **Servidor de Producción:** Gunicorn reemplaza al servidor de desarrollo de Django, sirviendo la aplicación mediante `gunicorn config.wsgi:application`.
* **Observabilidad (Actividad 5):**
  - **Middleware de Correlación:** Intercepta peticiones y conserva el encabezado `X-Correlation-ID` del cliente o genera un UUID opaco, inyectándolo en la respuesta y los logs internos.
  - **Logs Estructurados (JSON):** Reemplaza el texto libre por eventos estructurados usando una "lista blanca" de campos técnicos (`timestamp`, `level`, `event`, `method`, `path`, `result`, `correlation_id`), evitando fugas de datos sensibles.
  - **Instrumentación de Dominio:** Registra hitos clave (`enrollment_created`, `enrollment_reused`, `enrollment_rejected`) para diagnóstico basado en evidencia directa.

### 2. Frontend (Astro + React)
Implementa un enfoque híbrido de renderizado que reemplaza la inicialización original basada en Vite.
* **Parte A - SSG (Representación Estática):** 
  Las páginas `/activities` y `/activities/[id]` consumen la API de Django exclusivamente durante el **build** (usando `getStaticPaths`). El HTML puro generado congela los datos y reduce drásticamente el tiempo de renderizado (LCP).
* **Parte B - CSR (Arquitectura de Islas):** 
  Para modificar inscripciones sin recargar la página, se creó la isla `EnrollmentIsland.jsx`. 
  *Ejemplo de uso:* Se incrusta con `<EnrollmentIsland client:load />`, indicando al navegador descargar JavaScript solo para esa porción interactiva.

### 3. Infraestructura (Docker Compose + Nginx)
* **Reverse Proxy (Nginx):** Actúa como punto de entrada único. La configuración en `nginx.conf` enruta `/api/` al servicio backend y `/` al servicio frontend-astro.
* **Orquestación:** El archivo `compose.yaml` define 4 servicios (`proxy`, `backend`, `frontend-astro`, `db`) con redes aisladas (`web` y `data`) y volúmenes persistentes (`pgdata` para PostgreSQL, `frontend_node_modules` para aislar dependencias).

---

## Puesta en Marcha y Ejecución

Para levantar el proyecto completo en su estado actual (contenerizado):

### Paso 1: Levantar el stack con Docker Compose

Abre tu terminal en la raíz del proyecto y ejecuta:

```bash
# Construye las imágenes y levanta todos los servicios
docker compose up --build
```

El stack quedará escuchando en:
* **Aplicación completa:** <http://localhost/> (vía Nginx)
* **API directamente:** <http://localhost/api/>

### Evidencia de Renderizado

Al correr el proyecto, se puede comprobar la naturaleza híbrida de la aplicación:

1. **Evidencia del Build (SSG):** Al inspeccionar el código fuente de la página de detalle (`Ctrl + U`), se observa que el título y la capacidad de la actividad ya vienen escritos desde el servidor en el HTML inicial.

2. **Evidencia del Navegador (CSR):** Al monitorear la pestaña Network, se ve la descarga de los scripts de React y del cliente de Astro. Inmediatamente después, se dispara un evento `fetch` hacia el backend para corroborar el estado de inscripción del usuario, demostrando que esta sección de la interfaz fue resuelta en tiempo de ejecución.

### Evidencia de Observabilidad

Los logs estructurados JSON con correlation IDs aparecen en la consola del contenedor backend (`docker compose logs -f backend`):

**Caso A: Generación automática del ID**
```bash
curl -i -X GET http://localhost/api/v1/activities
```

**Caso B: Trazabilidad completa con ID personalizado**
```bash
curl -i -X PUT \
  -H "X-Participant-Id: demo-user" \
  -H "X-Correlation-ID: evidencia-equipo-42" \
  http://localhost/api/v1/me/enrollments/ACTIVITY_ID
```
