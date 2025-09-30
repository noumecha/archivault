from django.http import JsonResponse
from rest_framework.authtoken.models import Token

class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # exclure les urls d'authentification 
        if request.path in ['/api/users/login/']:
            return self.get_response(request)
        
        # vérifier le token pour les autres urls
        token_key = request.headers.get('Authorization', '').split(' ')[-1]
        if not token_key:
            return JsonResponse(
                {'error', 'Token manquant'},
                status=401
            )

        try:
            token = Token.objects.get(key=token_key)
            request.user = token.user
        except Token.DoesNotExist:
            return JsonResponse(
                {'error' : 'Token invalide'},
                status=401
            )
        
        return self.get_response(request)