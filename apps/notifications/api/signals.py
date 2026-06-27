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
    """
    Gère les notifications de changement de statut d'une tâche.
    S'adapte dynamiquement selon que l'action vient de l'assigné ou d'un manager.
    """
    if created:
        return

    # Récupération du statut d'origine (mémorisé dans le __init__ du modèle)
    ancien_statut = getattr(instance, '_Tache__original_statut', None)

    # Récupération de l'auteur de la modification (injecté depuis l'API)
    auteur_action = getattr(instance, '_modifier_par', None)

    # Si aucun changement de statut n'a eu lieu, on s'arrête
    if ancien_statut == instance.statut:
        return

    # Acteurs clés du flux
    assigne = instance.assignee_a
    assignateur = instance.assignee_par
    document = instance.document

    # Le créateur du document lié peut aussi être notifié en cas d'annulation/clôture
    createur_doc = document.cree_par if document else None

    destinataires = set()
    titre = ""
    message = ""

    # Formatage du nom du modificateur
    if auteur_action:
        nom_auteur = auteur_action.get_full_name() or auteur_action.username
    else:
        nom_auteur = "Un gestionnaire"

    # ─── MATRICE LOGIQUE DES STATUTS ───

    if instance.statut == StatutTache.EN_COURS:
        titre = "Tâche commencée 🚀"
        message = f"La tâche '{instance.titre}' sur le document '{document.titre}' a été passée 'En cours' par {nom_auteur}."

        if auteur_action == assigne:
            if assignateur: destinataires.add(assignateur)
        else:
            if assigne: destinataires.add(assigne)

    elif instance.statut == StatutTache.EN_REVISION:
        titre = "Tâche en révision 🔍"
        message = f"La tâche '{instance.titre}' a été soumise pour vérification par {nom_auteur}."

        if auteur_action == assigne:
            if assignateur: destinataires.add(assignateur)
        else:
            if assigne: destinataires.add(assigne)

    elif instance.statut == StatutTache.TERMINEE:
        titre = "Tâche complétée 🎉"
        message = f"La tâche '{instance.titre}' a été validée et clôturée par {nom_auteur}."

        if auteur_action == assigne:
            # Clôture autonome par l'exécutant
            if assignateur: destinataires.add(assignateur)
        else:
            # Clôture / Validation par un Admin, Superviseur ou Responsable
            if assigne: destinataires.add(assigne)
            if assignateur: destinataires.add(assignateur)

    elif instance.statut == StatutTache.ANNULEE:
        titre = "Tâche annulée 🛑"
        message = f"La tâche '{instance.titre}' a été annulée par {nom_auteur}."

        # Tout le monde est prévenu en cas d'annulation définitive
        if assigne: destinataires.add(assigne)
        if assignateur: destinataires.add(assignateur)

    elif instance.statut == StatutTache.A_FAIRE:
        # Cas critique : Une tâche en révision est rejetée et repasse à l'état initial
        if ancien_statut == StatutTache.EN_REVISION:
            titre = "Correction demandée ↩️"
            message = f"Le travail sur la tâche '{instance.titre}' a été refusé par {nom_auteur}. Des corrections sont nécessaires."
        else:
            titre = "Tâche réinitialisée 📋"
            message = f"La tâche '{instance.titre}' a été remise à l'état 'À faire' par {nom_auteur}."

        if assigne: destinataires.add(assigne)

    # ─── SÉCURITÉ ET NETTOYAGE CRUCIAL ───

    # 1. L'auteur du changement ne doit JAMAIS recevoir sa propre notification
    if auteur_action in destinataires:
        destinataires.remove(auteur_action)

    # 2. Envoi final uniquement aux utilisateurs actifs du système
    for destinataire in destinataires:
        if destinataire and destinataire.is_active:
            Notification.objects.create(
                destinataire=destinataire,
                titre=titre,
                message=message,
                categorie=Notification.Category.TACHE,
                content_object=instance,
                url_action=f"/taches/detail/{instance.id}/"
            )
