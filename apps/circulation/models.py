from django.db import models
from users.models import Utilisateur
from documents.models import Document
# -*- coding: utf-8 -*-

# Circulation documents
class CirculationDocument(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    utilisateurs = models.ManyToManyField(Utilisateur, related_name='circulations')
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Circulation de {self.document.titre}"