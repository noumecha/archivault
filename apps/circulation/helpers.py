# apps/circulation/helpers.py

def get_client_ip(request):
    """
    Extrait l'adresse IP du client en prenant en compte
    les proxys inversés (Nginx, Gunicorn).
    """
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_agent(request):
    """Extrait le navigateur/OS de l'utilisateur."""
    if not request:
        return ""
    return request.META.get('HTTP_USER_AGENT', '')[:500]  # Sécurité : max 500 caractères
