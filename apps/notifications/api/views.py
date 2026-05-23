from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from .serializers import NotificationSerializer
from ..models import Notification
from config.api.base_api_view import BaseAPIView
from apps.users.models import RoleUtilisateur

class NotificationAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des notifications utilisateur.

    Endpoints :
        GET    /api/notifications/          → Liste des notifications de l'utilisateur
        PATCH  /api/notifications/<id>/read → Marquer une notification comme lue
        POST   /api/notifications/read-all  → Marquer toutes les notifications comme lues
        DELETE /api/notifications/<id>/     → Supprimer une notification
        POST /api/notifications/bulk-delete → Supprimer plusieurs notifications en même temps
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

    # ─────────────────────────────────────────────────────────────────────────
    # OVERRIDE DES ACTIONS POUR AJOUTER DES PERMISSIONS
    # ─────────────────────────────────────────────────────────────────────────
    def create_action(self, request, *args, **kwargs):
        self.check_role_permission(request)
        return super().create_action(request, *args, **kwargs)

    def update_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        return super().delete_action(request, pk, *args, **kwargs)

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

        deleted_count, _ = Notification.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} notifications(s) supprimé(s)',
            'deleted_count': deleted_count
        })

    def action_mark_as_read(self, request, pk=None, *args, **kwargs):
        """Marque une notification spécifique comme lue."""
        notification = get_object_or_404(self.get_queryset(), pk=pk)
        if not notification.is_read:
            notification.is_read = True
            notification.save()

        return Response({
            'success': True,
            'message': 'Notification marquée comme lue',
            'data': self.get_serializer(notification).data
        })

    """def action_mark_as_read(self, request, pk=None, *args, **kwargs):
        #Marque une notification spécifique comme lue ET crée un suivi.
        notification = get_object_or_404(self.get_queryset(), pk=pk)

        if not notification.is_read:
            notification.is_read = True
            notification.save()

            Notification.objects.create(
                destinataire=request.user, # Ou un autre acteur (ex: admin, ou champ 'expediteur' si existant)
                titre="Suivi : Notification lue",
                message=f"Vous avez pris connaissance de la notification : '{notification.titre}' le {timezone.now().strftime('%d/%m/%m à %H:%M')}.",
                categorie=Notification.Category.SYSTEME,
                content_object=notification.content_object,
                is_read=True
            )

        return Response({
            'success': True,
            'message': 'Notification marquée comme lue et suivi enregistré',
            'data': self.get_serializer(notification).data
        })"""

    def action_mark_all_as_read(self, request, *args, **kwargs):
        """Marque toutes les notifications de l'utilisateur comme lues."""
        updated_count = self.get_queryset().filter(is_read=False).update(is_read=True)

        return Response({
            'success': True,
            'message': f'{updated_count} notifications marquées comme lues',
            'updated_count': updated_count
        })

    def action_unread_count(self, request, *args, **kwargs):
        """Retourne le nombre de notifications non lues (pour le badge de la sidebar)."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({
            'success': True,
            'unread_count': count
        })
