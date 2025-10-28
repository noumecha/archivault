from django.db import models

# Ministère
class Ministere(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, name='description_ministere')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

# Division
class Division(models.Model):
    nom = models.CharField(max_length=255)
    ministere = models.ForeignKey(Ministere, on_delete=models.CASCADE, related_name='divisions')
    description = models.TextField(blank=True, name='description_division')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} ({self.ministere.nom})"

# Cellule
class Cellule(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, name='description_cellule')
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='cellules')
    # timestamp
    Date_creation = models.DateTimeField(auto_now_add=True)
    Date_miseajour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} - {self.division.nom}"
