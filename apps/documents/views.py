import json
import os
from django.views.generic import ListView
from django.views.generic import ListView, UpdateView
from .forms import *
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect, render
from django.contrib import messages
from config.views import BaseCRUDView
from django.db import transaction
from django.core.exceptions import PermissionDenied
from web_project import TemplateLayout
from dal import autocomplete
from datetime import datetime
from django.http import JsonResponse
from django.utils.text import slugify

#occupant view
class NiveauAccesDocumentView(BaseCRUDView):
    model = NiveauAccesDocument
    form_class = NiveauAccesDocumentsForm
    list_route = 'niveauaccess_list'
    list_template = 'niveauaccesss_list.html'
    context_object_name = 'niveauaccesss'
    object_name = 'niveauaccess'
    search_fields = ["niveau","description_niveauaccess"]
    filters = []
    headers = ["Libelle", "Description"]
    fields = ["niveau","description_niveauaccess"]
    delete_url = "niveauaccess_delete"

class SousTypeDocumentView(BaseCRUDView):
    model = SousTypeDocument
    form_class = SousTypeDocumentsForm
    list_route = 'soustypedocument_list'
    list_template = 'soustypedocument_list.html'
    context_object_name = 'soustypedocuments'
    object_name = 'soustypedocument'
    search_fields = ["libelle","description_soustypedocument"]
    filters = [('type_document', TypeDocument)]
    headers = ["Libelle", "Description", "Type"]
    fields = ["libelle","description_soustypedocument", "type_document"]
    delete_url = "soustypedocument_delete"

class ThemeListView(BaseCRUDView):
    model = Theme
    form_class = ThemesForm
    list_route = 'themes_list'
    list_template = 'themes_list.html'
    context_object_name = 'themes'
    search_fields = ["libelle","description_theme"]
    filters = []
    headers = ["Libelle", "Description"]
    fields = ["libelle","description_theme"]
    delete_url = "themes_delete"

class TypeDocumentView(BaseCRUDView):
    model = TypeDocument
    form_class = TypeDocumentsForm
    list_route = 'typedocument_list'
    list_template = 'typedocuments_list.html'
    context_object_name = 'typedocuments'
    search_fields = ["libelle","description_typedocument"]
    object_name = 'typedocument'
    headers = ["Libelle", "Description"]
    fields = ["libelle","description_typedocument"]
    delete_url = "typedocument_delete"

