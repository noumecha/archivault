from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.circulation.models import (
    CirculationDocument, EtapeCirculation,
    Tache, CommentaireTache,PrioriteTache,
    AuditLog, ActionAudit, StatutTache, StatutCirculation
)
from apps.circulation.services.audit_service import AuditService
from apps.documents.models import Document
from apps.users.models import Utilisateur

class CirculationView(TemplateView):
    template_name = "circulation/circulation.html"

# ─────────────────────────────────────────────
# CIRCULATION
# ─────────────────────────────────────────────

@login_required
def circulation_list(request):
    circulations = CirculationDocument.objects.select_related('document', 'initie_par').all()
    return render(request, 'circulation/circulation_list.html', {'circulations': circulations})


@login_required
def circulation_detail(request, pk):
    circulation = get_object_or_404(CirculationDocument, pk=pk)
    etapes = circulation.etapes.select_related('destinataire', 'traite_par').all()
    return render(request, 'circulation/circulation_detail.html', {
        'circulation': circulation,
        'etapes': etapes,
    })


@login_required
def circulation_create(request, document_pk):
    document = get_object_or_404(Document, pk=document_pk)
    utilisateurs = Utilisateur.objects.all()

    if request.method == 'POST':
        titre       = request.POST.get('titre')
        description = request.POST.get('description', '')
        destinataires = request.POST.getlist('destinataires[]')

        circulation = CirculationDocument.objects.create(
            document    = document,
            titre       = titre,
            description = description,
            initie_par  = request.user,
            statut      = StatutCirculation.EN_COURS,
        )

        for ordre, user_id in enumerate(destinataires, start=1):
            EtapeCirculation.objects.create(
                circulation  = circulation,
                ordre        = ordre,
                destinataire = Utilisateur.objects.get(pk=user_id),
            )

        AuditService.log(request, ActionAudit.CIRCULATION, circulation, {
            'action': 'creation_circuit',
            'document': document.titre,
            'etapes': len(destinataires),
        })

        return redirect('circulation_detail', pk=circulation.pk)

    return render(request, 'circulation/circulation_form.html', {
        'document': document,
        'utilisateurs': utilisateurs,
    })


@login_required
@require_POST
def etape_traiter(request, etape_pk):
    etape = get_object_or_404(EtapeCirculation, pk=etape_pk, destinataire=request.user)
    statut      = request.POST.get('statut')
    commentaire = request.POST.get('commentaire', '')

    etape.statut          = statut
    etape.commentaire     = commentaire
    etape.traite_par      = request.user
    etape.date_traitement = timezone.now()
    etape.save()

    # Clore la circulation si toutes les étapes sont traitées
    circulation = etape.circulation
    etapes_restantes = circulation.etapes.filter(statut=StatutCirculation.EN_ATTENTE)
    if not etapes_restantes.exists():
        circulation.statut   = StatutCirculation.CLOS
        circulation.date_fin = timezone.now()
        circulation.save()

    AuditService.log(request, ActionAudit.CIRCULATION, etape, {
        'statut': statut,
        'commentaire': commentaire,
    })

    return JsonResponse({'success': True, 'statut': etape.statut})


# ─────────────────────────────────────────────
# TÂCHES
# ─────────────────────────────────────────────

@login_required
def tache_list(request):
    """Tâches assignées à l'utilisateur connecté."""
    mes_taches = Tache.objects.filter(assignee_a=request.user).select_related('document', 'assignee_par')
    return render(request, 'circulation/tache_list.html', {'taches': mes_taches})


@login_required
def tache_detail(request, pk):
    tache = get_object_or_404(Tache, pk=pk)
    commentaires = tache.commentaires.select_related('auteur').all()
    return render(request, 'circulation/tache_detail.html', {
        'tache': tache,
        'commentaires': commentaires,
    })


@login_required
def tache_create(request, document_pk):
    document    = get_object_or_404(Document, pk=document_pk)
    utilisateurs = Utilisateur.objects.all()

    if request.method == 'POST':
        tache = Tache.objects.create(
            document      = document,
            titre         = request.POST.get('titre'),
            description   = request.POST.get('description', ''),
            assignee_par  = request.user,
            assignee_a    = Utilisateur.objects.get(pk=request.POST.get('assignee_a')),
            statut        = request.POST.get('statut', StatutTache.A_FAIRE),
            priorite      = request.POST.get('priorite', PrioriteTache.NORMALE),
            date_echeance = request.POST.get('date_echeance'),
        )

        AuditService.log(request, ActionAudit.TACHE, tache, {
            'action': 'creation',
            'assignee_a': tache.assignee_a.username,
            'priorite': tache.priorite,
        })

        return redirect('tache_detail', pk=tache.pk)

    return render(request, 'circulation/tache_form.html', {
        'document': document,
        'utilisateurs': utilisateurs,
    })


@login_required
@require_POST
def tache_update(request, pk):
    tache = get_object_or_404(Tache, pk=pk)
    ancien_statut = tache.statut

    tache.statut        = request.POST.get('statut', tache.statut)
    tache.priorite      = request.POST.get('priorite', tache.priorite)
    tache.date_echeance = request.POST.get('date_echeance', tache.date_echeance)
    tache.save()

    # Ajouter un commentaire automatique
    CommentaireTache.objects.create(
        tache         = tache,
        auteur        = request.user,
        contenu       = f"Statut mis à jour de '{ancien_statut}' à '{tache.statut}'",
        ancien_statut = ancien_statut,
        nouveau_statut = tache.statut,
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
    tache = get_object_or_404(Tache, pk=pk)
    contenu = request.POST.get('contenu', '').strip()

    if contenu:
        CommentaireTache.objects.create(
            tache   = tache,
            auteur  = request.user,
            contenu = contenu,
        )

        AuditService.log(request, ActionAudit.TACHE, tache, {
            'action': 'commentaire',
            'contenu': contenu[:100] + '...' if len(contenu) > 100 else contenu,
        })

    return JsonResponse({'success': True})


# ─────────────────────────────────────────────
# AUDIT LOG
# ─────────────────────────────────────────────

@login_required
def audit_log_list(request):
    logs = AuditLog.objects.select_related('utilisateur').order_by('-Date_creation')[:100]
    return render(request, 'circulation/audit_log_list.html', {'logs': logs})
