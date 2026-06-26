# apps/circulation/tasks.py
from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task
def executer_verification_echeances():
    """
    Tâche planifiée pour exécuter la commande de vérification des retards.
    """
    logger.info("Démarrage de la vérification planifiée des échéances de tâches...")
    try:
        call_command('verifier_echeances_taches')
        logger.info("Vérification des échéances terminée avec succès.")
        return "Succès"
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des échéances : {str(e)}")
        return f"Échec : {str(e)}"
