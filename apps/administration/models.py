from django.db import models

# Ministère
class Ministere(models.Model):
    nom = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

# Division
class Division(models.Model):
    nom = models.CharField(max_length=255)
    ministere = models.ForeignKey(Ministere, on_delete=models.CASCADE, related_name='divisions')

    def __str__(self):
        return f"{self.nom} ({self.ministere.nom})"

# Cellule
class Cellule(models.Model):
    nom = models.CharField(max_length=255)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='cellules')

    def __str__(self):
        return f"{self.nom} - {self.division.nom}"