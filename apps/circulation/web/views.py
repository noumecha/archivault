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
            context['utilisateurs'] = Utilisateur.objects.exclude(id=user.id)
            context['documents'] = Document.objects.all()
        else:
            # On ne propose que les utilisateurs de la même cellule pour les étapes
            context['utilisateurs'] = Utilisateur.objects.filter(cellule=user.cellule).exclude(id=user.id)
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

        tache = get_object_or_404(Tache, pk=self.kwargs['pk'])
        commentaires = tache.commentaires.select_related('auteur').all()

        context['statuts'] = StatutTache.choices
        context['priorites'] = PrioriteTache.choices
        context['tache'] = tache
        context['commentaires'] = commentaires
        context['can_validate'] = PermissionService.peut_valider_tache(self.request.user, tache)

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
    ]

    search_fields = ['titre', 'description', 'document__titre']
    headers = ["Titre", "Document", "Assigné à", "Statut", "Priorité", "Échéance"]
    fields = ['titre', 'document', 'assignee_a', 'statut', 'priorite', 'date_echeance']

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
        if is_admin(user) or is_superadmin(user):
            context['utilisateurs'] = Utilisateur.objects.all()
            context['documents'] = Document.objects.all()
        elif is_superviseur(user):
            # si c'est le superviseur on affiche uniquement les éléments de sa cellule
            context['utilisateurs'] = Utilisateur.objects.filter(cellule=user.cellule)
            context['documents'] = Document.objects.filter(cellule=user.cellule)
        else:
            # si c'est un utilisateur simple (responsable ou gestionnaire), on affiche seulement ceux à quoi il est lié
            context['utilisateurs'] = [user]
            context['documents'] = Document.objects.filter(cellule=user.cellule)

        for f in context.get('filters', []):
            if f['name'] == 'assignee_a':
                f['items'] = context['utilisateurs']
            if f['name'] == 'document':
                f['items'] = context['documents']

        return context

# ─────────────────────────────────────────────
# AUDIT LOG
# ─────────────────────────────────────────────
class AuditLogListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "pages/audit_log_list.html"

    def test_func(self):
        from apps.users.models import RoleUtilisateur
        return self.request.user.role in [
            RoleUtilisateur.SUPERADMIN,
            RoleUtilisateur.ADMIN,
            RoleUtilisateur.SUPERVISEUR,
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        logs = AuditLog.objects.select_related('utilisateur').order_by('-Date_creation')[:100]

        context['logs'] = logs

        return context
