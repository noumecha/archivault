from django.conf import settings
from .navigation import SIDEBAR_MENU
from .roles import *

def my_setting(request):
    return {'MY_SETTING': settings}

def layout_context(request):
    return {
        "layout_path": "layout/layout_blank.html"
    }

def sidebar_context(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    role = user.role
    current_path = request.path

    filtered_menu = []

    for item in SIDEBAR_MENU:
        item = item.copy()
        item_roles = item.get("roles", [])

        item["is_active"] = False
        item["is_open"] = False

        # ---- CHILDREN MANAGEMENT ----
        if "children" in item:
            visible_children = []

            for child in item["children"]:
                if role not in child.get("roles", []):
                    continue

                child = child.copy()
                child["is_active"] = (
                    child.get("url_prefix")
                    and current_path.startswith(child["url_prefix"])
                )

                if child["is_active"]:
                    item["is_open"] = True
                    item["is_active"] = True

                visible_children.append(child)

            # Si aucun enfant visible → on cache tout le parent
            if not visible_children:
                continue

            item["children"] = visible_children

        # ---- PARENT WITHOUT CHILDREN ----
        else:
            if item_roles and role not in item_roles:
                continue

            if item.get("url_prefix") and current_path.startswith(item["url_prefix"]):
                item["is_active"] = True

        # ---- FINAL VISIBILITY RULE ----
        if item_roles and role not in item_roles and "children" not in item:
            continue

        filtered_menu.append(item)

    # ---- SIDEBAR TITLE ----
    sidebar_title = "Archivault"
    if (is_responsable(user) or is_superviseur(user) or is_gestionnaire(user)) and user.cellule:
        sidebar_title = user.cellule.nom

    return {
        "sidebar_menu": filtered_menu,
        "sidebar_title": sidebar_title,
    }


# Add the 'ENVIRONMENT' setting to the template context
def environment(request):
    return {'ENVIRONMENT': settings.ENVIRONMENT}
