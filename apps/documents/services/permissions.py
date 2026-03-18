from django.db.models import Q
from apps.documents.models import Document
from config.roles import *

class DocumentPermissionService:

    @staticmethod
    def get_visible_documents(user):
        """
        Retourne le queryset des documents visibles par l'utilisateur
        """

        # Admin / Superadmin → tout voir
        if is_admin(user):
            return Document.objects.all()

        qs = Document.objects.all()

        # Superviseur → documents de sa cellule
        if user.role == 'superviseur':
            return qs.filter(cellule=user.cellule)

        # Gestionnaire / utilisateur
        print("user : ", {user})
        print("user.cellule : ", user.cellule)
        return qs.filter(
            Q(cellule=user.cellule) |
            Q(cree_par=user) |
            Q(document_permissions__utilisateur=user,
            document_permissions__can_view=True
        )
    ).distinct()

    """ Permission check methods """
    @staticmethod
    def can_view(user, document):
        if is_admin(user):
            return True

        if is_superviseur(user, document):
            return True

        if document.cellule == user.cellule:
            return True

        return document.permissions.filter(
            utilisateur=user,
            can_view=True
        ).exists()

    @staticmethod
    def can_download(user, document):
        if is_admin(user):
            return True

        if document.profil_document in ['imprimable', 'modifiable']:
            return True

        if is_superviseur(user, document):
            return True

        return is_owner(user, document)

    @staticmethod
    def can_edit(user, document):
        if is_admin(user):
            return True

        if is_superviseur(user, document):
            return True

        if document.profil_document != 'modifiable' and not DocumentPermissionService.can_download(user, document) and not is_owner(user, document):
            return False

        return (
            is_owner(user, document)
            or is_responsable(user, document)
        )

    @staticmethod
    def can_delete(user, document):
        if is_admin(user):
            return True

        return (
            is_admin(user) or is_superviseur(user, document)
            or is_owner(user, document)
        )

    @staticmethod
    def can_share(user, document):
        if is_admin(user):
            return True

        if user.role == 'superviseur' and user.cellule == document.cellule:
            return True

        return document.permissions.filter(
            utilisateur=user,
            can_share=True
        ).exists()
