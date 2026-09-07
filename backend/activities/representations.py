from django.utils import timezone

def serialize_activity(activity, include_available_slots=True) -> dict:
    """Serializa una actividad. Incluye available_slots por defecto."""
    data = {
        "id": str(activity.id),
        "title": activity.title,
        "starts_at":  timezone.localtime(activity.starts_at).isoformat(),
        "capacity": activity.capacity,
    }
    if include_available_slots:
        data["available_slots"] = activity.available_slots
    return data

# funcion para la versión 2
def serialize_activity_2(activity) -> dict:
    """Serialize una actividad con available"""
    data = {
        "id": str(activity.id),
        "title": activity.title,
        "starts_at": timezone.localtime(activity.starts_at).isoformat(),
        "availability": {
            "capacity": activity.capacity,
            "available_slots": activity.available_slots,
        }
    }
    return data

def serialize_activities(activities) -> list:
    return [serialize_activity(activity) for activity in activities]

def serialize_activities_2(activities) -> list: 
    return [serialize_activity_2(activity) for activity in activities]

def serialize_enrollment(enrollment) -> dict:
    """Serializa una inscripción."""
    return {
        "id": str(enrollment.id),
        "activity_id": str(enrollment.activity_id),
        "participant_id": str(enrollment.participant_id),
        "enrolled_at": timezone.localtime(enrollment.enrolled_at).isoformat(),
    }

def serialize_enrollments(enrollments) -> list:
    return [serialize_enrollment(e) for e in enrollments]