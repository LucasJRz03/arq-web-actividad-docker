# Helper para extraer el participante de demostración
from .models import Participant


def get_participant(request):
    participant_id = request.headers.get("X-Participant-Id")
    if not participant_id:
        return None
    try:
        return Participant.objects.get(id=participant_id)
    except (Participant.DoesNotExist, ValueError):
        return None