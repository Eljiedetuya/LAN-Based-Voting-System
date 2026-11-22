from django.http import JsonResponse


class RequirePasswordChangeMiddleware:
    """Limit temporary-password sessions to account recovery endpoints."""
    allowed_paths = {
        '/api/auth/csrf/',
        '/api/auth/login/',
        '/api/auth/logout/',
        '/api/auth/me/',
        '/api/auth/password/change/',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if (request.path.startswith('/api/') and request.path not in self.allowed_paths
                and user and user.is_authenticated and user.must_change_password):
            return JsonResponse({'error': {
                'code': 'password_change_required',
                'detail': 'Change your temporary password before continuing.',
            }}, status=403)
        return self.get_response(request)
