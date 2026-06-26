# apps/nofications/api/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.circulation.models import *
from ..models import Notification

# -- CIRCULATION --
""" Lors de la creation d'une étape de circulation pour un utilisateur, une notification est envoyée """
@receiver(post_save, sender=EtapeCirculation)
def notify_etape_destinataire(sender, instance, created, **kwargs):
    """
    On notifie le destinataire quand une étape est créée
    OU quand une étape existante devient 'active'.
    """
    if created and instance.ordre == 1 and instance.destinataire:
        Notification.objects.create(
            destinataire=instance.destinataire,
            titre="Nouvelle circulation",
            message=f"Une circulation a été initiée pour le document : {instance.circulation.document.titre}",
            categorie=Notification.Category.CIRCULATION,
            content_object=instance.circulation,
            url_action=f"/circulations/detail/{instance.circulation.id}/"
        )

""" Notification du prermier destinataire lors de la créationd de la circulation """
@receiver(post_save, sender=CirculationDocument)
def notify_circulation_init(sender, instance, created, **kwargs):
    if created:
        # Notifier par exemple le premier destinataire de l'étape 1
        premiere_etape = instance.etapes.filter(ordre=1).first()
        if premiere_etape and premiere_etape.destinataire:
            Notification.objects.create(
                destinataire=premiere_etape.destinataire,
                titre="Nouvelle circulation",
                message=f"Une circulation a été initiée pour : {instance.document.titre}",
                categorie=Notification.Category.CIRCULATION,
                content_object=instance,
                url_action=f"/circulations/detail/{instance.id}/"
            )

""" lorsque la premiè_ve étape est validé dans la circulation, on notifie l'utilisateur suivant """
@receiver(post_save, sender=EtapeCirculation)
def notify_next_step(sender, instance, created, **kwargs):
    # Si l'étape actuelle vient d'être validée
    if not created and instance.statut == 'valide':
        # On cherche l'étape suivante (ordre + 1) dans la même circulation
        next_step = EtapeCirculation.objects.filter(
            circulation=instance.circulation,
            ordre=instance.ordre + 1
        ).first()

        if next_step and next_step.destinataire:
            Notification.objects.create(
                destinataire=next_step.destinataire,
                titre="Document à traiter",
                message=f"C'est à votre tour de traiter : {instance.circulation.document.titre}",
                categorie=Notification.Category.CIRCULATION,
                content_object=instance.circulation,
                url_action=f"/circulations/detail/{instance.circulation.id}/"
            )

""" On notifie le créateur de la circulation lorsque la circulation est terminée """
@receiver(post_save, sender=CirculationDocument)
def notify_circulation_end(sender, instance, created, **kwargs):
    if not created: # On surveille la modification
        if instance.statut == 'termine':
            Notification.objects.create(
                destinataire=instance.initie_par,
                titre="Circulation terminée",
                message=f"Le circuit pour {instance.document.titre} est complet.",
                categorie=Notification.Category.SYSTEME,
                priorite=Notification.Priority.HIGH
            )

@receiver(post_save, sender=EtapeCirculation)
def notify_etape_traitee(sender, instance, created, **kwargs):
    """
    Lorsqu'une étape d'une circulation est traitée, on notifie l'initiateur de la circulation.
    """
    if not created and instance.statut in [StatutCirculation.VALIDE, StatutCirculation.REJETE, StatutCirculation.RETOURNE]:
        circulation = instance.circulation
        # On s'assure de ne pas notifier l'initiateur si c'est lui-même qui a traité l'étape
        if circulation.initie_par and circulation.initie_par != instance.traite_par:
            statut_label = "validée" if instance.statut == StatutCirculation.VALIDE else "rejetée/retournée"
            Notification.objects.create(
                destinataire=circulation.initie_par,
                titre=f"Étape de circulation {statut_label}",
                message=f"{instance.traite_par.username} a marqué l'étape '{instance.ordre} : {instance.titre_etape}' comme [{instance.statut}] pour le document : {circulation.document.titre}.",
                categorie=Notification.Category.CIRCULATION,
                content_object=circulation,
                url_action=f"/circulations/detail/{circulation.id}/"
            )

