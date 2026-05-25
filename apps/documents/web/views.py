# apps/documents/web/views.py
import json
import os
from django.views.generic import ListView, TemplateView
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.circulation.models import ActionAudit, CirculationDocument, Tache
from apps.circulation.services.audit_service import AuditService
from ..forms import *
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from config.views import BaseCRUDView
from django.db import transaction
from django.core.exceptions import PermissionDenied
from web_project import TemplateLayout
from dal import autocomplete
from datetime import datetime
from django.http import JsonResponse
from django.utils.text import slugify
from ..services.permissions import DocumentPermissionService
from config.roles import *
from config.mixins.permissions import *
from ..services.metadata_service import DocumentMetadataService
from apps.circulation.models import *

#occupant view
class NiveauAccesDocumentView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    model = NiveauAccesDocument
    form_class = NiveauAccesDocumentsForm
    list_route = 'niveauaccess_list'
    list_template = 'pages/niveauaccesss_list.html'
    context_object_name = 'niveauaccesss'
    object_name = 'niveauaccess'
    search_fields = ["niveau","description_niveauaccess"]
    filters = []
    headers = ["Libelle", "Description"]
    fields = ["niveau","description_niveauaccess"]
    delete_url = "niveauaccess_delete"

class SousTypeDocumentView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    filters = [
        ('cellule', Cellule, 'Unité de traitement'),
        ('type_document', TypeDocument, 'Type Document'),
    ]
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            filtered_cellules = Cellule.objects.all()
        else:
            filtered_cellules = Cellule.objects.filter(id=user.cellule_id) if user.cellule else Cellule.objects.none()
        context['cellules'] = filtered_cellules

        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            context['types_documents'] = TypeDocument.objects.all()
        else:
            context['types_documents'] = TypeDocument.objects.filter(cellule_id=user.cellule_id) if user.cellule else TypeDocument.objects.none()

        for f in context.get('filters', []):
            if f['name'] == 'cellule':
                f['items'] = filtered_cellules
            if f['name'] == 'type_document':
                f['items'] = context['types_documents']
        return context

    model = SousTypeDocument
    form_class = SousTypeDocumentsForm
    list_route = 'soustypedocument_list'
    list_template = 'pages/soustypedocument_list.html'
    context_object_name = 'soustypedocuments'
    object_name = 'soustypedocument'
    search_fields = ["libelle","description_soustypedocument"]
    headers = ["Libelle", "Description", "Type"]
    fields = ["libelle","description_soustypedocument", "type_document"]

class ThemeListView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    filters = [
        ('cellule', Cellule, 'Unité de traitement'),
    ]
    # surchage de get_context_data pour afficher les filters en fonction des roles
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        # --- FILTRAGE DES CELLULES ---
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            filtered_cellules = Cellule.objects.all()
        else:
            filtered_cellules = Cellule.objects.filter(id=user.cellule_id) if user.cellule else Cellule.objects.none()
        context['cellules'] = filtered_cellules
        for f in context.get('filters', []):
            if f['name'] == 'cellule':
                f['items'] = filtered_cellules

        return context
    model = Theme
    form_class = ThemesForm
    list_route = 'themes_list'
    list_template = 'pages/themes_list.html'
    context_object_name = 'themes'
    search_fields = ["libelle","description_theme", "cellule__nom"]
    headers = ["Libelle", "Description", "Cellule"]
    fields = ["libelle","description_theme", "cellule"]

class BailleursView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    filters = [
        ('cellule', Cellule, 'Unité de traitement')
    ]
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            context['cellules_list'] = Cellule.objects.all()
        else:
            context['cellules_list'] = Cellule.objects.filter(id=user.cellule_id) if user.cellule else Cellule.objects.none()

        for f in context.get('filters', []):
            if f['name'] == 'cellule':
                f['items'] = context['cellules_list']
        return context
    model = Bailleurs
    form_class = BailleursFrom
    list_route = 'bailleurs_list'
    list_template = 'pages/bailleurs_list.html'
    context_object_name = 'bailleurs',
    search_fields = ["abrevation","libelle","description"]
    headers = ["Abrevation","Libelle"]
    fields = ["abrevation","libelle"]
    object_name = 'bailleur'

