from apps.users.models import RoleUtilisateur

""" Role helper methods """
@staticmethod
def is_admin(user):
    return user.role in  [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]

@staticmethod
def is_superviseur(user):
    return getattr(user, 'role', '') == RoleUtilisateur.SUPERVISEUR

@staticmethod
def is_owner(user, document):
    return document.cree_par == user

@staticmethod
def is_responsable(user, document):
    return document.responsable_document == user

@staticmethod
def is_superadmin(user):
    return user.role == RoleUtilisateur.SUPERADMIN
