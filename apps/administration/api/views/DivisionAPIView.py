# apps/administration/api/views/DivisionAPIView.py
from rest_framework.response import Response
from rest_framework import status
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from config.api.base_api_view import BaseAPIView
from ...models import *
from ..serializers import *
from apps.circulation.services.audit_service import AuditService
from apps.circulation.models import ActionAudit, StatutAudit
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction


class DivisionAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des divisions.
    Remplace DivisionView (BaseCRUDView) en version full API.

    Endpoints :
        GET    /api/divisions/                               → Liste (paginée, filtrée, recherchée)
        POST   /api/divisions/create                         → Créer
        GET    /api/divisions/<id>/                          → Détail
        PUT    /api/divisions/<id>/update                    → Mise à jour complète
        PATCH  /api/divisions/<id>/update                    → Mise à jour partielle
        DELETE /api/divisions/<id>/delete                    → Supprimer
        STATUS /api/divisions/toggle-status
        STATUS /api/divisions/bulk-toggle-status
    """

    # ── Configuration du modèle ──────────────────────────────────────────────
    model = Division
    serializer_class = DivisionSerializer
    permission_classes = [IsAuthenticated]

    # ── Recherche & Filtrage ─────────────────────────────────────────────────
    search_fields = ['nom', 'description_division']
    filter_fields = ['ministere','direction_generale']

    # ── Permissions ──────────────────────────────────────────────────────────
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # QUERYSET PERSONNALISÉ
    # ─────────────────────────────────────────────────────────────────────────
    def get_queryset(self):
        return super().get_queryset()

    def retrieve_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        response = super().retrieve_action(request, pk, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            AuditService.log(
                request,
                action=ActionAudit.CONSULTATION,
                obj=instance,
                details={"contexte": "vue_detail_division"}
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
        label_backup = f"[Division] {str(instance)}"

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
        """Basculer le statut de plusieurs divisions."""
        self.check_role_permission(request)

        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'success': False,
                'message': 'Aucun ID fourni'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                divisions = Division.objects.filter(id__in=ids)
                count = divisions.count()

                for division in divisions:
                    division.statut = not division.statut
                    division.save()

                AuditService.log(
                    request,
                    action=ActionAudit.MODIFICATION,
                    label=f"Modification en masse (Statut) de {count} division(s)",
                    details={"ids_cible": ids, "action": "toggle_status_bulk"}
                )

                return Response({
                    'success': True,
                    'message': f'Statut de {count} division(s) modifié(s)'
                })
        except Exception as e:
            AuditService.log(
                request,
                action=ActionAudit.MODIFICATION,
                statut=StatutAudit.FAILED,
                label="Échec modification en masse (Statut) des divisions",
                details={"erreur": str(e), "ids_tentés": ids}
            )
            return Response({
                'success': False,
                'message': f'Erreur lors du traitement en masse : {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def action_toggle_status(self, request, pk=None, *args, **kwargs):
        """Basculer le statut d'une division."""
        self.check_role_permission(request)

        division = get_object_or_404(Division, pk=pk)
        old_status = division.statut
        new_status = not old_status

        division.statut = new_status
        division.save()

        serializer = self.get_serializer(division)

        AuditService.log(
            request,
            action=ActionAudit.MODIFICATION,
            obj=division,
            details={
                "champ": "statut",
                "avant": old_status,
                "apres": new_status
            }
        )

        return Response({
            'success': True,
            'message': 'Statut de la division modifié avec succès',
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
                    label=f"Suppression de {count} division(s)",
                    details={"ids_cible": ids}
                )

                queryset.delete()

                return Response({
                    'success': True,
                    'message': f'{count} division(s) supprimée(s)',
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
