# apps/documents/services/visibility_service.py
from config.roles import *
from django.db.models import Q

class VisibilityService:

    @staticmethod
    def filter_by_cellule(queryset, user, field_name='cellule'):
        if is_admin(user) or is_superadmin(user):
            return queryset

        return queryset.filter(**{field_name: user.cellule})

    @staticmethod
    def filter_by_cellule_or_generic(queryset, user):
        """
        Filtre un queryset pour inclure les éléments génériques
        + les éléments spécifiques à la cellule de l'utilisateur.
        """
        if not user.is_authenticated:
            return queryset.none()

        # Admins & Superadmins voient tout (génériques + toutes les cellules)
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            return queryset

        # Un utilisateur métier voit : Les génériques OU sa propre cellule
        if user.cellule_id:
            return queryset.filter(
                Q(cellule__isnull=True) | Q(cellule_id=user.cellule_id)
            )

        # Si l'utilisateur n'a pas de cellule, il ne voit que le générique
        return queryset.filter(cellule__isnull=True)
