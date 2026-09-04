# Backend Django

Aplicación Django clásica con persistencia SQLite. La ruta `/` consulta el modelo `Activity` y renderiza en el servidor una tabla HTML con todos sus campos.

## Requisitos

- Python 3.12 o posterior.

## Iniciar el proyecto

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_activities
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>.

## Documentación de Ninja
<http://127.0.0.1:8000/api/v1/docs>

`seed_activities` se puede ejecutar más de una vez: restaura el mismo conjunto de actividades sin duplicarlas.

## Comandos útiles

```bash
# Ejecutar las pruebas
python manage.py test

# Abrir la consola de Django
python manage.py shell

# Vaciar la base y volver a cargar los datos de muestra
python manage.py flush --noinput
python manage.py seed_activities
```

## Estructura relevante

- `activities/models.py`: modelo `Activity`.
- `activities/views.py`: vista clásica que consulta la base.
- `activities/templates/activities/activity_list.html`: documento HTML producido por Django.
- `activities/management/commands/seed_activities.py`: datos reproducibles.

SQLite usa el archivo `db.sqlite3`, creado por `python manage.py migrate` y excluido de Git.

# Actividad 1: De Monolito a API REST 

Este proyecto es una base de trabajo didáctica diseñada para enseñar cómo migrar de una aplicación tradicional de Django (renderizada en el servidor mediante plantillas HTML) a una arquitectura separada (desacoplada). El objetivo de esta primera fase es construir una API RESTful en el backend que luego será consumida por un frontend independiente.

---

## Estructura de la Arquitectura

El repositorio arranca con dos aplicaciones completamente independientes:

*   **Backend (`backend/`):** Está construido con Django y utiliza una base de datos SQLite. Contiene los modelos principales de dominio, como `Activity` y `Enrollment`. 
*   **Frontend (`frontend/`):** Es un proyecto inicializado con Vite, React y TypeScript. En este punto inicial, sirve como una base limpia preparada para integrarse con la API. (Ignorar)

---

## El Contrato HTTP (Endpoints Implementados)

Para transformar el backend en un proveedor de datos, se crearon los siguientes endpoints bajo el estándar RESTful, devolviendo respuestas en formato JSON en lugar de HTML:

### 1. Superficie de Lectura (Catálogo)
*   `GET /api/v1/activities/`: Lista todas las actividades disponibles en la base de datos.
*   `GET /api/v1/activities/<activity_id>`: Devuelve el detalle de una actividad específica utilizando su identificador UUID.

### 2. Superficie de Inscripción (Gestión de Usuarios)
Para simular una sesión de usuario de forma sencilla, estos endpoints exigen enviar el UUID del usuario a través del encabezado HTTP `X-Participant-Id`.

*   `GET /api/v1/me/enrollments`: Lista las inscripciones activas del participante actual.
*   `PUT /api/v1/me/enrollments/<activity_id>`: Inscribe al participante en la actividad. 
    *   Devuelve `201 Created` si fue exitoso. 
    *   Devuelve `409 Conflict` si la actividad no tiene cupos disponibles o si el participante ya estaba inscripto (capturando el `IntegrityError` de la base de datos).
*   `DELETE /api/v1/me/enrollments/<activity_id>`: Cancela la inscripción y libera el cupo, devolviendo un código `204 No Content`.

---

## Decisiones de Diseño y Patrones

### El Patrón "Despachador" en Django
En Django puro, al utilizar Vistas Basadas en Funciones (FBVs), el enrutador (`urls.py`) hace coincidir únicamente el texto de la URL de arriba hacia abajo, ignorando el verbo HTTP (GET, PUT, DELETE). 

Para cumplir con el requerimiento de que la ruta de inscripción y cancelación compartan exactamente la misma URL (`/api/v1/me/enrollments/<activity_id>`), se implementó el **Patrón Despachador**:
*   Se asignó una única función como punto de entrada en `urls.py`.
*   La vista principal actúa como un "semáforo" al utilizar el decorador combinado `@require_http_methods(["PUT", "DELETE"])`.
*   Internamente, la función evalúa el verbo con un condicional (`if request.method == "PUT":`) y deriva el tráfico hacia las sub-funciones independientes `procesar_inscripcion` o `procesar_cancelacion`. 

---

## Puesta en Marcha

El proyecto se puede levantar localmente de la siguiente forma:

**1. Levantar el Backend (Puerto 8000)**
```bash
# Aplicar migraciones y poblar datos de prueba de forma reproducible
python manage.py migrate
python manage.py seed_activities

# Iniciar servidor local
python manage.py runserver
