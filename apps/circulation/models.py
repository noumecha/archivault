from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.documents.models import Document
from apps.users.models import Utilisateur, RoleUtilisateur


# ─────────────────────────────────────────────
# PERMISSIONS CUSTOM
# ─────────────────────────────────────────────

class PermissionTache(models.TextChoices):
    CREER_TACHE = 'creer_tache', 'Créer des tâches'
    ASSIGNER_TACHE = 'assigner_tache', 'Assigner des tâches'
    VALIDER_TACHE = 'valider_tache', 'Valider des tâches'
    VOIR_TOUTES_TACHES = 'voir_toutes_taches', 'Voir toutes les tâches'


# ─────────────────────────────────────────────
# CIRCULATION
# ─────────────────────────────────────────────

class StatutCirculation(models.TextChoices):
    EN_ATTENTE   = 'en_attente',   'En attente'
    EN_COURS     = 'en_cours',     'En cours'
    VALIDE       = 'valide',       'Validé'
    REJETE       = 'rejete',       'Rejeté'
    RETOURNE     = 'retourne',     'Retourné'
    CLOS         = 'clos',         'Clos'


class CirculationDocument(models.Model):
    """
    Représente un circuit de circulation d'un document.
    """
    document      = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='circulations')
    titre         = models.CharField(max_length=255)
    description   = models.TextField(blank=True)
    initie_par    = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='circulations_initiees')
    statut        = models.CharField(max_length=20, choices=StatutCirculation.choices, default=StatutCirculation.EN_ATTENTE)
    date_debut    = models.DateTimeField(default=timezone.now)
    date_fin      = models.DateTimeField(null=True, blank=True)
    # timestamp
    Date_creation    = models.DateTimeField(auto_now_add=True)
    Date_miseajour   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-Date_creation']

    def __str__(self):
        return f"Circulation [{self.document.titre}] — {self.statut}"


class EtapeCirculation(models.Model):
    """
    Chaque étape du circuit : qui doit traiter, dans quel ordre, quel résultat.
    """
    circulation   = models.ForeignKey(CirculationDocument, on_delete=models.CASCADE, related_name='etapes')
    ordre         = models.PositiveIntegerField()
    destinataire  = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='etapes_recues')
    statut        = models.CharField(max_length=20, choices=StatutCirculation.choices, default=StatutCirculation.EN_ATTENTE)
    commentaire   = models.TextField(blank=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par    = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='etapes_traitees')
    est_actuelle = models.BooleanField(default=False) # Très utile pour les requêtes SQL rapides
    date_reception = models.DateTimeField(null=True, blank=True) # Traçabilité : "Vu à telle heure"
    # timestamp
    Date_creation    = models.DateTimeField(auto_now_add=True)
    Date_miseajour   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre']
        unique_together = ('circulation', 'ordre')

    def __str__(self):
        return f"Étape {self.ordre} — {self.destinataire} [{self.statut}]"


# ─────────────────────────────────────────────
# TÂCHES
# ─────────────────────────────────────────────

class PrioriteTache(models.TextChoices):
    BASSE   = 'basse',   'Basse'
    NORMALE = 'normale', 'Normale'
    HAUTE   = 'haute',   'Haute'
    URGENTE = 'urgente', 'Urgente'


class StatutTache(models.TextChoices):
    A_FAIRE     = 'a_faire',     'À faire'
    EN_COURS    = 'en_cours',    'En cours'
    EN_REVISION = 'en_revision', 'En révision'
    TERMINEE    = 'terminee',    'Terminée'
    ANNULEE     = 'annulee',     'Annulée'


class Tache(models.Model):
    """
    Tâche confiée à un utilisateur sur un document.
    """
    document      = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='taches')
    titre         = models.CharField(max_length=255)
    description   = models.TextField(blank=True)
    assignee_par  = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='taches_assignees')
    assignee_a    = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='mes_taches')
    statut        = models.CharField(max_length=20, choices=StatutTache.choices, default=StatutTache.A_FAIRE)
    priorite      = models.CharField(max_length=20, choices=PrioriteTache.choices, default=PrioriteTache.NORMALE)
    date_echeance = models.DateField(null=True, blank=True)
    date_cloture  = models.DateTimeField(null=True, blank=True)
    # timestamp
    Date_creation    = models.DateTimeField(auto_now_add=True)
    Date_miseajour   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priorite', '-Date_creation']

    def __str__(self):
        return f"[{self.priorite.upper()}] {self.titre} → {self.assignee_a}"

    def is_overdue(self):
        """Vérifier si la tâche est en retard."""
        if self.date_echeance and self.statut != StatutTache.TERMINEE:
            return timezone.now().date() > self.date_echeance
        return False


class CommentaireTache(models.Model):
    """
    Commentaires/suivi sur une tâche (timeline).
    """
    tache         = models.ForeignKey(Tache, on_delete=models.CASCADE, related_name='commentaires')
    auteur        = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    contenu       = models.TextField()
    ancien_statut = models.CharField(max_length=20, blank=True)
    nouveau_statut = models.CharField(max_length=20, blank=True)
    # timestamp
    Date_creation    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['Date_creation']

    def __str__(self):
        return f"Commentaire de {self.auteur} sur [{self.tache.titre}]"


# ─────────────────────────────────────────────
# AUDIT LOG
# ─────────────────────────────────────────────

class ActionAudit(models.TextChoices):
    CREATION      = 'creation',      'Création'
    MODIFICATION  = 'modification',  'Modification'
    SUPPRESSION   = 'suppression',   'Suppression'
    TELECHARGEMENT = 'telechargement', 'Téléchargement'
    IMPRESSION    = 'impression',    'Impression'
    CIRCULATION   = 'circulation',   'Circulation'
    TACHE         = 'tache',         'Tâche'
    CONNEXION     = 'connexion',     'Connexion'
    CONSULTATION  = 'consultation',  'Consultation'


class AuditLog(models.Model):
    """
    Journal d'audit complet — toutes les actions du système.
    """
    utilisateur   = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action        = models.CharField(max_length=30, choices=ActionAudit.choices)
    objet_type    = models.CharField(max_length=100)
    objet_id      = models.PositiveIntegerField(null=True, blank=True)
    objet_label   = models.CharField(max_length=255, blank=True)
    details       = models.JSONField(blank=True, null=True)
    ip_address    = models.GenericIPAddressField(null=True, blank=True)
    user_agent    = models.TextField(blank=True)
    # timestamp
    Date_creation    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-Date_creation']

    def __str__(self):
        return f"[{self.action}] {self.utilisateur} — {self.objet_label} ({self.Date_creation:%d/%m/%Y %H:%M})"
