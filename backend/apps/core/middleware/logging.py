"""
Middleware para logging de requests.
"""
import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware que registra información sobre cada request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Tiempo de inicio
        start_time = time.time()

        # Log del request
        logger.info(
            f"REQUEST: {request.method} {request.path} "
            f"[User: {request.user if hasattr(request, 'user') else 'Anonymous'}]"
        )

        # Procesar request
        response = self.get_response(request)

        # Calcular duración
        duration = time.time() - start_time

        # Log del response
        logger.info(
            f"RESPONSE: {request.method} {request.path} "
            f"[Status: {response.status_code}] "
            f"[Duration: {duration:.2f}s]"
        )

        return response
