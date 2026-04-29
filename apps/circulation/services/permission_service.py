# apps/circulation/services/permission_service.py
from apps.users.models import RoleUtilisateur

class PermissionService:
    """
    Service pour gérer les permissions des tâches et circulations.
    """

    # Rôles autorisés à assigner des tâches
    ROLES_ASSIGNER_TACHE = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.GESTIONNAIRE,
    ]

    # Rôles autorisés à voir toutes les tâches
    ROLES_VOIR_TOUTES_TACHES = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.GESTIONNAIRE,
    ]

    # Rôles autorisés à créer des circulations
    ROLES_CREER_CIRCULATION = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.GESTIONNAIRE,
    ]

    @staticmethod
    def peut_assigner_tache(user):
        """Vérifier si l'utilisateur peut assigner des tâches."""
        return user.role in PermissionService.ROLES_ASSIGNER_TACHE

    @staticmethod
    def peut_voir_toutes_taches(user):
        """Vérifier si l'utilisateur peut voir toutes les tâches."""
        return user.role in PermissionService.ROLES_VOIR_TOUTES_TACHES

    @staticmethod
    def peut_creer_circulation(user):
        """Vérifier si l'utilisateur peut créer une circulation."""
        return user.role in PermissionService.ROLES_CREER_CIRCULATION

    @staticmethod
    def peut_valider_tache(user, tache):
        """Vérifier si l'utilisateur peut valider une tâche."""
        # Le créateur ou un superviseur peut valider
        # ou celui à qui on a assigner la tache
        return (
            user == tache.assignee_par or
            user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN, RoleUtilisateur.SUPERVISEUR] or
            user == tache.assignee_a
        )

    @staticmethod
    def peut_supprimer_tache(user, tache):
        """Vérifier si l'utilisateur peut supprimer une tâche."""
        # Le créateur ou un superviseur peut supprimer
        return (
            user == tache.assignee_par or
            user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]
        )

    @staticmethod
    def peut_voir_tache(user, tache):
        """ Peut voir une taches spécifique."""
        # Le créateur ou un superviseur peut voir
        # ou celui à qui on assigner la tache
        return (
            user == tache.assignee_par or
            user == tache.assignee_a or
            user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN, RoleUtilisateur.SUPERVISEUR]
        )
