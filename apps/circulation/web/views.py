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
class CirculationView(LoginRequiredMixin, TemplateView):
    template_name = "pages/circulation_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        circulations = CirculationDocument.objects.select_related('document', 'initie_par').all()

        context['circulations'] = circulations
        context['can_create_circulation'] = PermissionService.peut_creer_circulation(self.request.user)

        return context


class CirculationDetailView(LoginRequiredMixin, TemplateView):
    template_name = "pages/circulation_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        pk = self.kwargs['pk']
        circulation = get_object_or_404(CirculationDocument, pk=pk)
        etapes = circulation.etapes.select_related('destinataire', 'traite_par').all()

        context['circulation'] = circulation
        context['etapes'] = etapes

        return context


class CirculationCreateView(LoginRequiredMixin, CanCreateCirculationMixin, TemplateView):
    template_name = "circulation_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        document = get_object_or_404(Document, pk=self.kwargs['document_pk'])
        utilisateurs = Utilisateur.objects.all()

        context['document'] = document
        context['utilisateurs'] = utilisateurs

        return context

    def post(self, request, *args, **kwargs):
        document = get_object_or_404(Document, pk=self.kwargs['document_pk'])
        titre = request.POST.get('titre')
        description = request.POST.get('description', '')
        destinataires = request.POST.getlist('destinataires[]')

        circulation = CirculationDocument.objects.create(
            document=document,
            titre=titre,
            description=description,
            initie_par=request.user,
            statut=StatutCirculation.EN_COURS,
        )

        for ordre, user_id in enumerate(destinataires, start=1):
            EtapeCirculation.objects.create(
                circulation=circulation,
                ordre=ordre,
                destinataire=Utilisateur.objects.get(pk=user_id),
            )

        AuditService.log(request, ActionAudit.CIRCULATION, circulation, {
            'action': 'creation_circuit',
            'document': document.titre,
            'etapes': len(destinataires),
        })

        return redirect('circulation_detail', pk=circulation.pk)


@login_required
@require_POST
def etape_traiter(request, etape_pk):
    etape = get_object_or_404(EtapeCirculation, pk=etape_pk, destinataire=request.user)
    statut = request.POST.get('statut')
    commentaire = request.POST.get('commentaire', '')

    etape.statut = statut
    etape.commentaire = commentaire
    etape.traite_par = request.user
    etape.date_traitement = timezone.now()
    etape.save()

    circulation = etape.circulation
    etapes_restantes = circulation.etapes.filter(statut=StatutCirculation.EN_ATTENTE)
    if not etapes_restantes.exists():
        circulation.statut = StatutCirculation.CLOS
        circulation.date_fin = timezone.now()
        circulation.save()

    AuditService.log(request, ActionAudit.CIRCULATION, etape, {
        'statut': statut,
        'commentaire': commentaire,
    })

    return JsonResponse({'success': True, 'statut': etape.statut})


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