@receiver(post_save, sender=CirculationDocument)
def notify_circulation_global_end(sender, instance, created, **kwargs):
    """
    Lorsqu'une circulation globale se termine (Validée/Close ou Rejetée définitivement),
    on notifie l'initiateur de la circulation.
    """
    if not created:
        if instance.statut in [StatutCirculation.CLOS, StatutCirculation.REJETE]:
            titre_notif = "Circulation terminée avec succès" if instance.statut == StatutCirculation.CLOS else "Circulation rejetée"
            message_notif = (
                f"Le circuit pour le document '{instance.document.titre}' est désormais complet et clôturé."
                if instance.statut == StatutCirculation.CLOS else
                f"Le circuit pour le document '{instance.document.titre}' a été interrompu suite à un rejet."
            )

            if instance.initie_par:
                Notification.objects.create(
                    destinataire=instance.initie_par,
                    titre=titre_notif,
                    message=message_notif,
                    categorie=Notification.Category.CIRCULATION,
                    content_object=instance,
                    priorite=Notification.Priority.HIGH,
                    url_action=f"/circulations/detail/{instance.id}/"
                )

# -- TACHE --
@receiver(post_save, sender=Tache)
def notify_tache_assignee(sender, instance, created, **kwargs):
    """Notification à la création de la tâche."""
    if created and instance.assignee_a:
        Notification.objects.create(
            destinataire=instance.assignee_a,
            titre="Nouvelle tâche assignée",
            message=f"Vous avez été assigné à la tâche : {instance.titre}",
            categorie=Notification.Category.TACHE,
            content_object=instance,
            url_action=f"/taches/detail/{instance.id}/"
        )

@receiver(post_save, sender=Tache)
def notify_tache_status_changes(sender, instance, created, **kwargs):
    """Gère les notifications liées aux changements de statut d'une tâche."""
    if created:
        return

    # On récupère l'état d'origine mémorisé par l'astuce du __init__
    ancien_statut = getattr(instance, '_Tache__original_statut', None)

    # Si le statut n'a pas bougé, on ne fait rien
    if ancien_statut == instance.statut:
        return

    # Préparation des paramètres de notification communs
    destinataire = None
    titre = ""
    message = ""

    nom_assigne = instance.assignee_a.get_full_name() or instance.assignee_a.username if instance.assignee_a else "Un utilisateur"

    if instance.statut == StatutTache.EN_COURS:
        if instance.assignee_par and instance.assignee_par != instance.assignee_a:
            destinataire = instance.assignee_par
            titre = "Tâche commencée"
            message = f"La tâche '{instance.titre}' a été commencée par {nom_assigne}."

    elif instance.statut == StatutTache.EN_REVISION:
        if instance.assignee_par and instance.assignee_par != instance.assignee_a:
            destinataire = instance.assignee_par
            titre = "Tâche en révision"
            message = f"La tâche '{instance.titre}' est désormais en révision par {nom_assigne}."

    elif instance.statut == StatutTache.TERMINEE:
        if instance.assignee_par and instance.assignee_par != instance.assignee_a:
            destinataire = instance.assignee_par
            titre = "Tâche complétée 🎉"
            message = f"La tâche '{instance.titre}' a été traitée avec succès par {nom_assigne}."

    elif instance.statut == StatutTache.ANNULEE:
        # En cas d'annulation par un manager, c'est l'assigné qui doit être prévenu
        if instance.assignee_a and instance.assignee_par == instance.cree_par:
            destinataire = instance.assignee_a
            titre = "Tâche annulée"
            message = f"La tâche '{instance.titre}' à laquelle vous étiez assigné a été annulée."

    # Envoi de la notification si un scénario est validé
    if destinataire:
        Notification.objects.create(
            destinataire=destinataire,
            titre=titre,
            message=message,
            categorie=Notification.Category.TACHE,
            content_object=instance,
            url_action=f"/taches/detail/{instance.id}/"
        )
