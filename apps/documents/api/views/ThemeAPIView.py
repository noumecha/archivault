# apps/documents/api/views/ThemeAPIView.py
from rest_framework import status
from rest_framework.response import Response
from apps.documents.services.visibility_service import VisibilityService
from config.api.base_api_view import BaseAPIView
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from ...models import *
from rest_framework.permissions import IsAuthenticated
from ..serializers import *
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from apps.users.models import RoleUtilisateur
from apps.circulation.services.audit_service import AuditService
from apps.circulation.models import ActionAudit, StatutAudit

class ThemeAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des themes.

    Endpoints :

        GET    /api/themes/              → Liste (paginée, filtrée, recherchée)
        POST   /api/themes/create              → Créer
        GET    /api/themes/<id>/         → Détail
        PUT    /api/themes/<id>/update         → Mise à jour complète
        PATCH  /api/themes/<id>/update         → Mise à jour partielle
        DELETE /api/themes/<id>/delete         → Supprimer
    """

    # ── Configuration du modèle ──────────────────────────────────────────────
    model = Theme
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]

    # ── Recherche & Filtrage ─────────────────────────────────────────────────
    search_fields = ['libelle', 'description_theme']
    filter_fields = ['cellule']

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
        queryset = Theme.objects.select_related('cellule').all()
        qs = VisibilityService.filter_by_cellule_or_generic(queryset, self.request.user)
        return super().get_queryset(qs)

    def retrieve_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        response = super().retrieve_action(request, pk, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            AuditService.log(
                request,
                action=ActionAudit.CONSULTATION,
                obj=instance,
                details={"contexte": "vue_detail_theme"}
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
    # OVERRIDE DES ACTIONS POUR AJOUTER DES PERMISSIONS
    # ─────────────────────────────────────────────────────────────────────────
    def create_action(self, request, *args, **kwargs):
        """Création avec vérification du rôle et journalisation."""
        self.check_role_permission(request)

        if request.user.role not in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            request.data['cellule'] = request.user.cellule_id

        response = super().create_action(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            obj = self.model.objects.filter(id=response.data.get('id')).first()
            AuditService.log(request, ActionAudit.CREATION, obj=obj)
        else:
            AuditService.log(request, ActionAudit.CREATION, statut=StatutAudit.FAILED, details=response.data)
        return response

    def update_action(self, request, pk=None, *args, **kwargs):
        """Mise à jour avec vérification du rôle et journalisation."""
        self.check_role_permission(request)
        instance = self.get_object()
        response = super().update_action(request, pk, *args, **kwargs)

        if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            AuditService.log(request, ActionAudit.MODIFICATION, obj=instance)
        else:
            AuditService.log(request, ActionAudit.MODIFICATION, obj=instance, statut=StatutAudit.FAILED, details=response.data)
        return response

    def delete_action(self, request, pk=None, *args, **kwargs):
        """Suppression avec vérification du rôle et journalisation."""
        self.check_role_permission(request)
        instance = self.get_object()
        label_backup = f"[Thème] {str(instance)}"

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
        'bulk_delete': 'action_bulk_delete',
    }

    def action_bulk_delete(self, request, *args, **kwargs):
        """Suppression en masse avec atomicité et journalisation."""
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

                # Enregistrement du log de masse avant la purge
                AuditService.log(
                    request,
                    action=ActionAudit.SUPPRESSION_MASSE,
                    label=f"Suppression de {count} thème(s)",
                    details={"ids_cible": ids}
                )

                queryset.delete()

                return Response({
                    'success': True,
                    'message': f'{count} theme(s) supprimé(s)',
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
