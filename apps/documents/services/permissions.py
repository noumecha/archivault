# apps/documents/services/permissions.py
from django.db.models import Q
from apps.documents.models import Document, NiveauAcces, DocumentPermission
from config.roles import *

class DocumentPermissionService:

    @staticmethod
    def get_visible_documents(user):
        """
        Retourne le queryset des documents visibles par l'utilisateur.
        """
        # Admin / Superadmin → tout voir
        if is_admin(user) or is_superadmin(user):
            return Document.objects.all()

        qs = Document.objects.all()

        # Superviseur → documents de sa cellule
        if is_superviseur(user): # Correction mineure pour utiliser ta fonction de rôle homogène
            return qs.filter(cellule=user.cellule)

        # Gestionnaire / Collaborateur / Utilisateur
        return qs.filter(
            Q(cellule=user.cellule) |
            Q(cree_par=user) |
            Q(permissions=user) |  # Inclus via le ManyToMany field
            Q(
                document_permissions__utilisateur=user,
                document_permissions__can_view=True
            )
        ).distinct()

    """ Permission check methods """

    @staticmethod
    def can_view(user, document):
        # 1. Privilèges de rôles ou structures globales
        if is_admin(user) or is_superadmin(user) or is_superviseur(user):
            return True

        if document.niveau_acces == NiveauAcces.PUBLIC:
            return True

        if document.cellule == user.cellule:
            return True

        if is_owner(user, document):
            return True

        # 2. Vérification de la permission granulaire (Tâches hors cellule / Partages explicites)
        return DocumentPermission.objects.filter(
            document=document,
            utilisateur=user,
            can_view=True
        ).exists()

    @staticmethod
    def can_download(user, document):
        # 1. Privilèges de rôles ou structures globales
        if is_admin(user) or is_superadmin(user) or is_superviseur(user):
            return True

        if document.profil_document in ['imprimable', 'modifiable']:
            return True

        if document.niveau_acces == NiveauAcces.PUBLIC:
            return True

        if is_owner(user, document):
            return True

        # 2. Vérification de la permission granulaire
        return DocumentPermission.objects.filter(
            document=document,
            utilisateur=user,
            can_download=True
        ).exists()

    @staticmethod
    def can_edit(user, document):
        # 1. Privilèges de rôles ou structures globales
        if is_admin(user) or is_superadmin(user):
            return True

        if document.niveau_acces == NiveauAcces.PUBLIC:
            return True

        # Un superviseur gère les modifications sur les documents de sa cellule
        if is_superviseur(user) and document.cellule == user.cellule:
            return True

        # 2. Vérification de la permission granulaire
        # Si une tâche lui a été assignée avec 'can_edit=True'
        if DocumentPermission.objects.filter(
            document=document,
            utilisateur=user,
            can_edit=True
        ).exists():
            return True

        # 3. Logique de repli sur le profil du document
        if document.profil_document != 'modifiable' and not DocumentPermissionService.can_download(user, document) and not is_owner(user, document):
            return False

        return (
            is_owner(user, document)
            or is_responsable(user)
        )

    @staticmethod
    def can_delete(user, document):
        if is_admin(user) or is_superadmin(user):
            return True

        if document.niveau_acces == NiveauAcces.PUBLIC:
            return True

        if is_superviseur(user) and document.cellule == user.cellule:
            return True

        if is_owner(user, document):
            return True

        # Vérification de la permission granulaire
        return DocumentPermission.objects.filter(
            document=document,
            utilisateur=user,
            can_delete=True
        ).exists()

    @staticmethod
    def can_share(user, document):
        if is_admin(user) or is_superadmin(user):
            return True

        if document.niveau_acces == NiveauAcces.PUBLIC:
            return True

        if is_superviseur(user) and user.cellule == document.cellule:
            return True

        if is_owner(user, document):
            return True

        # Vérification de la permission granulaire
        return DocumentPermission.objects.filter(
            document=document,
            utilisateur=user,
            can_share=True
        ).exists()
