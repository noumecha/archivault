from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

PUBLIC_PATHS = [
    '/login/',
    '/api/login/',
    '/logout/',
    '/api/logout/',
    '/admin/',
    '/__reload__/',
    '/static/',
    '/media/',  # Ajoutez ceci
]

class JWTAuthMiddleware:
    """
    Middleware global qui redirige les utilisateurs non authentifiés vers la page de login.
    Il vérifie le token JWT stocké dans les cookies (access_token).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        # Autoriser les chemins publics (inclut /login/)
        if any(path.startswith(p) for p in PUBLIC_PATHS):
            return self.get_response(request)

        # Ne pas interférer avec les appels d'API REST
        if path.startswith('/api/'):
            return self.get_response(request)

        # Vérifie la présence du cookie d'authentification
        token = request.COOKIES.get('access_token')
        if token:
            try:
                AccessToken(token)  # valide le token
                return self.get_response(request)
            except Exception as e:
                # Token expiré ou invalide
                response = redirect(reverse('login'))
                response.delete_cookie('access_token')  # Nettoie le cookie invalide
                return response

        # Redirige vers la page de login
        return redirect(reverse('login'))
