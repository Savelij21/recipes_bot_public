from django.conf import settings
from django.http import JsonResponse


class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Исключение админки и других URL
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Фильтрация только для API URL-адресов
        api_key = request.headers.get('X-API-Key')
        if api_key != settings.SECRET_KEY:
            return JsonResponse({'error': 'Invalid API Key'}, status=401)

        return self.get_response(request)
