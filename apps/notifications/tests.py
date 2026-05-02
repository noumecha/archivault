from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    class Category(models.TextChoices):
        TACHE = 'tache', 'Tâche'
        CIRCULATION = 'circulation', 'Circulation'
        SYSTEME = 'systeme', 'Système'

    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=255)
    message = models.TextField()
    categorie = models.CharField(max_length=20, choices=Category.choices, default=Category.SYSTEME)

    # Pour pointer vers n'importe quel objet (Tache, Document, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    url_action = models.CharField(max_length=255, blank=True, null=True) # Lien vers l'action
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.destinataire.username} - {self.titre}"