class AvenantsView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            context['bailleurs_list'] = Bailleurs.objects.all()
        else:
            context['bailleurs_list'] = Bailleurs.objects.filter(cellule_id=user.cellule_id) if user.cellule else Bailleurs.objects.none()

        for f in context.get('filters', []):
            if f['name'] == 'bailleur':
                f['items'] = context['bailleurs_list']
        return context

    model = Avenants
    form_class = AvenantsForm
    list_route = 'avenants_list'
    list_template = 'pages/avenants_list.html'
    context_object_name = 'avenants',
    search_fields = ["nom","prenom"]
    filters = [
        ('bailleur', Bailleurs),
    ]
    headers = ["Nom","Prenom","Bailleur"]
    fields = ["nom","prenom","bailleur"]
    object_name = 'avenant'


class TypeDocumentView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    filters = [
        ('cellule', Cellule, 'Unité de traitement'),
        ('parent_type', TypeDocument, 'Type parent'),
    ]
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            filtered_cellules = Cellule.objects.all()
        else:
            filtered_cellules = Cellule.objects.filter(id=user.cellule_id) if user.cellule else Cellule.objects.none()

        context['cellules'] = filtered_cellules
        # Ajouter les types pour le parent_type
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            context['parent_types'] = TypeDocument.objects.filter(parent_type__isnull=True)
        else:
            context['parent_types'] = TypeDocument.objects.filter(cellule_id=user.cellule_id, parent_type__isnull=True)

        for f in context.get('filters', []):
            if f['name'] == 'cellule':
                f['items'] = filtered_cellules
            if f['name'] == 'parent_type':
                f['items'] = context['parent_types']
        return context

    model = TypeDocument
    list_route = 'typedocument_list'
    list_template = 'pages/typedocuments_list.html'
    context_object_name = 'typedocuments'
    search_fields = ["libelle","description_typedocument", "cellule__nom"]
    object_name = 'typedocument'
    headers = ["Libelle", "Description"]
    fields = ["libelle","description_typedocument"]

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
        ('type_document', TypeDocument),
        ('sous_type', SousTypeDocument),
        ('etat', EtatDocument),
        ('profil_document', ProfilDoc, 'Profil document'),
        ('theme', Theme),
        ('cellule', Cellule, 'Unité de traitement'),
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

# managing doucments
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

def check_document(request):
    filename = request.GET.get("filename", "")
    name = os.path.splitext(filename)[0]
    titre = name.replace('_', ' ').replace('-', ' ').strip()

    exists = Document.objects.filter(titre__iexact=titre).first()

    if exists:
        return JsonResponse({
            "exists": True,
            "document_id": exists.id,
            "titre": exists.titre,
        })

    return JsonResponse({"exists": False})

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

class TypeDocumentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = TypeDocument.objects.all()
        if self.q:
            qs = qs.filter(
                Q(libelle__icontains=self.q) | Q(description__icontains=self.q)
            )
        return qs

class SousTypeDocumentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SousTypeDocument.objects.all()
        if self.q:
            qs = qs.filter(
                Q(libelle__icontains=self.q) | Q(description__icontains=self.q)
            )
        return qs

class DocumentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Document.objects.all()
        if self.q:
            qs = qs.filter(
                Q(titre__icontains=self.q)
            )
        return qs

class BailleurAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Bailleurs.objects.all()
        if self.q:
            qs = qs.filter(
                Q(libelle__icontains=self.q) | Q(abrevation__icontains=self.q)
            )
        return qs

class AvenantAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Avenants.objects.all()
        if self.q:
            qs = qs.filter(
                Q(nom__icontains=self.q) | Q(prenom__icontains=self.q)
            )
        return qs

# filtering structure base on administration
def getsoustypes(request):
    if request.method == 'GET':
        type_id = request.GET.get('type_id')
        if not type_id:
            return JsonResponse({'error': 'Aucun type selectionné'}, status=400)
        try:
            type_id = int(type_id)
            soustypes = SousTypeDocument.objects.filter(type_document=type_id)[:20]  # Limit to 20 results for performance
            soustypeslist = [{'id': soustype.id, 'text': soustype.libelle} for soustype in soustypes]
            return JsonResponse(soustypeslist, safe=False)
        except (ValueError, TypeDocument.DoesNotExist):
            return JsonResponse({'error': 'ID du type incorrect'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)
