import json

from django import template

register = template.Library()

@register.filter
def get_field_value(obj, field_name):
    """Return dynamic attribute value of an object by name"""
    return getattr(obj, field_name, None)

@register.filter
def get_attr(obj, attr):
    """Permet d'accéder dynamiquement à un attribut d'un objet dans le template"""
    return getattr(obj, attr, None)

@register.filter
def col_size(fields_per_row):
    try:
        return int(12 / int(fields_per_row))
    except:
        return 12

@register.filter(name='pretty_json')
def pretty_json(value):
    """
    Filtre pour formater proprement un dictionnaire ou un JSONField
    en chaîne JSON indentée et lisible.
    """
    if value is None:
        return ""

    # Si la valeur est déjà un dictionnaire (comme un JSONField Django)
    if isinstance(value, dict) or isinstance(value, list):
        return json.dumps(value, indent=4, ensure_ascii=False)

    # Si c'est une chaîne de caractères brute contenant du JSON
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return json.dumps(parsed, indent=4, ensure_ascii=False)
        except ValueError:
            return value # Retourne la chaîne brute si ce n'est pas du JSON valide

    return str(value)
