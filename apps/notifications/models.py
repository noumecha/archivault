from django.db import models
from documents.models import Document
from users.models import Utilisateur

# notifications/models.py
class Notification(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    message = models.TextField()
    vue = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(auto_now_add=True)
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notif to {self.utilisateur} | {self.document}"
