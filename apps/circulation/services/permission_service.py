# apps/circulation/services/permission_service.py
from apps.users.models import RoleUtilisateur

class PermissionService:
    """
    Service pour gérer les permissions des tâches et circulations.
    """

    # Rôles autorisés à assigner des tâches
    ROLES_ASSIGN_TASK = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.GESTIONNAIRE,
    ]

    # Rôles autorisés à voir toutes les tâches
    ROLES_VIEW_TASK = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.GESTIONNAIRE,
    ]

    # Rôles autorisés à créer des circulations
    ROLES_CREATE_CIRCULATION = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.GESTIONNAIRE,
    ]

    """ Circulations """
    @staticmethod
    def peut_creer_circulation(user):
        """Vérifier si l'utilisateur peut créer une circulation."""
        return user.role in PermissionService.ROLES_CREER_CIRCULATION

    @staticmethod
    def can_update_circulation(user, circulation):
        """Vérifier si l'utilisateur peut mettre à jour une circulation."""
        # Seul le créateur ou un superviseur peut mettre à jour
        return (
            user == circulation.initie_par or
            user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN] or
            user.role in [RoleUtilisateur.SUPERVISEUR] and user.cellule == circulation.document.cellule
        )

    @staticmethod
    def can_delete_circulation(user, circulation):
        """Vérifier si l'utilisateur peut supprimer une circulation."""
        # Seul le créateur ou un superviseur peut supprimer
        return (
            user == circulation.initie_par or
            user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN] or
            user.role in [RoleUtilisateur.SUPERVISEUR] and user.cellule == circulation.document.cellule
        )

    """ Tâches """
    @staticmethod
    def can_assign_task(user):
        """Vérifier si l'utilisateur peut assigner des tâches."""
        return user.role in PermissionService.ROLES_ASSIGN_TASK

    @staticmethod
    def can_view_tasks(user):
        """Vérifier si l'utilisateur peut voir toutes les tâches."""
        return user.role in PermissionService.ROLES_VIEW_TASK

    @staticmethod
    def can_edit_task(user, tache):
        """ Seul le créateur ou un superviseur peut éditer une tâche """
        return (
            user == tache.assignee_par or
            user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN, RoleUtilisateur.SUPERVISEUR]
        )

    @staticmethod
    def can_validate_task(user, tache):
        """Vérifier si l'utilisateur peut valider une tâche."""
        # Le créateur ou un superviseur peut valider
        # ou celui à qui on a assigner la tache
        return (
            user == tache.assignee_par or
            user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN, RoleUtilisateur.SUPERVISEUR] or
            user == tache.assignee_a
        )

    @staticmethod
    def can_delete_task(user, tache):
        """Vérifier si l'utilisateur peut supprimer une tâche."""
        # Le créateur ou un superviseur peut supprimer
        return (
            user == tache.assignee_par or
            user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]
        )

    @staticmethod
    def can_view_task(user, tache):
        """ Peut voir une taches spécifique."""
        # Le créateur ou un superviseur peut voir
        # ou celui à qui on assigner la tache
        return (
            user == tache.assignee_par or
            user == tache.assignee_a or
            user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN, RoleUtilisateur.SUPERVISEUR]
        )
