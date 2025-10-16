from django import template

register = template.Library()

@register.filter
def endswith(value, arg):
    """Retourne True si la chaîne se termine par arg"""
    try:
        return str(value).lower().endswith(str(arg).lower())
    except Exception:
        return False
