from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.circulation.models import *
from ..models import Notification

@receiver(post_save, sender=Tache)
def notify_tache_assignee(sender, instance, created, **kwargs):
    if created and instance.assignee_a:
        Notification.objects.create(
            destinataire=instance.assignee_a,
            titre="Nouvelle tâche assignée",
            message=f"Vous avez été assigné à la tâche : {instance.titre}",
            categorie=Notification.Category.TACHE,
            content_object=instance,
            url_action=f"/taches/detail/{instance.id}/"
        )

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

@receiver(post_save, sender=CirculationDocument)
def notify_circulation_end(sender, instance, created, **kwargs):
    if not created: # On surveille la modification
        if instance.statut == 'termine':
            Notification.objects.create(
                destinataire=instance.createur, # Assure-toi d'avoir un champ createur
                titre="Circulation terminée",
                message=f"Le circuit pour {instance.document.titre} est complet.",
                categorie=Notification.Category.SYSTEME,
                priorite=Notification.Priority.HIGH
            )
