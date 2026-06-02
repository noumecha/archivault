# apps/notifications/api/views/NotificationAPIView.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from .serializers import NotificationSerializer
from ..models import Notification
from config.api.base_api_view import BaseAPIView
from apps.users.models import RoleUtilisateur
from apps.circulation.services.audit_service import AuditService
from apps.circulation.models import ActionAudit, StatutAudit


class NotificationAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des notifications utilisateur.

    Endpoints :
        GET    /api/notifications/          → Liste des notifications de l'utilisateur
        PATCH  /api/notifications/<id>/read → Marquer une notification comme lue
        POST   /api/notifications/read-all  → Marquer toutes les notifications comme lues
        DELETE /api/notifications/<id>/     → Supprimer une notification
        POST   /api/notifications/bulk-delete → Supprimer plusieurs notifications en même temps
    """

    model = Notification
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    # ── Permissions ──────────────────────────────────────────────────────────
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.RESPONSABLE,
        RoleUtilisateur.GESTIONNAIRE
    ]

    # Filtrage et recherche
    filter_fields = ['is_read', 'categorie', 'priorite']
    search_fields = ['titre', 'message']

    def get_queryset(self):
        """L'utilisateur ne voit que ses propres notifications."""
        qs = Notification.objects.filter(destinataire=self.request.user)
        return super().get_queryset(queryset=qs)

    # 👁️ Audit de la consultation d'une notification (Détail)
    def retrieve_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        response = super().retrieve_action(request, pk, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            AuditService.log(
                request,
                action=ActionAudit.CONSULTATION,
                obj=instance,
                details={"contexte": "consultation_directe_notification"}
            )
        return response

    # ─────────────────────────────────────────────────────────────────────────
    # OVERRIDE DES ACTIONS POUR AJOUTER DES PERMISSIONS ET L'AUDIT
    # ─────────────────────────────────────────────────────────────────────────
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
        label_backup = f"[Notification] {instance.titre}"

        response = super().delete_action(request, pk, *args, **kwargs)

        if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            AuditService.log(request, ActionAudit.SUPPRESSION, label=label_backup, details={"notification_id": pk})
        else:
            AuditService.log(request, ActionAudit.SUPPRESSION, obj=instance, statut=StatutAudit.FAILED)
        return response

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS PERSONNALISÉES
    # ─────────────────────────────────────────────────────────────────────────
    custom_actions = {
        'mark_as_read': 'action_mark_as_read',
        'mark_all_as_read': 'action_mark_all_as_read',
        'unread_count': 'action_unread_count',
        'bulk_delete': 'action_bulk_delete',
    }

    def action_bulk_delete(self, request, *args, **kwargs):
        """Supprime plusieurs notifications en même temps."""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'success': False,
                'message': 'Aucun ID fourni'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # On cible uniquement les notifications de l'utilisateur pour sécurité
                queryset = self.get_queryset().filter(id__in=ids)
                count = queryset.count()

                AuditService.log(
                    request,
                    action=ActionAudit.SUPPRESSION_MASSE,
                    label=f"Suppression de {count} notification(s)",
                    details={"ids_cible": ids}
                )

                queryset.delete()

                return Response({
                    'success': True,
                    'message': f'{count} notification(s) supprimée(s)',
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

    def action_mark_as_read(self, request, pk=None, *args, **kwargs):
        """
        Marque une notification spécifique comme lue ET horodate la prise de connaissance
        de l'objet lié (Tâche/Circulation) pour le contrôle hiérarchique.
        """
        notification = get_object_or_404(self.get_queryset(), pk=pk)
        now = timezone.now()

        if not notification.is_read:
            notification.is_read = True
            notification.save()

            # 🟢 HISTORISATION ET CONTRÔLE HIÉRARCHIQUE VIA LE CONTENT_TYPE
            target_object = notification.content_object

            if target_object:
                # Cas 1 : C'est une Tâche
                if hasattr(target_object, 'date_premiere_consultation'):
                    if not target_object.date_premiere_consultation:
                        target_object.date_premiere_consultation = now
                    if hasattr(target_object, 'nb_consultations'):
                        target_object.nb_consultations += 1
                    target_object.save()

                    # Audit de la prise de connaissance de la tâche sous-jacente
                    AuditService.log(
                        request,
                        action=ActionAudit.MODIFICATION,
                        obj=target_object,
                        details={"evenement": "lecture_notification_tache", "notification_id": notification.id}
                    )

                # Cas 2 : C'est une Étape de Circulation
                elif target_object.__class__.__name__ == 'CirculationDocument':
                    # Log l'action de traitement / lecture du document lié
                    AuditService.log(
                        request,
                        action=ActionAudit.CONSULTATION,
                        obj=target_object,
                        details={"evenement": "lecture_notification_circulation", "notification_id": notification.id}
                    )

            # Log de la notification elle-même passée à l'état "lu"
            AuditService.log(
                request,
                action=ActionAudit.MODIFICATION,
                obj=notification,
                details={"champ": "is_read", "avant": False, "apres": True}
            )

        return Response({
            'success': True,
            'message': 'Notification consultée et traçabilité hiérarchique enregistrée',
            'data': self.get_serializer(notification).data
        })

    def action_mark_all_as_read(self, request, *args, **kwargs):
        """Marque toutes les notifications de l'utilisateur comme lues."""
        try:
            with transaction.atomic():
                unreads = self.get_queryset().filter(is_read=False)
                updated_count = unreads.count()

                if updated_count > 0:
                    unreads.update(is_read=True)

                    AuditService.log(
                        request,
                        action=ActionAudit.MODIFICATION,
                        label=f"Marquage en masse comme lu de {updated_count} notification(s)",
                        details={"action": "mark_all_as_read"}
                    )

                return Response({
                    'success': True,
                    'message': f'{updated_count} notifications marquées comme lues',
                    'updated_count': updated_count
                })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Erreur lors du traitement : {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def action_unread_count(self, request, *args, **kwargs):
        """Retourne le nombre de notifications non lues (Pas de log d'audit requis pour ce polling)."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({
            'success': True,
            'unread_count': count
        })
