import { useState, useEffect } from 'react';

const PARTICIPANT_ID = "1f7b226a-5833-4ac3-8de7-fafccb079bf8";

export default function EnrollmentIsland({ activityId }) {
  // 'isEnrolled' empieza en false. 'loading' empieza en true (porque al cargar, aún no tenemos la respuesta).
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [loading, setLoading] = useState(true);
  // Para guardar mensajes de error en la pantalla
  const [errorMsg, setErrorMsg] = useState(null);
  // useEffect se ejecuta automáticamente cuando la isla aparece en el navegador.
  useEffect(() => {
    // GET a API de Django enviando el header requerido
    fetch("/api/v1/me/enrollments", {
      method: "GET",
      headers: {
        "X-Participant-Id": PARTICIPANT_ID
      }
    })
      .then((response) => response.json())
      .then((enrollments) => {
        // La API nos devuelve un array con todas nuestras inscripciones.
        // Usa .some() para verificar si alguna de ellas coincide con el ID de la actividad actual.
        const alreadyEnrolled = enrollments.some(e => e.activity_id === activityId);
        
        setIsEnrolled(alreadyEnrolled); // Actualizamos el estado
        setLoading(false);              // Apagamos el mensaje de carga
      })
      .catch((error) => {
        console.error("Error al consultar la API:", error);
        setLoading(false);
      });
  }, [activityId]); // Este array le dice a React: "Solo vuelve a ejecutar esto si cambia el activityId"

  // PUT - funcion para inscribirse
  const handleEnroll = async () => {
    setLoading(true);    // está cargando
    setErrorMsg(null);   // Limpia errores anteriores

    try {
      const response = await fetch(`/api/v1/me/enrollments/${activityId}`, {
        method: "PUT",
        headers: { "X-Participant-Id": PARTICIPANT_ID }
      });

      // Evalua los status HTTP
      if (response.status === 201) {
        setIsEnrolled(true); // Cambiamos el estado para que la UI se actualice sola
      } else if (response.status === 409) {
        setErrorMsg("Conflicto: La actividad no tiene cupos o ya estabas inscripto.");
      } else if (response.status === 404) {
        setErrorMsg("Error: La actividad no existe.");
      } else {
        setErrorMsg(`Error inesperado (Status: ${response.status})`);
      }
    } catch (err) {
      setErrorMsg("Error de red al intentar conectarse con el servidor.");
    }

    setLoading(false);
  };

  //Renderiza la interfaz dependiendo de los estados
  return (
    <div style={{ border: "2px solid #007bff", padding: "1rem", marginTop: "2rem" }}>
      <h3>Gestión de Inscripciones</h3>
      
      {/* Si hay un error, lo muestra en color rojo */}
      {errorMsg && <p style={{ color: "red", fontWeight: "bold" }}>{errorMsg}</p>}

      {loading ? (
        <p>Consultando el estado de tu inscripción...</p>
      ) : isEnrolled ? (
        <p>Ya estás inscripto en esta actividad.</p>
      ) : (
        <button 
          onClick={handleEnroll} 
          style={{ padding: "0.5rem 1rem", cursor: "pointer", background: "#007bff", color: "white", border: "none" }}
        >
          Inscribirme a esta actividad
        </button>
      )}
    </div>
  );
}
