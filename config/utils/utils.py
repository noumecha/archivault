from django.db import models

def generates_filters(filters):
    filters_context = []
    for f in filters:
        # --- GESTION DES FILTRES ---
        # chaque élément peut être :
        # - un modèle Django (ex: Cellule)
        # - une TextChoices (ex: RoleUtilisateur)
        # - un tuple (nom_du_champ, source)
        # - un tuple (nom_du_champ, source, label)
        # - un iterable [(value, label), ...]
        label = None
        if isinstance(f, (list, tuple)):
            if len(f) == 3:
                field_name, source, label = f
            elif len(f) == 2:
                field_name, source = f
            else:
                continue  # Ignore invalid tuples
        else:
            source = f
            field_name = getattr(source, "__name__", "filter").lower()
        if not label:
            label = field_name.replace('_', ' ').title()
        # 🔹 Cas 1 : modèle Django
        if hasattr(source, "objects"):
            try:
                items = source.objects.all()
                # Si le modèle a une date de création, on peut trier
                if hasattr(source, "Date_creation"):
                    items = items.order_by("-Date_creation")
                filters_context.append({
                    "name": field_name,
                    "label": label,
                    "type": "model",
                    "items": items
                })
                continue
            except Exception:
                pass
        # 🔹 Cas 2 : TextChoices
        try:
            if issubclass(source, models.TextChoices):
                filters_context.append({
                    "name": field_name,
                    "label": label,
                    "type": "choices",
                    "items": [{"value": c.value, "label": c.label} for c in source]
                })
                continue
        except TypeError:
            pass
        # 🔹 Cas 3 : Iterable de tuples (value, label)
        try:
            items = list(source)
            if items and isinstance(items[0], (list, tuple)) and len(items[0]) >= 2:
                filters_context.append({
                    "name": field_name,
                    "label": label,
                    "type": "iterable",
                    "items": [{"value": v, "label": l} for v, l in items]
                })
                continue
        except Exception:
            pass
    return filters_context
