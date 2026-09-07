# Actividad 4: Evolución y Versionado de la API 🚀

El objetivo de esta actividad fue introducir una nueva versión de la API (v2) con un cambio en la forma de los datos, pero **sin romper** el funcionamiento de la versión original (v1).

A continuación, se detallan las modificaciones principales, dónde se hicieron y por qué.

---

## 🛠️ Modificaciones Realizadas

**1. Nueva forma de los datos (`representations.py`)**
*   **Qué modificamos:** Creamos funciones nuevas exclusivas para v2 (como `serialize_activity_2`). Estas nuevas funciones agrupan los cupos dentro de un nuevo bloque anidado llamado `availability`.
*   **Por qué:** Era fundamental aislar esta lógica. Si modificábamos la función original de v1, rompíamos automáticamente el contrato para los clientes antiguos que esperan encontrar los cupos en la raíz del JSON.

**2. Separación de Rutas (`urls.py`)**
*   **Qué modificamos:** Agregamos nuevas direcciones que empiezan con `/api/v2/activities` apuntando a las nuevas funciones. Sin embargo, para las inscripciones (`enrollments`), las rutas de v2 apuntan exactamente a las mismas vistas de v1.
*   **Por qué:** Para el catálogo necesitábamos separar los caminos porque la respuesta cambia. Pero para las inscripciones, la consigna indicaba que el contrato no cambiaba en absoluto, por lo que reutilizamos el código existente para no duplicar trabajo.

**3. Controladores y Documentación (`views.py`)**
*   **Qué modificamos:** Creamos nuevas vistas para v2 que utilizan los nuevos serializadores. Además, configuramos esquemas (`Schema`) separados en Django Ninja para documentar esta nueva versión.
*   **Por qué:** Necesitábamos que la documentación interactiva (Swagger UI) mostrara claramente cómo es el JSON de v1 (plano) y cómo es el de v2 (anidado) de forma independiente, sin que el framework las mezcle.

**4. La Base de Datos (Lo que NO tocamos)**
*   **Qué mantuvimos igual:** No modificamos los modelos ni la estructura interna de la base de datos. 
*   **Por qué:** El versionado de una API trata sobre cómo **presentamos** la información hacia afuera. La lógica interna, las reglas de negocio y los datos reales siguen siendo exactamente los mismos y compartidos para ambas versiones.

---

## 🚀 Cómo probar la convivencia de versiones

Para verificar que ambas versiones funcionan en simultáneo sin pisarse, iniciá el servidor local y ejecutá estas consultas desde tu terminal:

*   **Consultar v1 (Datos de cupos en la raíz):**
    `curl.exe -X GET http://127.0.0.1:8000/api/v1/activities`
    
*   **Consultar v2 (Datos anidados en availability):**
    `curl.exe -X GET http://127.0.0.1:8000/api/v2/activities`

*   **Ver la documentación (Swagger UI):**
    Ingresá desde el navegador a `http://127.0.0.1:8000/api/docs` para comprobar que ambos contratos están documentados de forma diferenciada.