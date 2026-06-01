# apps/documents/api/views/TypeDocumentAPIView.py
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
from apps.users.models import RoleUtilisateur
from apps.circulation.services.audit_service import AuditService
from django.db import transaction
from apps.circulation.models import ActionAudit, StatutAudit

class TypeDocumentAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des types de documents.

    Endpoints :

        GET    /api/typedocuments/              → Liste (paginée, filtrée, recherchée)
        POST   /api/typedocuments/create              → Créer
        GET    /api/typedocuments/<id>/         → Détail
        PUT    /api/typedocuments/<id>/update         → Mise à jour complète
        PATCH  /api/typedocuments/<id>/update         → Mise à jour partielle
        DELETE /api/typedocuments/<id>/delete         → Supprimer
    """
    model = TypeDocument
    serializer_class = TypeDocumentSerializer
    permission_classes = [IsAuthenticated]

    search_fields = ['libelle', 'description_typedocument']
    filter_fields = ['cellule', 'parent_type']

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]

    def get_queryset(self):
        queryset = TypeDocument.objects.select_related('cellule', 'parent_type').all()
        qs = VisibilityService.filter_by_cellule(queryset, self.request.user)
        return super().get_queryset(qs)

    def retrieve_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        response = super().retrieve_action(request, pk, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            AuditService.log(
                request,
                action=ActionAudit.CONSULTATION,
                obj=instance,
                details={"contexte": "vue_detail_type_document"}
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
        label_backup = f"[Type Document] {str(instance)}"

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

                # Enregistrement du log de masse avant le nettoyage en DB
                AuditService.log(
                    request,
                    action=ActionAudit.SUPPRESSION_MASSE,
                    label=f"Suppression de {count} type(s) de document",
                    details={"ids_cible": ids}
                )

                queryset.delete()

                return Response({
                    'success': True,
                    'message': f'{count} type(s) supprimé(s)',
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
