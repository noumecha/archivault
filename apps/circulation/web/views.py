from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from apps.circulation.models import *
from apps.circulation.services.audit_service import AuditService
from apps.circulation.services.permission_service import PermissionService
from apps.documents.models import Document
from apps.users.models import Utilisateur
from config.views import BaseCRUDView
from config.mixins.permissions import RoleRequiredMixin
from config.roles import RoleUtilisateur, is_admin, is_superadmin, is_superviseur
from apps.administration.models import Cellule
from web_project import TemplateLayout
from apps.circulation.models import CirculationDocument, StatutCirculation, EtapeCirculation

"""
    Fonctions utilitaires pour la récupération des utilisateurs et des documents selon le rôle
"""
def get_documents_for_user(user):
    """Retourne la liste des documents accessibles pour les formulaires selon le rôle."""
    if is_admin(user) or is_superadmin(user):
        return Document.objects.all()
    elif is_superviseur(user) or hasattr(user, 'cellule'):
        return Document.objects.filter(cellule=user.cellule)
    return Document.objects.none()

def get_utilisateurs_for_user(user):
    """Retourne la liste des utilisateurs assignables selon le rôle."""
    if is_admin(user) or is_superadmin(user):
        return Utilisateur.objects.all()
    elif is_superviseur(user) and hasattr(user, 'cellule'):
        return Utilisateur.objects.filter(cellule=user.cellule)
    return [user]

# ─────────────────────────────────────────────
# MIXINS CUSTOM
# ─────────────────────────────────────────────
class CanAssignTaskMixin(UserPassesTestMixin):
    """Mixin pour vérifier si l'utilisateur peut assigner des tâches."""
    def test_func(self):
        return PermissionService.peut_assigner_tache(self.request.user)

    def handle_no_permission(self):
        return redirect('tache_list')


class CanViewAllTasksMixin(UserPassesTestMixin):
    """Mixin pour vérifier si l'utilisateur peut voir toutes les tâches."""
    def test_func(self):
        return PermissionService.peut_voir_toutes_taches(self.request.user)

    def handle_no_permission(self):
        return redirect('tache_list')


class CanCreateCirculationMixin(UserPassesTestMixin):
    """Mixin pour vérifier si l'utilisateur peut créer une circulation."""
    def test_func(self):
        return PermissionService.peut_creer_circulation(self.request.user)

    def handle_no_permission(self):
        return redirect('circulation_list')


