from apps.users.models import RoleUtilisateur

""" Role helper methods """
@staticmethod
def is_admin(user):
    return user.role in  [RoleUtilisateur.ADMIN]

@staticmethod
def is_superviseur(user):
    return getattr(user, 'role', '') == RoleUtilisateur.SUPERVISEUR

@staticmethod
def is_owner(user, document):
    return document.cree_par == user

@staticmethod
def is_responsable(user):
    return user.role == RoleUtilisateur.RESPONSABLE

@staticmethod
def is_superadmin(user):
    return user.role == RoleUtilisateur.SUPERADMIN

@staticmethod
def is_gestionnaire(user):
    return user.role == RoleUtilisateur.GESTIONNAIRE
