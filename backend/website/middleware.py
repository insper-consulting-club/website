from django.conf import settings
from django.utils.cache import patch_cache_control


class PublicApiCacheMiddleware:
    """Deixa o navegador reaproveitar por alguns segundos as respostas de leitura da API.

    Evita refazer a mesma chamada a cada troca de página. O custo é que uma edição
    feita no admin pode levar até `API_CACHE_SECONDS` para aparecer no site.
    O `/api/health/` fica de fora, porque o monitor precisa de uma resposta real.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        seconds = settings.API_CACHE_SECONDS
        if (
            seconds > 0
            and request.method in ("GET", "HEAD")
            and request.path.startswith("/api/")
            and request.path != "/api/health/"
            and response.status_code == 200
            and not response.has_header("Cache-Control")
        ):
            patch_cache_control(response, public=True, max_age=seconds)
        return response
