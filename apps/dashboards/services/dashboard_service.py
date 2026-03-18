from apps.documents.models import Document
from apps.users.models import RoleUtilisateur
from config.roles import *

class DashboardService:

    @staticmethod
    def get_dashboard_type(user):
        if is_admin(user) or is_superadmin(user):
            return "GLOBAL"
        if is_superviseur(user):
            return "CELLULE"
        return "USER"

    @staticmethod
    def get_documents_queryset(user):
        dashboard_type = DashboardService.get_dashboard_type(user)
        qs = Document.objects.all()
        if dashboard_type == "GLOBAL":
            return qs
        if dashboard_type == "CELLULE":
            return qs.filter(cellule=user.cellule)
        return qs.filter(cellule=user.cellule, cree_par=user)
