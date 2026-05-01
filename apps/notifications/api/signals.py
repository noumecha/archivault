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
            url_action=f"/tasks/details/{instance.id}/"
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
                url_action=f"/circulation/details/{instance.id}/"
            )
