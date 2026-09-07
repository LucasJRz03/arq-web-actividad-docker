from datetime import datetime
from uuid import UUID
import logging

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
    serialize_activities_2,
    serialize_activity_2,
    serialize_enrollment,
    serialize_enrollments,
)

logger = logging.getLogger('actividad_logger')

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

class AvailabilityOut(Schema):
    capacity: int = Field(ge=0, description="Cantidad máxima de participantes.", examples=[30],)
    available_slots: int = Field(ge=0, description="Cupos disponibles.", examples=[24])

class ActivityOutV2(Schema):
    id: UUID = Field(description="Identificador único de la actividad.")
    title: str = Field(description="Nombre visible de la actividad.")
    starts_at: datetime = Field(
        description="Fecha en ISO 8601 (YYYY-MM-DDTHH:SS+HH:MM).", 
        examples=["2026-03-25T18:00:00-03:00"]
        )
    availability : AvailabilityOut
# ---- openapi

def response_error(status, code, message):
    # Antes: return JsonResponse({"error": message, "code": code}, status=status})
    return JsonResponse({"code": code, "message": message}, status=status)

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
    "/v1/activities",
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


@api.get(
    "/v2/activities",
    response=list[ActivityOutV2],
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

def activity_api_list_2(request):
    activities = Activity.objects.all()
    payload = serialize_activities_2(activities)
    return JsonResponse(payload, safe=False)

@require_GET
def activity_detail_2(request, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
        return JsonResponse(serialize_activity_2(activity))
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
    # 1. Idempotencia: verificar si la inscripción ya existe
    try:
        enrollment = Enrollment.objects.get(participant=participant, activity=activity)
        logger.info("enrollment_reused", extra={"correlation_id": request.correlation_id})
        return JsonResponse(serialize_enrollment(enrollment), status=200)
    except Enrollment.DoesNotExist:
        pass
    
    # 2. Invariante: Control de capacidad (actualizado con el contrato estricto)
    if activity.available_slots <= 0:
        logger.info("enrollment_rejected", extra={"correlation_id": request.correlation_id, "result": "capacity_exhausted"})
        return response_error(409, "capacity_exhausted", "No hay lugares disponibles")

    # 3. Creación de la primera inscripcion
    try:
        enrollment = Enrollment.objects.create(participant=participant, activity=activity)
        logger.info("enrollment_created", extra={"correlation_id": request.correlation_id, "result": "created"} )
        return JsonResponse(serialize_enrollment(enrollment), status=201)
    except IntegrityError:
        # Preventivo para colisiones a nivel de base de datos
        return response_error(409, "conflict", "El participante ya está inscripto")


def procesar_cancelacion(request, participant, activity):
    try:
        enrollment = Enrollment.objects.get(participant=participant, activity=activity)
        enrollment.delete()
    except Enrollment.DoesNotExist:
        # si ya existe, ignora el error
        pass 
    # en ambos casos (se borró recién o ya estaba borrado), devuelve 204
    return JsonResponse({}, status=204)

# devuelve 405 si no recibe uno de estos métodos
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
       
