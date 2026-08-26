from django.http import JsonResponse

def error_response(status: int, code: str, message: str = "") -> JsonResponse:
    """Respuesta de error estándar."""
    return JsonResponse(
        {"error": {"code": code, "message": message}},
        status=status,
    )