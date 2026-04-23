# config/mixins/drf_permissions.py

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class RoleRequiredPermission(BasePermission):
    """
    Permission DRF pour vérifier les rôles autorisés.
    À utiliser avec les vues DRF (APIView, ViewSet, etc.)
    """

    allowed_roles = []  # À surcharger dans les sous-classes

    def has_permission(self, request, view):
        """Vérifie si l'utilisateur a un rôle autorisé."""
        if not request.user or not request.user.is_authenticated:
            return False

        # Si allowed_roles est vide → pas de restriction
        if not view.allowed_roles:
            return True

        # Vérifie le rôle de l'utilisateur
        user_role = getattr(request.user, 'role', None)
        return user_role in view.allowed_roles


class DRFRoleRequiredMixin:
    """
    Mixin pour les vues DRF qui ont besoin de vérifier les rôles.
    À utiliser avec BaseAPIView ou ViewSet.
    """

    allowed_roles = []

    def check_role_permission(self, request):
        """
        Vérifie les permissions de rôle.
        À appeler dans les actions qui nécessitent une vérification.
        """
        if not self.allowed_roles:
            return True

        user_role = getattr(request.user, 'role', None)
        if user_role not in self.allowed_roles:
            raise PermissionDenied(
                detail="Vous n'avez pas la permission d'effectuer cette action"
            )
        return True
