from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q

from apps.circulation.models import (
    CirculationDocument, EtapeCirculation, PrioriteTache,
    Tache, CommentaireTache,
    AuditLog, ActionAudit, StatutTache, StatutCirculation
)
from apps.circulation.services.audit_service import AuditService
from apps.circulation.services.permission_service import PermissionService
from apps.documents.models import Document
from apps.users.models import Utilisateur
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
    template_name = "circulation_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        circulations = CirculationDocument.objects.select_related('document', 'initie_par').all()

        context['circulations'] = circulations
        context['can_create_circulation'] = PermissionService.peut_creer_circulation(self.request.user)

        return context


class CirculationDetailView(LoginRequiredMixin, TemplateView):
    template_name = "circulation_detail.html"

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
# TÂCHES - MES TÂCHES (Exécution)
# ─────────────────────────────────────────────

class TacheView(LoginRequiredMixin, TemplateView):
    """Vue pour afficher les tâches assignées à l'utilisateur connecté."""
    template_name = "tache_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        # Tâches assignées à l'utilisateur
        mes_taches = Tache.objects.filter(
            assignee_a=self.request.user
        ).select_related('document', 'assignee_par')

        # Filtrage optionnel
        statut = self.request.GET.get('statut', '')
        priorite = self.request.GET.get('priorite', '')

        if statut:
            mes_taches = mes_taches.filter(statut=statut)
        if priorite:
            mes_taches = mes_taches.filter(priorite=priorite)

        context['taches'] = mes_taches
        context['statuts'] = StatutTache.choices
        context['priorites'] = PrioriteTache.choices
        context['selected_statut'] = statut
        context['selected_priorite'] = priorite

        return context


class TacheDetailView(LoginRequiredMixin, TemplateView):
    """Détail d'une tâche."""
    template_name = "tache_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        tache = get_object_or_404(Tache, pk=self.kwargs['pk'])
        commentaires = tache.commentaires.select_related('auteur').all()

        context['tache'] = tache
        context['commentaires'] = commentaires
        context['can_validate'] = PermissionService.peut_valider_tache(self.request.user, tache)

        return context


# ─────────────────────────────────────────────
# TÂCHES - GESTION (Assignation)
# ─────────────────────────────────────────────

class TacheManagementView(LoginRequiredMixin, CanViewAllTasksMixin, TemplateView):
    """Vue pour gérer toutes les tâches (assignation)."""
    template_name = "tache_management.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        # Toutes les tâches
        taches = Tache.objects.select_related('document', 'assignee_a', 'assignee_par').all()

        # Filtrage
        statut = self.request.GET.get('statut', '')
        priorite = self.request.GET.get('priorite', '')
        assignee = self.request.GET.get('assignee', '')
        document = self.request.GET.get('document', '')

        if statut:
            taches = taches.filter(statut=statut)
        if priorite:
            taches = taches.filter(priorite=priorite)
        if assignee:
            taches = taches.filter(assignee_a_id=assignee)
        if document:
            taches = taches.filter(document_id=document)

        context['taches'] = taches
        context['statuts'] = StatutTache.choices
        context['priorites'] = PrioriteTache.choices
        context['utilisateurs'] = Utilisateur.objects.all()
        context['documents'] = Document.objects.all()
        context['selected_statut'] = statut
        context['selected_priorite'] = priorite
        context['selected_assignee'] = assignee
        context['selected_document'] = document

        return context


class TacheCreateView(LoginRequiredMixin, CanAssignTaskMixin, TemplateView):
    """Créer une nouvelle tâche (depuis le menu)."""
    template_name = "tache_create_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        utilisateurs = Utilisateur.objects.all()
        documents = Document.objects.all()

        context['utilisateurs'] = utilisateurs
        context['documents'] = documents

        return context

    def post(self, request, *args, **kwargs):
        document = get_object_or_404(Document, pk=request.POST.get('document'))

        tache = Tache.objects.create(
            document=document,
            titre=request.POST.get('titre'),
            description=request.POST.get('description', ''),
            assignee_par=request.user,
            assignee_a=Utilisateur.objects.get(pk=request.POST.get('assignee_a')),
            statut=request.POST.get('statut', StatutTache.A_FAIRE),
            priorite=request.POST.get('priorite', PrioriteTache.NORMALE),
            date_echeance=request.POST.get('date_echeance') or None,
        )

        AuditService.log(request, ActionAudit.TACHE, tache, {
            'action': 'creation',
            'assignee_a': tache.assignee_a.username,
            'priorite': tache.priorite,
        })

        return redirect('tache_detail', pk=tache.pk)


class TacheCreateFromDocumentView(LoginRequiredMixin, CanAssignTaskMixin, TemplateView):
    """Créer une tâche depuis un document."""
    template_name = "tache_create_from_document.html"

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

        tache = Tache.objects.create(
            document=document,
            titre=request.POST.get('titre'),
            description=request.POST.get('description', ''),
            assignee_par=request.user,
            assignee_a=Utilisateur.objects.get(pk=request.POST.get('assignee_a')),
            statut=request.POST.get('statut', StatutTache.A_FAIRE),
            priorite=request.POST.get('priorite', PrioriteTache.NORMALE),
            date_echeance=request.POST.get('date_echeance') or None,
        )

        AuditService.log(request, ActionAudit.TACHE, tache, {
            'action': 'creation',
            'assignee_a': tache.assignee_a.username,
            'priorite': tache.priorite,
        })

        return redirect('tache_detail', pk=tache.pk)


@login_required
@require_POST
def tache_update(request, pk):
    """Mettre à jour une tâche."""
    tache = get_object_or_404(Tache, pk=pk)

    # Vérifier les permissions
    if tache.assignee_a != request.user and not PermissionService.peut_valider_tache(request.user, tache):
        return JsonResponse({'success': False, 'error': 'Permission refusée'}, status=403)

    ancien_statut = tache.statut

    tache.statut = request.POST.get('statut', tache.statut)
    tache.priorite = request.POST.get('priorite', tache.priorite)
    tache.date_echeance = request.POST.get('date_echeance', tache.date_echeance)

    if tache.statut == StatutTache.TERMINEE:
        tache.date_cloture = timezone.now()

    tache.save()

    # Ajouter un commentaire automatique
    CommentaireTache.objects.create(
        tache=tache,
        auteur=request.user,
        contenu=f"Statut mis à jour de '{ancien_statut}' à '{tache.statut}'",
        ancien_statut=ancien_statut,
        nouveau_statut=tache.statut,
    )

    AuditService.log(request, ActionAudit.TACHE, tache, {
        'action': 'mise_a_jour',
        'ancien_statut': ancien_statut,
        'nouveau_statut': tache.statut,
    })

    return JsonResponse({'success': True, 'statut': tache.statut})


@login_required
@require_POST
def tache_commenter(request, pk):
    """Ajouter un commentaire à une tâche."""
    tache = get_object_or_404(Tache, pk=pk)
    contenu = request.POST.get('contenu', '').strip()

    if contenu:
        CommentaireTache.objects.create(
            tache=tache,
            auteur=request.user,
            contenu=contenu,
        )

        AuditService.log(request, ActionAudit.TACHE, tache, {
            'action': 'commentaire',
            'contenu': contenu[:100] + '...' if len(contenu) > 100 else contenu,
        })

    return JsonResponse({'success': True})


# ─────────────────────────────────────────────
# AUDIT LOG
# ─────────────────────────────────────────────

class AuditLogListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "audit_log_list.html"

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
