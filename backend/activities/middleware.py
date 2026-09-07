import uuid
import logging 

logger = logging.getLogger('actividad_logger')

class CorrelationIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
       
        x = request.headers.get('X-Correlation-ID')
       
        if not x:
            x = str(uuid.uuid4())

        request.correlation_id = x
                    # request_received es el log entrada
        logger.info("request_received", extra={"correlation_id": x, "method": request.method, "path": request.path})

        response = self.get_response(request)

        response["X-Correlation-ID"] = x

        logger.info("request_completed", extra={"correlation_id": x, "result": response.status_code})

        return response