from datetime import datetime
from uuid import UUID

from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

# importado de openapi
from ninja import NinjaAPI, Schema
from pydantic import Field

from .identity import get_participant
from .models import Activity, Enrollment, Participant
from .representations import (
    serialize_activities,
    serialize_activity,
    serialize_enrollment,
    serialize_enrollments,
)

api = NinjaAPI(title="Activities API", version="1.0.0")

class ActivityOut(Schema):
    id: UUID = Field(description="Identificador único de la actividad.")
    title: str = Field(description="Nombre visible de la actividad.")
    starts_at: datetime = Field(
        description="Fecha en ISO 8601 (YYYY-MM-DDTHH:SS+HH:MM).", 
        examples=["2026-03-25T18:00:00-03:00"]
    )
    capacity: int = Field(
        ge=0,
        description="Cantidad máxima de participantes.",
        examples=[30],
    )
# ---- openapi

def response_error(status, code, message):
    return JsonResponse({"error": message, "code": code}, status=status)

@require_GET
def activity_list(request):
    activities = Activity.objects.all()
    return render(
        request,
        "activities/activity_list.html",
        {"activities": activities},
    )

# importado de openapi
@api.get(
    "/activities",
    response=list[ActivityOut],
    tags=["Activities"],
    openapi_extra={
        "responses": {
            405: {
                "headers": {
                    "Allow": {
                        "description": "Método HTTP admitido por la ruta.",
                        "schema": {
                            "type": "string",
                            "example": "GET"
                        }
                    }
                }
            }
        }
    },
)
#--------

@require_GET
def activity_api_list(request):
    activities = Activity.objects.all()
    payload = serialize_activities(activities)
    # safe=False permite devolver una lista en lugar de un diccionario
    return JsonResponse(payload, safe=False)

@require_GET
def activity_detail(request, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
        return JsonResponse(serialize_activity(activity))
    except (Activity.DoesNotExist, ValueError):
        return response_error(404, "not_found", "Actividad no encontrada")

@require_GET
def my_enrollments_list(request):
    participant = get_participant(request)
    if not participant:
        return response_error(400, "invalid_identity", "Identidad inválida")
    
    enrollments = Enrollment.objects.filter(participant=participant)
    payload = serialize_enrollments(enrollments)
    return JsonResponse(payload, safe=False)

def procesar_inscripcion(request, participant, activity):
    if activity.available_slots <= 0:
        return response_error(409, "conflict", "La actividad no tiene cupos disponibles")

    try:
        enrollment = Enrollment.objects.create(participant=participant, activity=activity)
        return JsonResponse(serialize_enrollment(enrollment), status=201)
    except IntegrityError:
        return response_error(409, "conflict", "El participante ya está inscripto")

def procesar_cancelacion(request, participant, activity):
    try:
        enrollment = Enrollment.objects.get(participant=participant, activity=activity)
        enrollment.delete()
        return JsonResponse({}, status=204)
    except Enrollment.DoesNotExist:
        return response_error(404, "not_found", "Inscripción no encontrada")

@require_http_methods(["PUT", "DELETE"])
@csrf_exempt
def activity_enrollment_api_put_delete(request, activity_id):
    participant = get_participant(request)
    if not participant:
        return response_error(400, "invalid_identity", "Identidad inválida")
        
    try:
        activity = Activity.objects.get(id=activity_id)
    except (Activity.DoesNotExist, ValueError):
        return response_error(404, "not_found", "Actividad no encontrada")

    if request.method == "PUT":
        return procesar_inscripcion(request, participant, activity)
    elif request.method == "DELETE":
        return procesar_cancelacion(request, participant, activity)
       
