from django.db import models
from apps.administration.models import Cellule
from apps.users.models import Utilisateur, RoleUtilisateur

# Create your models here.
class Theme(models.Model):
    libelle = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, name='description_theme')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

class TypeDocument(models.Model):
    libelle = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, name='description_typedocument')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

class SousTypeDocument(models.Model):
    libelle = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, name='description_soustypedocument')
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
    niveau = models.CharField(max_length=100, unique=True)  # Ex: 'confidentiel', 'restreint'
    description = models.TextField(blank=True, name='description_niveauaccess')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.niveau

class ProfilDoc(models.TextChoices):
    CONSULTATIF = 'consultatif', 'Consultatif'
    MODIFIABLE = 'modifiable', 'Modifiable'
    IMPRIMABLE = 'imprimable', 'Imprimable'

class Document(models.Model):
    titre = models.CharField(max_length=255, unique=True)
    fichier = models.FileField(upload_to='documents/')
    type_document = models.ForeignKey(TypeDocument, on_delete=models.SET_NULL, null=True)
    sous_type = models.ForeignKey(SousTypeDocument, on_delete=models.SET_NULL, null=True, blank=True)
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True)
    cellule = models.ForeignKey(Cellule, on_delete=models.SET_NULL, null=True, blank=True)
    etat = models.CharField(max_length=20, choices=EtatDocument.choices, default=EtatDocument.EN_ATTENTE)
    niveau_acces = models.ForeignKey(NiveauAccesDocument, on_delete=models.SET_NULL, null=True)
    profil_document = models.CharField(max_length=20, choices=ProfilDoc.choices, default=ProfilDoc.CONSULTATIF)
    metadonnees = models.JSONField(blank=True, null=True)
    cree_par = models.ForeignKey('users.Utilisateur', on_delete=models.SET_NULL, null=True, related_name='documents_crees')
    modifier_par = models.ForeignKey('users.Utilisateur', on_delete=models.SET_NULL, null=True, related_name='documents_maj')
    responsable_document = models.ForeignKey(
        'users.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents_responsables',
        limit_choices_to={'role': 'responsable'}
    )
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre
