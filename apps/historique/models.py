from django.db import models
from users.models import Utilisateur
from documents.models import Document
# -*- coding: utf-8 -*-

# Historique circulation
class HistoriqueCirculationDocument(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    date_action = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.action} ({self.date_action})"