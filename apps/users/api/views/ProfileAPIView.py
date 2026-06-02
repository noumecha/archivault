# apps/users/api/views/ProfileAPIView.py
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout as django_logout
from config.api.base_api_view import BaseAPIView
from apps.circulation.services.audit_service import AuditService
from apps.circulation.models import ActionAudit, StatutAudit
from ..serializers import ChangePasswordSerializer, UtilisateurProfileSerializer

class ProfileAPIView(BaseAPIView):
    serializer_class = UtilisateurProfileSerializer
    custom_actions = {
        'update_profile': 'update_profile',
        'change_password': 'change_password',
    }

    def update_profile(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # 🟢 SUCCÈS : Journalisation de la mise à jour du profil
            AuditService.log(
                request,
                action=ActionAudit.MODIFICATION,
                obj=request.user,
                details={"action_profil": "mise_a_jour_informations"}
            )
            return Response({'success': True, 'message': 'Profil mis à jour'})

        # 🛑 ÉCHEC : Journalisation de l'erreur de modification
        AuditService.log(
            request,
            action=ActionAudit.MODIFICATION,
            obj=request.user,
            statut=StatutAudit.FAILED,
            details={"erreurs_validation": serializer.errors, "action_profil": "mise_a_jour_informations"}
        )
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get('old_password')):
                # 🛑 ÉCHEC : Ancien mot de passe erroné
                AuditService.log(
                    request,
                    action=ActionAudit.MODIFICATION,
                    obj=user,
                    statut=StatutAudit.FAILED,
                    details={"motif": "Ancien mot de passe incorrect", "action_profil": "changement_mot_de_passe"}
                )
                return Response({'old_password': ['Ancien mot de passe incorrect']}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.data.get('new_password'))
            user.save()

            # 🟢 SUCCÈS : Log enregistré impérativement AVANT la déconnexion (django_logout)
            AuditService.log(
                request,
                action=ActionAudit.MODIFICATION,
                obj=user,
                details={"action_profil": "changement_mot_de_passe_reussi", "evenement": "deconnexion_automatique"}
            )

            # Déconnexion de l'utilisateur suite au changement de mot de passe
            django_logout(request)
            return Response({
                'success': True,
                'message': 'Mot de passe modifié',
            })

        # 🛑 ÉCHEC : Formulaire ou critères de complexité du mot de passe invalides
        AuditService.log(
            request,
            action=ActionAudit.MODIFICATION,
            obj=request.user,
            statut=StatutAudit.FAILED,
            details={"erreurs_validation": serializer.errors, "action_profil": "changement_mot_de_passe"}
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
