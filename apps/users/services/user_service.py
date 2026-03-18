from config.roles import *
from apps.users.models import Utilisateur, RoleUtilisateur

class UserService:
    @staticmethod
    def get_users_queryset(user):
        """
        Retourne le queryset des utilisateurs visibles par l'utilisateur actuel
        en fonction de son rôle.
        """
        qs = Utilisateur.objects.all()

        if is_admin(user) or is_superadmin(user):
            return qs

        if is_superviseur(user):
            return qs.filter(cellule=user.cellule)

        return qs.none()
