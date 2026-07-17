# apps/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import os
import uuid

class RoleUtilisateur(models.TextChoices):
    SUPERADMIN = 'superadmin', 'Super Administrateur'
    ADMIN = 'administrateur', 'Administrateur'
    SUPERVISEUR = 'superviseur', 'Superviseur' # responsable ou directeur de la cellule
    GESTIONNAIRE = 'gestionnaire', 'Gestionnaire' # gestionnaire de documents
    RESPONSABLE = 'responsable', 'Responsable' # utilisateur avec des droits spécifiques

# Utilisateur personnalisé
def user_avatar_path(instance, filename):
    # On récupère l'extension originale (.jpg, .png, etc.)
    ext = filename.split('.')[-1]
    # On crée un nom unique (ex: 550e8400-e29b-41d4-a716-446655440000.jpg)
    filename = f"{uuid.uuid4()}.{ext}"
    # Retourne le chemin : avatars/user_1/uuid.jpg
    return os.path.join('avatars', f'user_{instance.id}', filename)

class Utilisateur(AbstractUser):
    avatar = models.ImageField(upload_to=user_avatar_path, max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, choices=RoleUtilisateur.choices, default=RoleUtilisateur.RESPONSABLE)
    cellule = models.ForeignKey('administration.Cellule', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    cellules_supervisees = models.ManyToManyField(
        'administration.Cellule',
        blank=True,
        related_name='superviseurs',
        help_text="Cellules supervisées par cet utilisateur (si rôle Superviseur)"
    )
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

    @property
    def mes_cellules_ids(self):
        """Retourne les IDs de toutes les cellules sous la responsabilité ou rattachement de l'utilisateur."""
        cell_ids = list(self.cellules_supervisees.values_list('id', flat=True))
        if self.cellule_id:
            cell_ids.append(self.cellule_id)
        return list(set(cell_ids))

    def __str__(self):
        return self.username
