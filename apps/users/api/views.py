# apps/users/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from ..services.auth_service import AuthService
from config.api.base_api_view import BaseAPIView
from ..models import Utilisateur, RoleUtilisateur
from ..services.user_service import UserService
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import UtilisateurSerializer

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("request.data : ", request.data)
        username = request.data.get("username")
        password = request.data.get("password")

        user = AuthService.authenticate_user(username, password)
        if not user:
            return Response({"error": "Identifiants invalides"}, status=status.HTTP_401_UNAUTHORIZED)

        django_login(request, user)
        tokens = AuthService.generate_tokens_for_user(user)

        response = Response({
            "message": "Connexion réussie",
            "user": {"id": user.id, "username": user.username, "role": user.role} # Optionnel pour le mobile
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            'access_token', tokens['access'],
            httponly=True, secure=not settings.DEBUG, samesite='Lax'
        )
        response.set_cookie(
            'refresh_token', tokens['refresh'],
            httponly=True, secure=not settings.DEBUG, samesite='Lax'
        )
        response.data['tokens'] = tokens

        return response

class LogoutAPIView(APIView):
    def post(self, request):
        response = Response({"message": "Déconnexion réussie"}, status=status.HTTP_200_OK)
        # Supprimer les cookies côté client
        django_logout(request)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

class UserAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des utilisateurs.
    Remplace UserView (BaseCRUDView) en version full API.

    Endpoints :
        GET    /api/users/              → Liste (paginée, filtrée, recherchée)
        POST   /api/users/create              → Créer
        GET    /api/users/<id>/         → Détail
        PUT    /api/users/<id>/update         → Mise à jour complète
        PATCH  /api/users/<id>/update         → Mise à jour partielle
        DELETE /api/users/<id>/delete         → Supprimer
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
        # Récupère le queryset de base selon les permissions
        qs = UserService.get_users_queryset(self.request.user)

        # Applique les filtres et recherche (hérité de BaseAPIView)
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
    }

    def action_toggle_status(self, request, pk=None, *args, **kwargs):
        """Basculer le statut d'un utilisateur."""
        self.check_role_permission(request)

        user = get_object_or_404(Utilisateur, pk=pk)
        new_status = False if user.is_active == True else True
        user.is_active = new_status
        user.save()

        serializer = self.get_serializer(user)
        return Response({
            'success': True,
            'message': f'Statut de l\'utilisateur modifié avec succès',
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

        deleted_count, _ = Utilisateur.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} utilisateur(s) supprimé(s)',
            'deleted_count': deleted_count
        })
