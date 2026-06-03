# apps/documents/web/views/DocumentView.py
from django.views.generic import TemplateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.circulation.models import CirculationDocument, Tache
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from config.views import BaseCRUDView
from django.core.exceptions import PermissionDenied
from web_project import TemplateLayout
from dal import autocomplete
from config.roles import *
from ...forms import *
from ...services.permissions import DocumentPermissionService
from config.mixins.permissions import *
from apps.circulation.models import *


class DocumentDetailView(LoginRequiredMixin, TemplateView):
    template_name = "pages/document_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)

        document = get_object_or_404(Document, pk=self.kwargs['pk'])

        # Récupérer les tâches associées
        taches = Tache.objects.filter(document=document)

        # utilisateurs
        utilisateurs = Utilisateur.objects.all()
        context['utilisateurs'] = utilisateurs

        # Récupérer les circulations associées
        circulations = CirculationDocument.objects.filter(document=document)

        # Log de consultation
        # AuditService.log(self.request, ActionAudit.CONSULTATION, document)

        context.update({
            'document': document,
            'taches': taches,
            'circulations': circulations,
            'utilisateurs': utilisateurs
        })

        return context

class DocumentUpdateView(UpdateView):
    model = Document
    form_class = DocumentsForm
    template_name = "pages/document_edit.html"
    success_url = None


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        layout_context = TemplateLayout.init(self, {})
        context.update(layout_context)

        context['document'] = self.object
        context['can_view'] = DocumentPermissionService.can_view(self.request.user, self.object)
        context['can_edit'] = DocumentPermissionService.can_edit(self.request.user, self.object)
        context['can_delete'] = DocumentPermissionService.can_delete(self.request.user, self.object)
        context['can_download'] = DocumentPermissionService.can_download(self.request.user, self.object)

        return context

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user

        if not DocumentPermissionService.can_view(user, self.object):
            raise PermissionDenied("Accès refusé.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        document = form.save(commit=False)
        document.modifier_par = self.request.user
        document.save()
        messages.success(self.request, "Document mis à jour avec succès.")
        return super().form_valid(form)

class DocumentDeleteView(DeleteView):
    model = Document
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("list_document")

    def dispatch(self, request, *args, **kwargs):
        document = self.get_object()
        user = request.user

        if not DocumentPermissionService.can_delete(user, document):
            raise PermissionDenied("Vous n'avez pas le droit de supprimer ce document.")

        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Document supprimé avec succès.")
        return super().delete(request, *args, **kwargs)

class DocumentCreateMultipleView(ListView):
    template_name = "pages/document_upload_multiple.html"
    form_class = UploadMultipleForm

    def get(self, request):
        form = self.form_class(user=request.user)
        ctx = {
            "form": form,
            "can_create_metadata": is_admin(request.user) or is_superadmin(request.user) or is_superviseur(request.user)
        }
        ctx["fields_per_row"] = 2
        return render(request, self.template_name, ctx)

class DocumentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Document.objects.all()
        if self.q:
            qs = qs.filter(
                Q(titre__icontains=self.q)
            )
        return qs

class DocumentView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.RESPONSABLE,
        RoleUtilisateur.GESTIONNAIRE,
    ]
    model = Document
    list_route = 'documents_list'
    list_template = 'pages/document_list.html'
    context_object_name = 'documents'
    search_fields = [
        "titre",
        "type_document",
        "sous_type",
        "theme",
        "cellule",
        "etat",
        "niveau_acces",
        "profil_document",
        "regles_classement",
        "metadonnees",
        "cree_par",
    ]
    filters = [
        ('cellule', Cellule, 'Unité de traitement'),
        ('type_document', TypeDocument),
        ('sous_type', SousTypeDocument),
        ('etat', EtatDocument),
        ('profil_document', ProfilDoc, 'Profil document'),
        ('theme', Theme),
        ('niveau_acces', NiveauAcces, 'Niveau d\'accès')
    ]
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        filtered_etat = EtatDocument.choices
        filtered_niveau_access = NiveauAcces.choices
        filtered_profil_documents = ProfilDoc.choices
        priorites = PrioriteTache.choices
        statuts = StatutTache.choices
        user = self.request.user
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            filtered_cellules = Cellule.objects.all()
            filtered_types = TypeDocument.objects.all()
            filtered_themes = Theme.objects.all()
            filtered_soustypes = SousTypeDocument.objects.all()
            filtered_utilisateurs = Utilisateur.objects.all()
            filtered_documents = Document.objects.all()
        else:
            filtered_documents = Document.objects.filter(cellule_id=user.cellule_id) if user.cellule else Document.objects.none()
            filtered_utilisateurs = Utilisateur.objects.filter(cellule_id=user.cellule_id) if user.cellule else Utilisateur.objects.none()
            filtered_cellules = Cellule.objects.filter(id=user.cellule_id) if user.cellule else Cellule.objects.none()
            filtered_types = TypeDocument.objects.filter(cellule_id=user.cellule_id) if user.cellule else TypeDocument.objects.none()
            filtered_themes = Theme.objects.filter(cellule_id=user.cellule_id) if user.cellule else Theme.objects.none()
            filtered_soustypes = SousTypeDocument.objects.filter(type_document__cellule_id=user.cellule_id) if user.cellule else SousTypeDocument.objects.none()

        context['cellules'] = filtered_cellules
        context['types_documents'] = filtered_types
        context['themes'] = filtered_themes
        context['sous_types'] = filtered_soustypes
        context['etats'] = filtered_etat
        context['niveau_access'] = filtered_niveau_access
        context['profil_documents'] = filtered_profil_documents
        context['priorites'] = priorites
        context['statuts'] = statuts
        context['utilisateurs'] = filtered_utilisateurs
        context['documents'] = filtered_documents

        # Mapping des filtres vers les querysets filtrés par rôle
        filter_mapping = {
            'cellule': filtered_cellules,
            'type_document': filtered_types,
            'theme': filtered_themes,
            'sous_type': filtered_soustypes,
        }
        for f in context.get('filters', []):
            if f['name'] in filter_mapping:
                f['items'] = filter_mapping[f['name']]
        return context