class DocumentView(BaseCRUDView):
    model = Document
    form_class = DocumentsForm
    list_route = 'documents_list'
    list_template = 'documents_list.html'
    partial_template = 'partials/documents_partial.html'
    context_object_name = 'documents'
    search_fields = [
        "titre",
        "fichier",
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

# managing doucments
class DocumentCreateMultipleView(ListView):
    template_name = "upload_multiple.html"
    form_class = UploadMultipleForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        files = request.FILES.getlist('fichiers')

        # Récupère la liste des actions JSON envoyées par le client
        actions_json = request.POST.getlist("actions[]")

        # Transforme la liste en un dictionnaire {nom_fichier: {action, documentId}}
        actions = {}
        for action_str in actions_json:
            action_data = json.loads(action_str)
            actions[action_data['name']] = action_data

        try:
            if form.is_valid():
                data = form.cleaned_data
                created_documents = []
                created_versions = []
                skipped = []

                with transaction.atomic():
                    for f in files:
                        name = os.path.splitext(f.name)[0]
                        titre = name.replace("_", " ").replace("-", " ").strip()

                        action_info = actions.get(f.name)
                        action = action_info['action'] if action_info else "create"

                        # ⚠ si utilisateur demande IGNORER
                        if action == "skip":
                            skipped.append(titre)
                            continue

                        doc_exist = Document.objects.filter(titre__iexact=titre).first()

                        # -----------------------------------------------------------
                        # 1️⃣ CAS A — DOCUMENT N’EXISTE PAS -> Création document
                        # -----------------------------------------------------------
                        if not doc_exist and action == "create":
                            doc = Document.objects.create(
                                titre=titre,
                                fichier=f,
                                type_document=data.get("type_document"),
                                sous_type=data.get("sous_type"),
                                theme=data.get("theme"),
                                cellule=data.get("cellule"),
                                etat=data.get("etat") or Document._meta.get_field('etat').default,
                                niveau_acces=data.get("niveau_acces"),
                                profil_document=data.get("profil_document") or Document._meta.get_field('profil_document').default,
                                cree_par=request.user if request.user.is_authenticated else None,
                                metadonnees=data.get("metadonnees") or None,
                                responsable_document=data.get("responsable_document"),
                            )

                            if data.get("regles_classement"):
                                doc.regles_classement.set(data.get("regles_classement"))

                            created_documents.append(doc)
                            continue

                        # -----------------------------------------------------------
                        # 2️⃣ CAS B — DOCUMENT EXISTE MAIS L’USER VEUT CRÉER UNE VERSION
                        # -----------------------------------------------------------
                        if doc_exist and action == "version":
                            last_version = doc_exist.versions.order_by("-numero_version").first()
                            next_version_number = (last_version.numero_version + 1) if last_version else 1

                            version = VersionDocument.objects.create(
                                # change the document title with the current date and hour
                                titre=f"{doc_exist.titre}-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}",
                                document=doc_exist,
                                numero_version=next_version_number,
                                fichier=f,
                                cree_par=request.user if request.user.is_authenticated else None,
                                responsable_version=data.get("responsable_document"),
                            )

                            created_versions.append(version)
                            continue

                        # -----------------------------------------------------------
                        # 3️⃣ CAS C — DOCUMENT EXISTE MAIS L’USER VEUT REMPLACER
                        # -----------------------------------------------------------
                        if doc_exist and action == "overwrite":
                            doc_exist.fichier = f
                            doc_exist.modifier_par = request.user
                            doc_exist.save()

                            created_documents.append(doc_exist)
                            continue

                if created_documents:
                    return JsonResponse({
                        "success": True,
                        "message": f"{len(created_documents)} document(s) enregistré(s) avec succès."
                    })

                if created_versions:
                    return JsonResponse({
                        "success": True,
                        "message": f"{len(created_versions)} nouvelle(s) version(s) créées."
                    })

            return JsonResponse({
                "success": False,
                "message": "Erreur lors de l'enregistrement",
                "errors" : form.errors
            })
        except Exception as e:
            return e

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

class DocumentListView(ListView):
    model = Document
    template_name = "list.html"
    context_object_name = "documents"
    paginate_by = 24

    def get_queryset(self):
        qs = super().get_queryset().select_related('type_document', 'theme', 'cellule')
        q = self.request.GET.get('q')
        type_id = self.request.GET.get('type')
        theme_id = self.request.GET.get('theme')
        extension = self.request.GET.get('ext')
        if q:
            qs = qs.filter(titre__icontains=q)
        if type_id:
            qs = qs.filter(type_document_id=type_id)
        if theme_id:
            qs = qs.filter(theme_id=theme_id)
        if extension:
            qs = qs.filter(fichier__iendswith='.' + extension.lstrip('.'))
        return qs.order_by('-Date_creation')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['types'] = TypeDocument.objects.all()
        ctx['themes'] = Theme.objects.all()
        ctx['selected_type'] = self.request.GET.get('type', '')
        ctx['selected_theme'] = self.request.GET.get('theme', '')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['ext'] = self.request.GET.get('ext', '')
        return ctx

class DocumentUpdateView(UpdateView):
    model = Document
    form_class = DocumentsForm
    template_name = "edit.html"
    success_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        layout_context = TemplateLayout.init(self, {})
        context.update(layout_context)
        context['document'] = self.object
        return context

    def dispatch(self, request, *args, **kwargs):
        """🔐 Vérifie les droits d'accès avant toute action"""
        document = self.get_object()
        user = request.user

        # L’administrateur a tous les droits
        if user.is_superuser or getattr(user, 'role', '') == 'admin':
            return super().dispatch(request, *args, **kwargs)

        # Gestion selon le profil du document
        if document.profil_document == 'consultatif':
            # Lecture seule → pas de modification
            raise PermissionDenied("Ce document est consultatif. Vous ne pouvez pas le modifier.")

        elif document.profil_document == 'imprimable':
            # Peut seulement le télécharger → pas d’édition
            raise PermissionDenied("Ce document est uniquement imprimable, pas modifiable.")

        elif document.profil_document == 'modifiable':
            # Peut modifier uniquement si c’est le créateur ou le responsable
            if document.cree_par != user and document.responsable_document != user:
                raise PermissionDenied("Vous n'avez pas la permission de modifier ce document.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        document = form.save(commit=False)
        if self.request.user.is_authenticated:
            document.modifier_par = self.request.user
        document.save()

        messages.success(self.request, "Document mis à jour avec succès.")
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class DocumentDeleteView(DeleteView):
    model = Document
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("list_document")

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_superuser or getattr(user, 'role', '') == 'admin'):
            raise PermissionDenied("Seul un administrateur peut supprimer des documents.")
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
