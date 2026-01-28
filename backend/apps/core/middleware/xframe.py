"""
Middleware para eliminar X-Frame-Options header.
Esto permite que los archivos se muestren en iframes.
NOTA: Solo usar en desarrollo local.
"""


class RemoveXFrameOptionsMiddleware:
    """
    Middleware que elimina el header X-Frame-Options de todas las respuestas.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Eliminar X-Frame-Options si existe
        if 'X-Frame-Options' in response:
            del response['X-Frame-Options']
        return response
