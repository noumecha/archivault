# apps/administration/models.py
from django.db import models

# statut
class Statut(models.TextChoices):
    ACTIVE = 'activé', 'Activé'
    DESACTIVE = 'desactivé', 'Desactivé'

# Ministère
class Ministere(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    abrevation = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, name='description_ministere')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"(Ministère) {self.nom}"

# direction generale
class DirectionGenerale(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, name='description_direction_generale')
    ministere = models.ForeignKey(Ministere, on_delete=models.CASCADE, related_name='directions_generales', null=True, blank=True)
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"(Direction Générale) {self.nom}"


# Division
class Division(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    ministere = models.ForeignKey(Ministere, on_delete=models.CASCADE, related_name='divisions')
    direction_generale = models.ForeignKey(DirectionGenerale, on_delete=models.CASCADE, related_name='divisions', blank=True, null=True)
    statut = models.BooleanField(default=False, blank=True, null=True)
    description = models.TextField(blank=True, name='description_division')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"(Division) {self.nom}"

# Cellule
class Cellule(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, name='description_cellule')
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='cellules')
    # avoir ou non des bailleurs
    accepte_bailleurs = models.BooleanField(
        default=False,
        help_text=(
            "Designe la possibilité pour une cellule de gérer des bailleurs."
        ),
    )
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nom', 'division'], name='unique_nom_division_cellule')
        ]

    def __str__(self):
        return f"(Unité de traitement) : {self.nom}"
