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
    # a typeDocument belongs to a Cellule
    cellule = models.ForeignKey(Cellule, on_delete=models.CASCADE, null=True, blank=True)
    # relation de règle de gestion
    parent_type = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='sous_types_fonctionnels'
    )
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"(Type de document) : {self.libelle}"

class SousTypeDocument(models.Model):
    libelle = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, name='description_soustypedocument')
    type_document = models.ForeignKey(TypeDocument, on_delete=models.CASCADE, related_name='sous_types')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"(Sous Type de document) : {self.libelle}"

class EtatDocument(models.TextChoices):
    EN_ATTENTE = 'en attente',
    EN_TRAITEMENT = 'en traitement',
    VALIDE = 'valide',
    ARCHIVE = 'archive',

class NiveauAccesDocument(models.Model): # to change later as enum textchoices
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

class Bailleurs(models.Model):
    abrevation = models.CharField(max_length=255, unique=True)
    libelle = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    # a bailleur belongs to a cellule :
    cellule = models.ForeignKey(Cellule, on_delete=models.CASCADE, null=True, blank=True)
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.libelle

class Avenants(models.Model):
    # a avenant believe to a bailleur
    bailleur = models.ForeignKey(Bailleurs, on_delete=models.CASCADE, null=True, related_name= "avenant_bailleur")
    nom = models.CharField(max_length=255, unique=True)
    prenom = models.CharField(max_length=255, unique=True)
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

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
    # relations
    bailleur = models.ForeignKey(Bailleurs, on_delete=models.CASCADE, related_name='document_bailleur', null=True, blank=True)
    avenant = models.ForeignKey(Avenants, on_delete=models.CASCADE, related_name='document_avenant', null=True, blank=True)
    # Relation hiérarchique
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enfants'
    )
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = f"({self.type_document.libelle}) : {self.titre}" if self.type_document else f"(Aucun type de document) : {self.titre}"
        return name

class VersionDocument(models.Model):
    # generic
    titre = models.CharField(max_length=255, unique=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    numero_version = models.PositiveIntegerField()
    fichier = models.FileField(upload_to='documents/')
    # utilisateur
    cree_par = models.ForeignKey('users.Utilisateur', on_delete=models.SET_NULL, null=True, related_name='version_documents_crees')
    modifier_par = models.ForeignKey('users.Utilisateur', on_delete=models.SET_NULL, null=True, related_name='version_documents_maj')
    responsable_version = models.ForeignKey(
        'users.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='version_documents_responsables',
        limit_choices_to={'role': 'responsable'}
    )
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre
