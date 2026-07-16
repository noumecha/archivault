# apps/notifications/api/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.circulation.models import *
from ..models import Notification

# ─────────────────────────────────────────────────────────────────────────────
# 1. NOTIFICATIONS LIÉES AUX ÉTAPES (EtapeCirculation)
# ─────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender=EtapeCirculation)
def notify_etape_events(sender, instance, created, **kwargs):
    """
    Gère toutes les notifications liées au changement d'état d'une étape :
    - Notification du destinataire de la NOUVELLE étape active (Validation, Rejet/Retour arrière)
    - Notification de l'INITIATEUR quand une étape est traitée
    """
    # CAS A : L'étape vient d'être activée (Soit création Étape 1, soit passage au suivant/précédent)
    # On vérifie 'est_actuelle' pour être sûr que c'est le destinataire courant
    if instance.est_actuelle and instance.destinataire:
        # On évite de double-notifier si l'étape est marquée comme traitée au même moment
        if instance.statut in [StatutCirculation.EN_COURS, StatutCirculation.RETOURNE]:

            # Ajustement du message selon qu'il s'agisse d'un retour ou d'un flux normal
            if instance.statut == StatutCirculation.RETOURNE:
                titre_notif = "Document retourné à corriger"
                message_notif = f"Le document '{instance.circulation.document.titre}' vous a été retourné pour révision/correction."
            else:
                titre_notif = "Document à traiter"
                message_notif = f"C'est à votre tour de traiter le document : {instance.circulation.document.titre}"

            Notification.objects.create(
                destinataire=instance.destinataire,
                titre=titre_notif,
                message=message_notif,
                categorie=Notification.Category.CIRCULATION,
                content_object=instance.circulation,
                url_action=f"/circulations/detail/{instance.circulation.id}/"
            )

    # CAS B : L'étape a été TRAITÉE (Validation, Rejet ou Retour)
    # On informe l'initiateur du traitement effectué
    if not created and instance.statut in [StatutCirculation.VALIDE, StatutCirculation.REJETE, StatutCirculation.RETOURNE]:
        circulation = instance.circulation

        # On notifie l'initiateur (seulement si ce n'est pas lui qui vient de traiter l'étape)
        if circulation.initie_par and circulation.initie_par != instance.traite_par:

            statut_map = {
                StatutCirculation.VALIDE: "validée",
                StatutCirculation.REJETE: "rejetée",
                StatutCirculation.RETOURNE: "retournée"
            }
            libelle_statut = statut_map.get(instance.statut, str(instance.statut))
            acteur_name = instance.traite_par.get_full_name() or instance.traite_par.username if instance.traite_par else "Un utilisateur"

            Notification.objects.create(
                destinataire=circulation.initie_par,
                titre=f"Étape {libelle_statut}",
                message=f"{acteur_name} a marqué l'étape {instance.ordre} ('{instance.titre_etape}') comme [{libelle_statut}] pour : {circulation.document.titre}.",
                categorie=Notification.Category.CIRCULATION,
                content_object=circulation,
                url_action=f"/circulations/detail/{circulation.id}/"
            )


# ─────────────────────────────────────────────────────────────────────────────
# 2. NOTIFICATIONS LIÉES À LA CIRCULATION GLOBALE (CirculationDocument)
# ─────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender=CirculationDocument)
def notify_circulation_events(sender, instance, created, **kwargs):
    """
    Gère l'initialisation et la clôture globale d'un circuit.
    """
    # CAS A : Création initiale de la circulation
    if created:
        # L'étape 1 est gérée automatiquement par 'notify_etape_events' lorsque
        # les objets EtapeCirculation sont créés dans la transaction atomic.
        pass

    # CAS B : Fin/Clôture ou Rejet définitif de la circulation globale
    else:
        if instance.statut in [StatutCirculation.CLOS, StatutCirculation.VALIDE, StatutCirculation.REJETE]:

            is_succes = instance.statut in [StatutCirculation.CLOS, StatutCirculation.VALIDE]
            titre_notif = "Circulation terminée avec succès" if is_succes else "Circulation interrompue (Rejet)"

            message_notif = (
                f"Le circuit pour le document '{instance.document.titre}' est désormais complet et clôturé."
                if is_succes else
                f"Le circuit pour le document '{instance.document.titre}' a été définitivement interrompu suite à un rejet."
            )

            if instance.initie_par:
                # Vérification anti-doublon basique (évite de générer 2 fois la notif de fin si mis à jour rapidement)
                deja_notifie = Notification.objects.filter(
                    destinataire=instance.initie_par,
                    titre=titre_notif,
                    content_type__model="circulationdocument",
                    object_id=instance.id
                ).exists()

                if not deja_notifie:
                    Notification.objects.create(
                        destinataire=instance.initie_par,
                        titre=titre_notif,
                        message=message_notif,
                        categorie=Notification.Category.CIRCULATION,
                        priorite=Notification.Priority.HIGH,
                        content_object=instance,
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
