# apps/users/api/views/LogoutAPIView.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout as django_logout
from apps.circulation.services.audit_service import AuditService
from apps.circulation.models import ActionAudit, StatutAudit

class LogoutAPIView(APIView):
    def post(self, request):
        if request.user and request.user.is_authenticated:
            AuditService.log(
                request,
                action=ActionAudit.DECONNEXION,
                obj=request.user,
                details={"contexte": "deconnexion_session_jwt"}
            )
        else:
            AuditService.log(
                request,
                action=ActionAudit.DECONNEXION,
                statut=StatutAudit.FAILED,
                label="Tentative de déconnexion d'un utilisateur non authentifié"
            )

        response = Response({"message": "Déconnexion réussie"}, status=status.HTTP_200_OK)
        django_logout(request)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response
