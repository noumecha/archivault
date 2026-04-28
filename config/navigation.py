SIDEBAR_MENU = [
    {
        "title": "Accueil",
        "icon": "ri-home-smile-line",
        "url_name": "index",
        "roles": ["superadmin", "administrateur", "superviseur", "gestionnaire", "responsable"],
        "url_prefix": "/dashboard/",
    },
    # CIRCULATION
    {
        "header": "Circulation & Tâches",
        "roles": ["superadmin", "administrateur", "superviseur", "gestionnaire", "responsable"],
    },
    {
        "title": "Circulation",
        "icon": "ri-file-list-3-fill",
        "url_prefix": "/circulation/",
        "roles": ["superadmin", "administrateur", "superviseur", "gestionnaire", "responsable"],
        "children": [
            {
                "title": "Circulations",
                "url_prefix": "/circulation/circulations/",
                "url_name": "circulation_list",
                "roles": ["superadmin", "administrateur", "superviseur"],
            },
            {
                "title": "Mes tâches",
                "url_prefix": "/circulation/taches/",
                "url_name": "tache_list",
                "roles": ["superadmin", "administrateur", "superviseur", "gestionnaire", "responsable"],
            },
            {
                "title": "Gestion des tâches",
                "url_prefix": "/circulation/taches-management/",
                "url_name": "tache_management",
                "roles": ["superadmin", "administrateur", "superviseur"],
            },
            {
                "title": "Créer une tâche",
                "url_prefix": "/circulation/taches/create/",
                "url_name": "tache_create",
                "roles": ["superadmin", "administrateur", "superviseur"],
            },
            {
                "title": "Audit",
                "url_name": "audit_log_list",
                "url_prefix": "/circulation/audit/",
                "roles": ["superadmin", "administrateur", "superviseur"],
            },
        ],
    },
    # Documents
    {
        "header": "Gestion des documents",
        "roles": ["superadmin", "administrateur", "superviseur", "gestionnaire", "responsable"],
    },
    {
        "title": "Ajouter",
        "icon": "ri-sticky-note-add-line",
        "url_prefix": "/upload/",
        "url_name": "upload_page",
        "roles": ["superadmin", "administrateur", "superviseur", "gestionnaire", "responsable"],
    },
    {
        "title": "Documents",
        "icon": "ri-file-list-3-fill",
        "url_prefix": "/documents/",
        "roles": ["superadmin", "administrateur", "superviseur", "gestionnaire", "responsable"],
        "children": [
            {
                "title": "Listes",
                "url_name": "document_list",
                "url_prefix": "/documents/",
                "roles": ["superadmin", "administrateur", "superviseur", "gestionnaire", "responsable"]
            },
            {
                "title": "Types",
                "url_name": "typedocument_list",
                "url_prefix": "/typedocument/typedocuments/",
                "roles": ["superadmin", "administrateur", "superviseur"]
            },
            {
                "title": "Sous Types",
                "url_name": "soustypedocument_list",
                "url_prefix": "/soustypedocument/soustypedocuments/",
                "roles": ["superadmin", "administrateur", "superviseur"]
            },
            {
                "title": "Thèmes",
                "url_name": "themes_list",
                "url_prefix": "/theme/themes/",
                "roles": ["superadmin", "administrateur", "superviseur"]
            },
        ],
    },

    {
        "header": "Utilisateurs & Rôles",
        "roles": ["superadmin", "administrateur", "superviseur"],
    },
    {
        "title": "Profil",
        "icon": "ri-profile-line",
        "url_name": "user_profile",
        "url_prefix": "/profile/",
        "roles": ["superadmin", "administrateur", "superviseur", "gestionnaire", "responsable"],
    },
    {
        "title": "Utilisateurs",
        "icon": "ri-group-line",
        "roles": ["superadmin", "administrateur", "superviseur"],
        "children": [
            {
                "title": "Listes",
                "url_name": "utilisateur_list",
                "url_prefix": "/utilisateur/",
                "roles": ["superadmin", "administrateur", "superviseur"]
            },
        ],
    },

    {
        "header": "Éléments Administratifs",
        "roles": ["superadmin", "administrateur", "superviseur"],
    },
    {
        "title": "Unité de traitement",
        "icon": "ri-building-line",
        "url_name": "cellule_list",
        "url_prefix": "/cellule/",
        "roles": ["superadmin", "administrateur"],
    },
    {
        "title": "Divisions",
        "icon": "ri-building-2-line",
        "url_name": "division_list",
        "url_prefix": "/division/",
        "roles": ["superadmin", "administrateur"],
    },
    {
        "title": "Directions générales",
        "icon": "ri-building-2-line",
        "url_prefix": "/directiongenerale/",
        "url_name": "directiongenerale_list",
        "roles": ["superadmin", "administrateur"],
    },
    {
        "title": "Ministères",
        "icon": "ri-government-line",
        "url_name": "ministere_list",
        "url_prefix": "/ministere/",
        "roles": ["superadmin", "administrateur"],
    },
    {
        "title": "Bailleurs",
        "icon": "ri-wallet-2-fill me-1",
        "url_name": "bailleurs_list",
        "url_prefix": "/bailleur/bailleurs/",
        "roles": ["superadmin", "administrateur", "superviseur"],
    },
    {
        "title": "Avenants",
        "icon": "ri-bill-fill me-1",
        "url_name": "avenants_list",
        "url_prefix": "/avenant/avenants/",
        "roles": ["superadmin", "administrateur", "superviseur"],
    },
]
