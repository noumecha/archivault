# apps/administration/api/views/CelluleAPIView.py
from rest_framework.response import Response
from rest_framework import status
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from config.api.base_api_view import BaseAPIView
from ...models import *
from django.db import transaction
from apps.circulation.services.audit_service import AuditService
from apps.circulation.models import ActionAudit, StatutAudit
from ..serializers import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


class CelluleAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des cellules.
    Remplace CelluleView (BaseCRUDView) en version full API.

    Endpoints :

        GET    /api/cellules/              → Liste (paginée, filtrée, recherchée)
        POST   /api/cellules/create              → Créer
        GET    /api/cellules/<id>/         → Détail
        PUT    /api/cellules/<id>/update         → Mise à jour complète
        PATCH  /api/cellules/<id>/update         → Mise à jour partielle
        DELETE /api/cellules/<id>/delete         → Supprimer
        STATUS BAILLEUR TOGGLE /api/cellules/<id>/toggle-accepte-bailleurs      → Changer le status d'acceptation de bailleur
        BULK STATUS BAILLEUR TOGGLE /api/cellules/bulk-toggle-accepte-bailleurs     → Changer le status d'acceptation de bailleur de plusieurs cellules
    """

    # ── Configuration du modèle ──────────────────────────────────────────────
    model = Cellule
    serializer_class = CelluleSerializer
    permission_classes = [IsAuthenticated]

    # ── Recherche & Filtrage ─────────────────────────────────────────────────
    search_fields = ['nom', 'description_cellule']
    filter_fields = ['division']

    # ── Permissions ──────────────────────────────────────────────────────────
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # QUERYSET PERSONNALISÉ
    # ─────────────────────────────────────────────────────────────────────────
    def get_queryset(self):
        return super().get_queryset()

    # ─────────────────────────────────────────────────────────────────────────
    # OVERRIDE DES ACTIONS POUR AJOUTER DES PERMISSIONS
    # ─────────────────────────────────────────────────────────────────────────
    # 👁️ Audit de la consultation de détail
    def retrieve_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        response = super().retrieve_action(request, pk, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            AuditService.log(
                request,
                action=ActionAudit.CONSULTATION,
                obj=instance,
                details={"contexte": "vue_detail_cellule"}
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
        label_backup = f"[Cellule] {str(instance)}"

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
        'toggle_accepte_bailleurs': 'action_toggle_accepte_bailleurs',
        'bulk_toggle_accepte_bailleurs': 'action_bulk_toggle_accepte_bailleurs'
    }

    def action_bulk_toggle_accepte_bailleurs(self, request, *args, **kwargs):
        """Basculer le statut de plusieurs cellules."""
        self.check_role_permission(request)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'success': False,
                'message': 'Aucun ID fourni'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                cellules = Cellule.objects.filter(id__in=ids)
                count = cellules.count()

                for cel in cellules:
                    cel.accepte_bailleurs = not cel.accepte_bailleurs
                    cel.save()

                AuditService.log(
                    request,
                    action=ActionAudit.MODIFICATION,
                    label=f"Modification en masse (Bailleurs) de {count} unité(s) de traitement",
                    details={"ids_cible": ids, "action": "toggle_accepte_bailleurs_bulk"}
                )

                return Response({
                    'success': True,
                    'message': f'{count} unité(s) de traitement modifiée(s)'
                })
        except Exception as e:
            AuditService.log(
                request,
                action=ActionAudit.MODIFICATION,
                statut=StatutAudit.FAILED,
                label="Échec modification en masse (Bailleurs) des unités de traitement",
                details={"erreur": str(e), "ids_tentés": ids}
            )
            return Response({
                'success': False,
                'message': f'Erreur lors du traitement en masse : {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def action_toggle_accepte_bailleurs(self, request, pk=None, *args, **kwargs):
        """Basculer le statut d'une cellule."""
        self.check_role_permission(request)

        cellule = get_object_or_404(Cellule, pk=pk)
        old_status = cellule.accepte_bailleurs
        new_status = not old_status

        cellule.accepte_bailleurs = new_status
        cellule.save()

        serializer = self.get_serializer(cellule)

        # Log du changement unitaire de statut
        AuditService.log(
            request,
            action=ActionAudit.MODIFICATION,
            obj=cellule,
            details={
                "champ": "accepte_bailleurs",
                "avant": old_status,
                "apres": new_status
            }
        )

        return Response({
            'success': True,
            'message': "Statut de l'unité de traitement (acceptation de bailleurs) modifié avec succès",
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
                    label=f"Suppression de {count} unité(s) de traitement",
                    details={"ids_cible": ids}
                )

                queryset.delete()

                return Response({
                    'success': True,
                    'message': f'{count} unité(s) de traitement supprimée(s)',
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
