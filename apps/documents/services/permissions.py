from django.db.models import Q
from apps.documents.models import Document

class DocumentPermissionService:

    @staticmethod
    def get_visible_documents(user):
        """
        Retourne le queryset des documents visibles par l'utilisateur
        """

        # Admin / Superadmin → tout voir
        if DocumentPermissionService.is_admin(user):
            return Document.objects.all()

        qs = Document.objects.all()

        # Superviseur → documents de sa cellule
        if user.role == 'superviseur':
            return qs.filter(cellule=user.cellule)

        # Gestionnaire / utilisateur
        return qs.filter(
            Q(cellule=user.cellule) |                 # Documents de sa cellule
            Q(cree_par=user) |                        # Documents qu'il a créés
            Q(permissions__utilisateur=user,          # Documents explicitement partagés
                permissions__can_view=True)
        ).distinct()

    """ Role helper methods """
    @staticmethod
    def is_admin(user):
        return user.is_superuser or getattr(user, 'role', '') in ['administrateur', 'superadmin']

    @staticmethod
    def is_superviseur(user, document):
        return getattr(user, 'role', '') == 'superviseur' and user.cellule == document.cellule

    @staticmethod
    def is_owner(user, document):
        return document.cree_par == user

    @staticmethod
    def is_responsable(user, document):
        return document.responsable_document == user

    """ Permission check methods """
    @staticmethod
    def can_view(user, document):
        if DocumentPermissionService.is_admin(user):
            return True

        if DocumentPermissionService.is_superviseur(user, document):
            return True

        if document.cellule == user.cellule:
            return True

        return document.permissions.filter(
            utilisateur=user,
            can_view=True
        ).exists()

    @staticmethod
    def can_download(user, document):
        if DocumentPermissionService.is_admin(user):
            return True

        if document.profil_document in ['imprimable', 'modifiable']:
            return True

        if DocumentPermissionService.is_superviseur(user, document):
            return True

        return DocumentPermissionService.is_owner(user, document)

    @staticmethod
    def can_edit(user, document):
        if DocumentPermissionService.is_admin(user):
            return True

        if DocumentPermissionService.is_superviseur(user, document):
            return True

        if document.profil_document != 'modifiable' and not DocumentPermissionService.can_download(user, document) and not DocumentPermissionService.is_owner(user, document):
            return False

        return (
            DocumentPermissionService.is_owner(user, document)
            or DocumentPermissionService.is_responsable(user, document)
        )

    @staticmethod
    def can_delete(user, document):
        if DocumentPermissionService.is_admin(user):
            return True

        return (
            DocumentPermissionService.is_admin(user) or DocumentPermissionService.is_superviseur(user, document)
            or DocumentPermissionService.is_owner(user, document)
        )

    @staticmethod
    def can_share(user, document):
        if DocumentPermissionService.is_admin(user):
            return True

        if user.role == 'superviseur' and user.cellule == document.cellule:
            return True

        return document.permissions.filter(
            utilisateur=user,
            can_share=True
        ).exists()
