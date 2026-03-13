from apps.documents.models import Document
from apps.users.models import RoleUtilisateur

class DashboardService:

    @staticmethod
    def get_dashboard_type(user):

        if user.role in [
            RoleUtilisateur.SUPERADMIN,
            RoleUtilisateur.ADMIN
        ]:
            return "GLOBAL"

        if user.role == RoleUtilisateur.SUPERVISEUR:
            return "CELLULE"

        return "USER"


    @staticmethod
    def get_documents_queryset(user):

        dashboard_type = DashboardService.get_dashboard_type(user)

        if dashboard_type == "GLOBAL":
            return Document.objects.all()

        if dashboard_type == "CELLULE":
            return Document.objects.filter(cellule=user.cellule)

        return Document.objects.filter(
            cellule=user.cellule,
            cree_par=user
        )
