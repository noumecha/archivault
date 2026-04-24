from config.roles import *
from apps.users.models import Utilisateur, RoleUtilisateur
from django.db.models import Q

class UserService:
    @staticmethod
    def get_users_queryset(user):
        """
        Retourne le queryset des utilisateurs visibles par l'utilisateur actuel
        en fonction de son rôle.
        """
        qs = Utilisateur.objects.all()
        if is_superadmin(user):
            return qs
        elif is_admin(user):
            return qs.exclude(role=RoleUtilisateur.SUPERADMIN).exclude(
                Q(role=RoleUtilisateur.ADMIN)#& ~Q(id=user.id)
            )
        elif is_superviseur(user):
            return qs.filter(
                cellule=user.cellule,
                role__in=[RoleUtilisateur.GESTIONNAIRE, RoleUtilisateur.RESPONSABLE]
            )
        return qs.none()
