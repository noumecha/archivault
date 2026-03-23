from config.roles import *

class VisibilityService:
    @staticmethod
    def filter_by_cellule(queryset, user):

        if is_admin(user) or is_superadmin(user):
            return queryset

        return queryset.filter(cellule=user.cellule)
