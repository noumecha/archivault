# apps/users/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from ..services.auth_service import AuthService

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("request.data : ", request.data)
        username = request.data.get("username")
        password = request.data.get("password")

        user = AuthService.authenticate_user(username, password)
        if not user:
            return Response({"error": "Identifiants invalides"}, status=status.HTTP_401_UNAUTHORIZED)

        django_login(request, user)
        tokens = AuthService.generate_tokens_for_user(user)

        response = Response({
            "message": "Connexion réussie",
            "user": {"id": user.id, "username": user.username, "role": user.role} # Optionnel pour le mobile
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            'access_token', tokens['access'],
            httponly=True, secure=not settings.DEBUG, samesite='Lax'
        )
        response.set_cookie(
            'refresh_token', tokens['refresh'],
            httponly=True, secure=not settings.DEBUG, samesite='Lax'
        )
        response.data['tokens'] = tokens

        return response

class LogoutAPIView(APIView):
    def post(self, request):
        response = Response({"message": "Déconnexion réussie"}, status=status.HTTP_200_OK)
        # Supprimer les cookies côté client
        django_logout(request)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