# ─────────────────────────────────────────────
# CIRCULATION
# ─────────────────────────────────────────────
class CirculationManagementView(RoleRequiredMixin, BaseCRUDView):
    """Vue de gestion des circuits de circulation."""
    model = CirculationDocument
    list_route = 'circulation_management'
    template_name = "pages/circulation_management.html"
    context_object_name = 'circulations'

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.RESPONSABLE,
        RoleUtilisateur.GESTIONNAIRE
    ]

    # Configuration des filtres pour BaseCRUDView
    filters = [
        ('statut', StatutCirculation, 'Statut'),
        ('initie_par', Utilisateur, 'Initié par'),
        ('document', Document, 'Document'),
    ]

    search_fields = ['titre', 'description', 'document__titre']
    headers = ["Document", "Titre", "Initié par", "Date Début", "Progression", "Statut"]

    def get_queryset(self, search_query=None):
        user = self.request.user
        queryset = super().get_queryset(search_query).select_related('document', 'initie_par')

        # Optimisation : prefetch l'étape actuelle pour la progression
        queryset = queryset.prefetch_related('etapes')

        if is_admin(user) or is_superadmin(user):
            return queryset

        # Un utilisateur voit ce qu'il a initié OU ce qui passe par lui (via les étapes)
        return queryset.filter(
            Q(initie_par=user) | Q(etapes__destinataire=user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user

        # Données pour les modals (création de circuit)
        context['statuts'] = StatutCirculation.choices

        # Filtrage des listes pour le formulaire d'initialisation
        if is_admin(user) or is_superadmin(user):
            context['utilisateurs'] = Utilisateur.objects.all()
            context['documents'] = Document.objects.all()
        else:
            # On ne propose que les utilisateurs de la même cellule pour les étapes
            context['utilisateurs'] = Utilisateur.objects.filter(cellule=user.cellule)
            context['documents'] = Document.objects.filter(cellule=user.cellule)

        # Injection des items filtrés dans les filtres de BaseCRUDView
        for f in context.get('filters', []):
            if f['name'] == 'initie_par':
                f['items'] = context['utilisateurs']
            if f['name'] == 'document':
                f['items'] = context['documents']

        return context

class CirculationDetailView(LoginRequiredMixin, TemplateView):
    """Vue détaillée pour voir la timeline et traiter l'étape actuelle."""
    template_name = "pages/circulation_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        circulation = get_object_or_404(
            CirculationDocument.objects.select_related('document', 'initie_par'),
            pk=self.kwargs['pk']
        )

        # Récupération ordonnée des étapes
        etapes = circulation.etapes.select_related('destinataire', 'traite_par').all().order_by('ordre')
        etape_actuelle = etapes.filter(est_actuelle=True).first()

        context['circulation'] = circulation
        context['etapes'] = etapes
        context['etape_actuelle'] = etape_actuelle
        context['choices_decisions'] = [
            StatutCirculation.VALIDE,
            StatutCirculation.REJETE,
            StatutCirculation.RETOURNE
        ]

        # Vérification si l'utilisateur actuel peut traiter l'étape
        context['peut_traiter'] = (
            etape_actuelle and
            etape_actuelle.destinataire == self.request.user and
            etape_actuelle.statut == StatutCirculation.EN_COURS
        )

        return context

# ─────────────────────────────────────────────
# TÂCHES - GESTION (Assignation)
# ─────────────────────────────────────────────
class TacheDetailView(LoginRequiredMixin, TemplateView):
    """Détail d'une tâche."""
    template_name = "pages/tache_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        user = self.request.user
        tache = get_object_or_404(Tache, pk=self.kwargs['pk'])
        commentaires = tache.commentaires.select_related('auteur').all()

        context['statuts'] = StatutTache.choices
        context['priorites'] = PrioriteTache.choices
        context['tache'] = tache
        context['commentaires'] = commentaires
        context['can_validate'] = PermissionService.peut_valider_tache(self.request.user, tache)

        context['documents'] = get_documents_for_user(user)
        context['utilisateurs'] = get_utilisateurs_for_user(user)

        return context

class TacheManagementView(RoleRequiredMixin, BaseCRUDView):
    model = Tache
    # form_class = TachesForm  # Assurez-vous d'avoir un TachesForm défini
    list_route = 'tache_management'
    template_name = "pages/tache_management.html"
    #list_template = "pages/tache_management.html"
    context_object_name = 'taches'

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.GESTIONNAIRE,
        RoleUtilisateur.RESPONSABLE,
    ]

    filters = [
        ('statut', StatutTache, 'Statut'),
        ('priorite', PrioriteTache, 'Priorité'),
        ('assignee_a', Utilisateur, 'Assigné à'),
        ('document', Document, 'Document'),
        ('assignee_par', Utilisateur, 'Assigné par'),
    ]

    search_fields = ['titre', 'description', 'document__titre']
    headers = ["Titre", "Document", "Assigné à", "Assigné par", "Statut", "Priorité", "Échéance"]
    fields = ['titre', 'document', 'assignee_a', 'assignee_par', 'statut', 'priorite', 'date_echeance']

    def get_queryset(self, search_query=None):
        user = self.request.user
        queryset = super().get_queryset(search_query).select_related('document', 'assignee_par', 'assignee_a')

        # 1. Admin & Superadmin : Tout voir
        if is_admin(user) or is_superadmin(user):
            return queryset

        # 2. Superviseur : Voir les tâches de sa cellule
        if is_superviseur(user):
            return queryset.filter(assignee_par__cellule=user.cellule)

        # 3. Utilisateur standard (Gestionnaire/Responsable) : Uniquement SES tâches
        # On fédère ici la vue "Mes Tâches"
        return queryset.filter(Q(assignee_a=user) | Q(assignee_par=user))

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        context['priorites'] = PrioriteTache.choices
        context['statuts'] = StatutTache.choices
        # Filtrage des options de formulaire/filtre selon la cellule
        # 🟢 Utilisation des helpers centralisés pour le formulaire d'ajout
        context['documents'] = get_documents_for_user(user)
        context['utilisateurs'] = get_utilisateurs_for_user(user)

        for f in context.get('filters', []):
            if f['name'] == 'assignee_a' or f['name'] == 'assignee_par':
                f['items'] = context['utilisateurs']
            if f['name'] == 'document':
                f['items'] = context['documents']

        return context

# ─────────────────────────────────────────────
# AUDIT LOG
# ─────────────────────────────────────────────
class AuditLogManagementView(RoleRequiredMixin, BaseCRUDView):
    """
    Vue de supervision et de filtrage du journal d'audit système.
    Hérite de BaseCRUDView pour bénéficier de la recherche et de la pagination.
    """
    model = AuditLog
    list_route = 'audit_log_management'  # Le nom de ta route d'URL web
    template_name = "pages/audit_log_management.html"
    context_object_name = 'logs'

    # Seuls les rôles de haute supervision ont le droit de voir l'audit
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
    ]

    # Configuration des filtres natifs de ton BaseCRUDView
    filters = [
        ('action', ActionAudit, 'Action'),
        ('statut', StatutAudit, 'Résultat'),
        ('utilisateur', Utilisateur, 'Opérateur'),
    ]

    search_fields = ['objet_label', 'ip_address', 'utilisateur__username', 'utilisateur__first_name', 'utilisateur__last_name']
    headers = ["Date & Heure", "Opérateur", "Action", "Cible", "Résultat", "Adresse IP", "Actions"]

    def get_queryset(self, search_query=None):
        """Optimisation ORM avec select_related pour le rendu du tableau."""
        queryset = super().get_queryset(search_query)
        # On cible le timestamp renommé en snake_case et indexé
        return queryset.select_related('utilisateur', 'content_type').order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Récupération de la liste des utilisateurs pour alimenter le filtre de recherche
        context['utilisateurs'] = Utilisateur.objects.all().order_by('username')

        # Injection dynamique des items dans la structure de filtrage de BaseCRUDView
        for f in context.get('filters', []):
            if f['name'] == 'utilisateur':
                f['items'] = context['utilisateurs']

        return context

class AuditLogDetailView(RoleRequiredMixin, TemplateView):
    """
    Vue détaillée pour inspecter les métadonnées d'une action spécifique
    (Payloads JSON, User-Agent complet, etc.).
    """
    template_name = "pages/audit_log_detail.html"

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        # Récupération du log ou 404
        log = get_object_or_404(
            AuditLog.objects.select_related('utilisateur', 'content_type'),
            pk=self.kwargs['pk']
        )

        context['log'] = log
        return context
