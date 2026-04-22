# apps/users/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from django.http import JsonResponse

PUBLIC_PATHS = [
    '/login/',
    '/logout/',
    '/admin/',
    '/__reload__/',
    '/static/',
    '/media/',
    '/api/auth/login/',
    '/api/auth/logout/',
]

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        # 1. On laisse passer les chemins publics (Vérification stricte)
        if any(path == p or path == p.rstrip('/') for p in PUBLIC_PATHS):
            return self.get_response(request)

        # 2. Si déjà connecté via Session Django
        if request.user.is_authenticated:
            return self.get_response(request)

        # 3. Vérification JWT Cookie
        token = request.COOKIES.get('access_token')
        if token:
            try:
                AccessToken(token)
                return self.get_response(request)
            except Exception:
                # Si le token est invalide et que c'est une API
                if path.startswith('/api/'):
                    return JsonResponse({'error': 'Unauthorized'}, status=401)

                response = redirect(reverse('login'))
                response.delete_cookie('access_token')
                return response

        # 4. Sécurité : Si on arrive ici, l'utilisateur n'est pas reconnu
        # JAMAIS de redirection 302 pour une API !
        if path.startswith('/api/'):
            return JsonResponse({'error': 'Authentication required'}, status=401)

        return redirect(reverse('login'))
