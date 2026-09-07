# Actividad 05: Observabilidad y Correlación 🔍

Este proyecto incorpora una capa de observabilidad transversal a la API, permitiendo reconstruir la historia completa de cada petición HTTP (request, decisiones de dominio y response) sin modificar la semántica de los recursos existentes ni crear una nueva versión.

**Modificaciones Realizadas**

* **Middleware de Correlación (`middleware.py`):** Intercepta todas las peticiones entrantes. Si el cliente envía el encabezado `X-Correlation-ID`, lo conserva; de lo contrario, genera un UUID opaco aleatorio. Este identificador se inyecta en la respuesta HTTP y se utiliza internamente para vincular todos los logs de una misma interacción.
* **Formateador de Logs (`log_formatters.py` y `settings.py`):** Reemplaza el registro de texto libre por eventos estructurados en formato JSON. Se configuró mediante una "lista blanca", extrayendo de forma manual y estricta solo los datos técnicos requeridos (`timestamp`, `level`, `event`, `method`, `path`, `result`, `correlation_id`). Esto bloquea cualquier fuga accidental de secretos, tokens o datos sensibles.
* **Instrumentación del Dominio (`views.py`):** Se integraron logs en los hitos clave del proceso de inscripción para registrar la decisión exacta del servidor (`enrollment_created`, `enrollment_reused`, `enrollment_rejected`). Esto permite diagnosticar incidentes basándose en evidencia directa en lugar de inferencias.

**Cómo Probar y Diagnosticar**

Iniciar el servidor con `python manage.py runserver` y ejecuta los siguientes comandos en una terminal separada. Los logs estructurados aparecerán en la consola de Django.

**Caso A: Generación automática del ID**
```bash
curl.exe -i -X GET http://127.0.0.1:8000/api/v1/activities
```

**Caso B: Trazabilidad completa y decisiones de dominio**
```bash
curl.exe -i -X PUT -H "X-Participant-Id: <TU_PARTICIPANT_ID>" -H "X-Correlation-ID: evidencia-equipo-42" http://127.0.0.1:8000/api/v1/me/enrollments/ACTIVITY_ID