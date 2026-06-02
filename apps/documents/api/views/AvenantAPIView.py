# apps/documents/api/views/AvenantAPIView.py
from rest_framework import status
from rest_framework.response import Response
from apps.documents.services.visibility_service import VisibilityService
from config.api.base_api_view import BaseAPIView
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from ...models import *
from rest_framework.permissions import IsAuthenticated
from ..serializers import *
from rest_framework import status
from rest_framework.response import Response
from django.db import transaction
from apps.users.models import RoleUtilisateur
from apps.circulation.services.audit_service import AuditService
from apps.circulation.models import ActionAudit, StatutAudit

class AvenantAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """API pour la gestion des avenants.

    Endpoints :

        GET    /api/avenants/              → Liste (paginée, filtrée, recherchée)
        POST   /api/avenants/create              → Créer
        GET    /api/avenants/<id>/         → Détail
        PUT    /api/avenants/<id>/update         → Mise à jour complète
        PATCH  /api/avenants/<id>/update         → Mise à jour partielle
        DELETE /api/avenants/<id>/delete         → Supprimer
    """
    model = Avenants
    serializer_class = AvenantSerializer
    permission_classes = [IsAuthenticated]

    search_fields = ['libelle', 'numero']
    filter_fields = ['bailleur']

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]

    def get_queryset(self):
        # Filtrage indirect : Avenant -> Bailleur -> Cellule
        base_qs = self.model.objects.select_related('bailleur__cellule').all()
        filtered_qs = VisibilityService.filter_by_cellule(
            base_qs,
            self.request.user,
            field_name='bailleur__cellule'
        )
        return super().get_queryset(filtered_qs)

    def retrieve_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        response = super().retrieve_action(request, pk, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            AuditService.log(
                request,
                action=ActionAudit.CONSULTATION,
                obj=instance,
                details={"contexte": "vue_detail_avenant"}
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
        self.check_role_permission(request)
        response = super().create_action(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            obj = self.model.objects.filter(id=response.data.get('id')).first()
            AuditService.log(request, ActionAudit.CREATION, obj=obj)
        else:
            AuditService.log(request, ActionAudit.CREATION, statut=StatutAudit.FAILED, details=response.data)
        return response

    def update_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        instance = self.get_object()
        response = super().update_action(request, pk, *args, **kwargs)
        if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            AuditService.log(request, ActionAudit.MODIFICATION, obj=instance)
        else:
            AuditService.log(request, ActionAudit.MODIFICATION, obj=instance, statut=StatutAudit.FAILED, details=response.data)
        return response

    def delete_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        instance = self.get_object()
        label_backup = f"[Avenant] {str(instance)}"
        response = super().delete_action(request, pk, *args, **kwargs)
        if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            AuditService.log(request, ActionAudit.SUPPRESSION, label=label_backup)
        else:
            AuditService.log(request, ActionAudit.SUPPRESSION, obj=instance, statut=StatutAudit.FAILED)
        return response

    custom_actions = {
        'bulk_delete': 'action_bulk_delete',
    }

    def action_bulk_delete(self, request, *args, **kwargs):
        self.check_role_permission(request)
        ids = request.data.get('ids', [])

        if not ids:
            return Response({'success': False, 'message': 'Aucun ID fourni'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                queryset = self.model.objects.filter(id__in=ids)
                count = queryset.count()

                # Audit avant suppression pour garder une trace des IDs
                AuditService.log(
                    request,
                    action=ActionAudit.SUPPRESSION_MASSE,
                    label=f"Suppression de {count} avenant(s)",
                    details={"ids_cible": ids}
                )

                queryset.delete()

                return Response({
                    'success': True,
                    'message': f'{count} avenant(s) supprimé(s)',
                    'deleted_count': count
                })
        except Exception as e:
            AuditService.log(
                request,
                action=ActionAudit.SUPPRESSION_MASSE,
                statut=StatutAudit.FAILED,
                details={"erreur": str(e), "ids_tentés": ids}
            )
            return Response({
                'success': False,
                'message': f'Erreur lors de la suppression : {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
