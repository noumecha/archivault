# apps/documents/services/visibility_service.py
from config.roles import *
class VisibilityService:
    @staticmethod
    def filter_by_cellule(queryset, user, field_name='cellule'):
        if is_admin(user) or is_superadmin(user):
            return queryset

        return queryset.filter(**{field_name: user.cellule})
