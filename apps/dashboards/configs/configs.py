from apps.users.models import RoleUtilisateur

DASHBOARD_CONFIG = {
    RoleUtilisateur.SUPERADMIN: [
        "system_stats",
        "cellules",
        "utilisateurs",
        "documents",
        "configs",
    ],
    RoleUtilisateur.ADMIN: [
        "system_stats",
        "cellules",
        "utilisateurs",
        "documents",
    ],
    RoleUtilisateur.SUPERVISEUR: [
        "cellule_stats",
        "cellule_documents",
        "cellule_users",
    ],
    RoleUtilisateur.GESTIONNAIRE: [
        "my_documents",
        "my_tasks",
    ],
    RoleUtilisateur.RESPONSABLE: [
        "my_documents",
    ],
}
