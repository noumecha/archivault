from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from apps.administration.models import Division
# -*- coding: utf-8 -*-

# Rôles utilisateur
class RoleUtilisateur(models.Model):
    nom = models.CharField(max_length=100)  # Ex: 'admin', 'superviseur', 'agent'
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

# Profil utilisateur
class ProfilUtilisateur(models.Model):
    nom = models.CharField(max_length=100)  # Ex: 'Gestionnaire', 'Agent Saisie'
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

# Utilisateur personnalisé
class Utilisateur(AbstractUser):
    role = models.ForeignKey(RoleUtilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name="users_roles")
    profil = models.ForeignKey(ProfilUtilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        related_name="utilisateur_groups",  # <-- unique name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="utilisateur_permissions",  # <-- unique name
        blank=True
    )
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_full_name()