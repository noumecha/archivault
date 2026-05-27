# apps/circulation/api/views/AuditLogAPIView.py
from datetime import timezone
from rest_framework.response import Response
from rest_framework import status
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from config.api.base_api_view import BaseAPIView
from ...models import RoleUtilisateur
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..serializers import *
from ...models import *
from datetime import timedelta
from apps.circulation.services.audit_service import AuditService

class AuditLogAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la consultation et la supervision du Journal d'Audit Système.

    Endpoints :
        GET    /api/audit/              → Liste des logs (paginée, filtrée, recherchée)
        GET    /api/audit/<id>/         → Détail complet d'un log d'audit
        POST   /api/audit/nettoyer/     → Action custom de purge (Optionnelle / SuperAdmin uniquement)
    """

    model = AuditLog
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    # ── Permissions strictes pour l'Audit ─────────────────────────────────────
    # Seuls les profils de supervision et d'administration ont accès aux logs
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]

    # ── Filtrage et recherche avancée ────────────────────────────────────────
    # Permet de filtrer par type d'action, par IP ou par succès/échec
    filter_fields = ['action', 'statut', 'ip_address', 'utilisateur']
    search_fields = ['objet_label', 'user_agent', 'utilisateur__username', 'utilisateur__first_name', 'utilisateur__last_name']

    def get_queryset(self):
        """
        Optimisation du QuerySet pour l'audit.
        Utilise select_related pour éviter le problème de requêtes N+1 avec l'utilisateur et le content_type.
        """
        qs = AuditLog.objects.select_related('utilisateur', 'content_type')

        # Exemple de filtre custom par plage de date si passé en paramètre d'URL (?jours=7)
        jours = self.request.GET.get('jours')
        if jours and jours.isdigit():
            date_limite = timezone.now() - timedelta(days=int(jours))
            qs = qs.filter(timestamp__gte=date_limite)

        return super().get_queryset(queryset=qs)

    # ── Sécurisation des actions CRUD standards ────────────────────────────────
    # On bloque explicitement les modifications et suppressions standards via l'API.

    def create_action(self, request, *args, **kwargs):
        return Response(
            {'success': False, 'message': 'Action interdite : Les logs d\'audit ne peuvent pas être créés manuellement.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def update_action(self, request, pk=None, *args, **kwargs):
        return Response(
            {'success': False, 'message': 'Action interdite : Un journal d\'audit est inaltérable.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def delete_action(self, request, pk=None, *args, **kwargs):
        return Response(
            {'success': False, 'message': 'Action interdite : Suppression individuelle de log impossible.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    # ── Actions Spécifiques (Custom) ─────────────────────────────────────────
    custom_actions = {
        'purger_logs': 'action_purger_logs',
    }

    def action_purger_logs(self, request, *args, **kwargs):
        """
        Action de maintenance : Permet de purger les logs de plus de X mois.
        Accessible UNIQUEMENT par le SUPERADMIN.
        """
        if request.user.role != RoleUtilisateur.SUPERADMIN:
            return Response(
                {'success': False, 'message': 'Droits insuffisants pour effectuer cette opération de maintenance.'},
                status=status.HTTP_403_FORBIDDEN
            )

        mois = request.data.get('mois_conservation', 6) # Par défaut 6 mois de rétention
        try:
            mois = int(mois)
            date_limite = timezone.now() - timedelta(days=mois * 30)

            # Suppression des vieux logs
            deleted_count, _ = AuditLog.objects.filter(timestamp__lt=date_limite).delete()

            return Response({
                'success': True,
                'message': f'Purge effectuée avec succès. {deleted_count} anciens logs supprimés.',
                'deleted_count': deleted_count
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response(
                {'success': False, 'message': 'Le paramètre mois_conservation doit être un entier valide.'},
                status=status.HTTP_400_BAD_REQUEST
            )
