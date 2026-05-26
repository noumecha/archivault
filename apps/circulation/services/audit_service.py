# apps/circulation/services/audit_service.py
import logging
from django.contrib.contenttypes.models import ContentType
from ..models import AuditLog
from ..helpers import get_client_ip, get_user_agent

logger = logging.getLogger(__name__)

class AuditService:

    @staticmethod
    def log(request, action, obj=None, label="", details=None, statut='success'):
        """
        Enregistre de manière sécurisée une action dans le journal d'audit.
        """
        try:
            # 1. Identification de l'acteur
            user = request.user if request and request.user and request.user.is_authenticated else None

            # 2. Extraction du contexte technique via les helpers
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)

            # 3. Résolution de l'objet générique (Content Type)
            content_type = None
            object_id = None

            if obj:
                content_type = ContentType.objects.get_for_model(obj)
                object_id = obj.id
                if not label:
                    label = str(obj)[:255]

            # 4. Insertion en Base de données
            AuditLog.objects.create(
                utilisateur=user,
                action=action,
                statut=statut,
                content_type=content_type,
                object_id=object_id,
                objet_label=label,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )

        except Exception as e:
            # Sécurité maximale : on écrit l'erreur dans les logs serveurs,
            # mais on ne lève pas d'exception pour ne pas figer l'application métier.
            logger.error(f"Échec critique de l'enregistrement de l'Audit Log: {str(e)}", exc_info=True)
