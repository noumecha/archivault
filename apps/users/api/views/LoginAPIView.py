# apps/users/api/views/LoginAPIView.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.contrib.auth import login as django_login
from ...services.auth_service import AuthService
from apps.circulation.services.audit_service import AuditService
from apps.circulation.models import ActionAudit, StatutAudit
from rest_framework import status

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = AuthService.authenticate_user(username, password)

        if not user:
            # 🛑 ÉCHEC : Journalisation de la tentative de connexion infructueuse
            # Sécurité : On logue l'identifiant tenté, mais JAMAIS le mot de passe reçu.
            AuditService.log(
                request,
                action=ActionAudit.CONNEXION,
                statut=StatutAudit.FAILED,
                label=f"Tentative de connexion échouée pour l'utilisateur : {username}",
                details={"username_tente": username, "motif": "Identifiants invalides"}
            )
            return Response({"error": "Identifiants invalides"}, status=status.HTTP_401_UNAUTHORIZED)

        # Connexion au sens session Django (attache l'utilisateur à la requête actuelle)
        django_login(request, user)
        tokens = AuthService.generate_tokens_for_user(user)

        # 🟢 SUCCÈS : Journalisation de la connexion réussie
        # request.user est maintenant valide grâce à django_login, le service va l'associer automatiquement
        AuditService.log(
            request,
            action=ActionAudit.CONNEXION,
            obj=user,
            details={"methode": "JWT / Coookie-based Auth"}
        )

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
