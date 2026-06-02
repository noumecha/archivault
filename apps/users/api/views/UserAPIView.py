# apps/users/api/views/UserAPIView.py
from rest_framework.response import Response
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from config.api.base_api_view import BaseAPIView
from ...models import Utilisateur, RoleUtilisateur
from ...services.user_service import UserService
from apps.circulation.services.audit_service import AuditService
from apps.circulation.models import ActionAudit, StatutAudit
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from ..serializers import UtilisateurSerializer


class UserAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des utilisateurs.
    Remplace UserView (BaseCRUDView) en version full API.

    Endpoints :
        GET    /api/users/              → Liste (paginée, filtrée, recherchée)
        POST   /api/users/create         → Créer
        GET    /api/users/<id>/         → Détail
        PUT    /api/users/<id>/update    → Mise à jour complète
        PATCH  /api/users/<id>/update    → Mise à jour partielle
        DELETE /api/users/<id>/delete    → Supprimer
    """

    # ── Configuration du modèle ──────────────────────────────────────────────
    model = Utilisateur
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAuthenticated]

    # ── Recherche & Filtrage ─────────────────────────────────────────────────
    search_fields = ['username', 'first_name', 'last_name', 'email']
    filter_fields = ['role', 'cellule', 'is_active']  # Filtres exacts autorisés

    # ── Permissions ──────────────────────────────────────────────────────────
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # QUERYSET PERSONNALISÉ
    # ─────────────────────────────────────────────────────────────────────────
    def get_queryset(self):
        """
        Retourne le queryset selon le rôle de l'utilisateur.
        Utilise UserService pour la logique métier.
        """
        qs = UserService.get_users_queryset(self.request.user)
        return super().get_queryset(queryset=qs)

    # 👁️ Audit de la consultation de détail d'un compte utilisateur
    def retrieve_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        response = super().retrieve_action(request, pk, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            AuditService.log(
                request,
                action=ActionAudit.CONSULTATION,
                obj=instance,
                details={"contexte": "vue_detail_utilisateur"}
            )
        else:
            AuditService.log(
                request,
                action=ActionAudit.CONSULTATION,
                obj=instance,
                statut=StatutAudit.FAILED,
                details={"status_code": response.status_code}
            )
        return response

    # ─────────────────────────────────────────────────────────────────────────
    # OVERRIDE DES ACTIONS POUR AJOUTER DES PERMISSIONS ET L'AUDIT
    # ─────────────────────────────────────────────────────────────────────────
    def create_action(self, request, *args, **kwargs):
        """Création avec vérification du rôle."""
        self.check_role_permission(request)
        response = super().create_action(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            obj = self.model.objects.filter(id=response.data.get('id')).first()
            AuditService.log(request, ActionAudit.CREATION, obj=obj)
        else:
            AuditService.log(request, ActionAudit.CREATION, statut=StatutAudit.FAILED, details=response.data)
        return response

    def update_action(self, request, pk=None, *args, **kwargs):
        """Mise à jour avec vérification du rôle."""
        self.check_role_permission(request)
        instance = self.get_object()
        response = super().update_action(request, pk, *args, **kwargs)

        if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            AuditService.log(request, ActionAudit.MODIFICATION, obj=instance)
        else:
            AuditService.log(request, ActionAudit.MODIFICATION, obj=instance, statut=StatutAudit.FAILED, details=response.data)
        return response

    def delete_action(self, request, pk=None, *args, **kwargs):
        """Suppression avec vérification du rôle."""
        self.check_role_permission(request)
        instance = self.get_object()
        label_backup = f"[Utilisateur] {str(instance)}"

        response = super().delete_action(request, pk, *args, **kwargs)

        if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            AuditService.log(request, ActionAudit.SUPPRESSION, label=label_backup)
        else:
            AuditService.log(request, ActionAudit.SUPPRESSION, obj=instance, statut=StatutAudit.FAILED)
        return response

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS PERSONNALISÉES
    # ─────────────────────────────────────────────────────────────────────────
    custom_actions = {
        'toggle_status': 'action_toggle_status',
        'bulk_delete': 'action_bulk_delete',
        'bulk_toggle_status': 'action_bulk_toggle_status'
    }

    def action_bulk_toggle_status(self, request, *args, **kwargs):
        """Basculer le statut de plusieurs utilisateurs."""
        self.check_role_permission(request)

        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'success': False,
                'message': 'Aucun ID fourni'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                users = Utilisateur.objects.filter(id__in=ids)
                count = users.count()

                for user in users:
                    user.is_active = not user.is_active
                    user.save()

                AuditService.log(
                    request,
                    action=ActionAudit.MODIFICATION,
                    label=f"Modification en masse (Activation) de {count} utilisateur(s)",
                    details={"ids_cible": ids, "action": "toggle_is_active_bulk"}
                )

                return Response({
                    'success': True,
                    'message': f'Statut de {count} utilisateur(s) modifié(s)'
                })
        except Exception as e:
            AuditService.log(
                request,
                action=ActionAudit.MODIFICATION,
                statut=StatutAudit.FAILED,
                label="Échec de la modification de statut en masse des utilisateurs",
                details={"erreur": str(e), "ids_tentés": ids}
            )
            return Response({
                'success': False,
                'message': f'Erreur lors du traitement en masse : {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def action_toggle_status(self, request, pk=None, *args, **kwargs):
        """Basculer le statut d'un utilisateur."""
        self.check_role_permission(request)

        user = get_object_or_404(Utilisateur, pk=pk)
        old_status = user.is_active
        new_status = not old_status

        user.is_active = new_status
        user.save()

        serializer = self.get_serializer(user)

        AuditService.log(
            request,
            action=ActionAudit.MODIFICATION,
            obj=user,
            details={
                "champ": "is_active",
                "avant": old_status,
                "apres": new_status
            }
        )

        return Response({
            'success': True,
            'message': "Statut de l'utilisateur modifié avec succès",
            'data': serializer.data
        })

    def action_bulk_delete(self, request, *args, **kwargs):
        """Suppression en masse."""
        self.check_role_permission(request)

        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'success': False,
                'message': 'Aucun ID fourni'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                queryset = self.model.objects.filter(id__in=ids)
                count = queryset.count()

                AuditService.log(
                    request,
                    action=ActionAudit.SUPPRESSION_MASSE,
                    label=f"Suppression de {count} utilisateur(s)",
                    details={"ids_cible": ids}
                )

                queryset.delete()

                return Response({
                    'success': True,
                    'message': f'{count} utilisateur(s) supprimé(s)',
                    'deleted_count': count
                })
        except Exception as e:
            AuditService.log(
                request,
                action=ActionAudit.SUPPRESSION_MASSE,
                statut=StatutAudit.FAILED,
                details={"erreur": str(e), "ids_tentes": ids}
            )
            return Response({
                'success': False,
                'message': f'Erreur lors de la suppression en masse : {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
