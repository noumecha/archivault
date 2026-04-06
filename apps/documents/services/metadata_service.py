from config.roles import *
from ..models import *

class DocumentMetadataService:

    @staticmethod
    def get_types(user):
        qs = TypeDocument.objects.all()
        if is_admin(user) or is_superadmin(user):
            return qs
        return qs.filter(cellule=user.cellule)

    @staticmethod
    def get_sous_types(user):
        qs = SousTypeDocument.objects.all()
        if is_admin(user) or is_superadmin(user):
            return qs
        return qs.filter(type_document__cellule=user.cellule)

    @staticmethod
    def get_themes(user):
        qs = Theme.objects.all()
        if is_admin(user) or is_superadmin(user):
            return qs
        return qs.filter(cellule=user.cellule)

    @staticmethod
    def get_bailleurs(user):
        qs = Bailleurs.objects.all()
        if is_admin(user) or is_superadmin(user):
            return qs
        return qs.filter(cellule=user.cellule)
