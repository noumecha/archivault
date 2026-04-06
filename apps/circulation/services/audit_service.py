from apps.circulation.models import AuditLog, ActionAudit


class AuditService:

    @staticmethod
    def log(request, action: str, objet, details: dict = None):
        """
        Enregistre une action dans le journal d'audit.

        Usage:
            AuditService.log(request, ActionAudit.CREATION, document)
            AuditService.log(request, ActionAudit.MODIFICATION, tache, details={"statut": "en_cours"})
        """
        ip = AuditService._get_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        AuditLog.objects.create(
            utilisateur  = request.user if request.user.is_authenticated else None,
            action       = action,
            objet_type   = objet.__class__.__name__,
            objet_id     = objet.pk,
            objet_label  = str(objet),
            details      = details or {},
            ip_address   = ip,
            user_agent   = user_agent,
        )

    @staticmethod
    def _get_ip(request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',').strip()
        return request.META.get('REMOTE_ADDR')
