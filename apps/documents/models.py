from django.db import models
from apps.administration.models import Cellule
from apps.users.models import Utilisateur

# Create your models here.
class Theme(models.Model):
    libelle = models.CharField(max_length=255)
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

class TypeDocument(models.Model):
    libelle = models.CharField(max_length=255)
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

class SousTypeDocument(models.Model):
    libelle = models.CharField(max_length=255)
    type_document = models.ForeignKey(TypeDocument, on_delete=models.CASCADE, related_name='sous_types')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.libelle} ({self.type_document})"

class EtatDocument(models.TextChoices):
    EN_ATTENTE = 'attente', 'En attente'
    EN_TRAITEMENT = 'traitement', 'En traitement'
    VALIDE = 'valide', 'Validé'
    ARCHIVE = 'archive', 'Archivé'

class NiveauAccesDocument(models.Model):
    niveau = models.CharField(max_length=100)  # Ex: 'confidentiel', 'restreint'
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.niveau

class ProfilDoc(models.TextChoices):
    CONSULTATIF = 'consultatif', 'Consultatif'
    MODIFIABLE = 'modifiable', 'Modifiable'
    IMPRIMABLE = 'imprimable', 'Imprimable'

class RegleClassement(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class Document(models.Model):
    titre = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='documents/')
    type_document = models.ForeignKey(TypeDocument, on_delete=models.SET_NULL, null=True)
    sous_type = models.ForeignKey(SousTypeDocument, on_delete=models.SET_NULL, null=True, blank=True)
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True)
    cellule = models.ForeignKey(Cellule, on_delete=models.SET_NULL, null=True)
    etat = models.CharField(max_length=20, choices=EtatDocument.choices, default=EtatDocument.EN_ATTENTE)
    niveau_acces = models.ForeignKey(NiveauAccesDocument, on_delete=models.SET_NULL, null=True)
    profil_document = models.CharField(max_length=20, choices=ProfilDoc.choices, default=ProfilDoc.CONSULTATIF)
    regles_classement = models.ManyToManyField(RegleClassement, blank=True)
    metadonnees = models.JSONField(blank=True, null=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='documents_crees')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre