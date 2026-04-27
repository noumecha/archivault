# apps/users/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import reverse, status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from apps.users.models import Utilisateur
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from config.api.base_api_view import BaseAPIView
from ..models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


class MinistereAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des ministères.
    Remplace MinistereView (BaseCRUDView) en version full API.

    Endpoints :
        GET    /api/ministeres/              → Liste (paginée, filtrée, recherchée)
        POST   /api/ministeres/create              → Créer
        GET    /api/ministeres/<id>/         → Détail
        PUT    /api/ministeres/<id>/update         → Mise à jour complète
        PATCH  /api/ministeres/<id>/update         → Mise à jour partielle
        DELETE /api/ministeres/<id>/delete         → Supprimer
    """

    # ── Configuration du modèle ──────────────────────────────────────────────
    model = Ministere
    serializer_class = MinistereSerializer
    permission_classes = [IsAuthenticated]

    # ── Recherche & Filtrage ─────────────────────────────────────────────────
    search_fields = ['nom', 'code', 'abrevation', 'description_ministere']
    filter_fields = []

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
    def create_action(self, request, *args, **kwargs):
        """Création avec vérification du rôle."""
        self.check_role_permission(request)
        return super().create_action(request, *args, **kwargs)

    def update_action(self, request, pk=None, *args, **kwargs):
        """Mise à jour avec vérification du rôle."""
        self.check_role_permission(request)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        """Suppression avec vérification du rôle."""
        self.check_role_permission(request)
        return super().delete_action(request, pk, *args, **kwargs)

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS PERSONNALISÉES
    # ─────────────────────────────────────────────────────────────────────────
    custom_actions = {
        'bulk_delete': 'action_bulk_delete',
    }

    def action_bulk_delete(self, request, *args, **kwargs):
        """Suppression en masse."""
        self.check_role_permission(request)

        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'success': False,
                'message': 'Aucun ID fourni'
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = Ministere.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} ministère(s) supprimé(s)',
            'deleted_count': deleted_count
        })

class DirectionGeneraleAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des directions générales.
    Remplace DirectionGeneraleView (BaseCRUDView) en version full API.

    Endpoints :
        GET    /api/directiongenerales/              → Liste (paginée, filtrée, recherchée)
        POST   /api/directiongenerales/create              → Créer
        GET    /api/directiongenerales/<id>/         → Détail
        PUT    /api/directiongenerales/<id>/update         → Mise à jour complète
        PATCH  /api/directiongenerales/<id>/update         → Mise à jour partielle
        DELETE /api/directiongenerales/<id>/delete         → Supprimer
    """

    # ── Configuration du modèle ──────────────────────────────────────────────
    model = DirectionGenerale
    serializer_class = DirectionGeneraleSerializer
    permission_classes = [IsAuthenticated]

    # ── Recherche & Filtrage ─────────────────────────────────────────────────
    search_fields = ['nom', 'description_direction_generale', 'ministere__nom']
    filter_fields = {
        'ministere': 'ministere',
    }

    # ── Permissions ──────────────────────────────────────────────────────────
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # QUERYSET PERSONNALISÉ
    # ─────────────────────────────────────────────────────────────────────────
    def get_queryset(self):
        base_qs = self.model.objects.select_related('ministere').all()
        return super().get_queryset(base_qs)

    # ─────────────────────────────────────────────────────────────────────────
    # OVERRIDE DES ACTIONS POUR AJOUTER DES PERMISSIONS
    # ─────────────────────────────────────────────────────────────────────────
    def create_action(self, request, *args, **kwargs):
        """Création avec vérification du rôle."""
        self.check_role_permission(request)
        return super().create_action(request, *args, **kwargs)

    def update_action(self, request, pk=None, *args, **kwargs):
        """Mise à jour avec vérification du rôle."""
        self.check_role_permission(request)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        """Suppression avec vérification du rôle."""
        self.check_role_permission(request)
        return super().delete_action(request, pk, *args, **kwargs)

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS PERSONNALISÉES
    # ─────────────────────────────────────────────────────────────────────────
    custom_actions = {
        'bulk_delete': 'action_bulk_delete',
    }

    def action_bulk_delete(self, request, *args, **kwargs):
        """Suppression en masse."""
        self.check_role_permission(request)

        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'success': False,
                'message': 'Aucun ID fourni'
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = DirectionGenerale.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} direction générale(s) supprimée(s)',
            'deleted_count': deleted_count
        })

class DivisionAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des divisions.
    Remplace DivisionView (BaseCRUDView) en version full API.

    Endpoints :
        GET    /api/divisions/              → Liste (paginée, filtrée, recherchée)
        POST   /api/divisions/create              → Créer
        GET    /api/divisions/<id>/         → Détail
        PUT    /api/divisions/<id>/update         → Mise à jour complète
        PATCH  /api/divisions/<id>/update         → Mise à jour partielle
        DELETE /api/divisions/<id>/delete         → Supprimer
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

    # ─────────────────────────────────────────────────────────────────────────
    # OVERRIDE DES ACTIONS POUR AJOUTER DES PERMISSIONS
    # ─────────────────────────────────────────────────────────────────────────
    def create_action(self, request, *args, **kwargs):
        """Création avec vérification du rôle."""
        self.check_role_permission(request)
        return super().create_action(request, *args, **kwargs)

    def update_action(self, request, pk=None, *args, **kwargs):
        """Mise à jour avec vérification du rôle."""
        self.check_role_permission(request)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        """Suppression avec vérification du rôle."""
        self.check_role_permission(request)
        return super().delete_action(request, pk, *args, **kwargs)

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

        divisions = Division.objects.filter(id__in=ids)
        for division in divisions:
            division.statut = not division.statut
            division.save()

        return Response({
            'success': True,
            'message': f'Statut de {divisions.count()} division(s) modifié(s)'
        })

    def action_toggle_status(self, request, pk=None, *args, **kwargs):
        """Basculer le statut d'une division."""
        self.check_role_permission(request)

        division = get_object_or_404(Division, pk=pk)
        new_status = False if division.statut == True else True
        division.statut = new_status
        division.save()

        serializer = self.get_serializer(division)
        return Response({
            'success': True,
            'message': f'Statut de la division modifié avec succès',
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

        deleted_count, _ = Division.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} division(s) supprimée(s)',
            'deleted_count': deleted_count
        })

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
    def create_action(self, request, *args, **kwargs):
        """Création avec vérification du rôle."""
        self.check_role_permission(request)
        return super().create_action(request, *args, **kwargs)

    def update_action(self, request, pk=None, *args, **kwargs):
        """Mise à jour avec vérification du rôle."""
        self.check_role_permission(request)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        """Suppression avec vérification du rôle."""
        self.check_role_permission(request)
        return super().delete_action(request, pk, *args, **kwargs)

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

        cellules = Cellule.objects.filter(id__in=ids)
        for cel in cellules:
            cel.accepte_bailleurs = not cel.accepte_bailleurs
            cel.save()

        return Response({
            'success': True,
            'message': f'{cellules.count()} unité(s) de traitement modifiée(s)'
        })

    def action_toggle_accepte_bailleurs(self, request, pk=None, *args, **kwargs):
        """Basculer le statut d'une cellule."""
        self.check_role_permission(request)

        cellule = get_object_or_404(Cellule, pk=pk)
        new_status = False if cellule.accepte_bailleurs == True else True
        cellule.accepte_bailleurs = new_status
        cellule.save()

        serializer = self.get_serializer(cellule)

        return Response({
            'success': True,
            'message': f'Statut de l\'unité de traitement (acceptation de bailleurs) modifié avec succès',
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

        deleted_count, _ = Cellule.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} unité(s) de traitement supprimée(s)',
            'deleted_count': deleted_count
        })
