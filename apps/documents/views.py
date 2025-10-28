from django.views.generic import ListView
from django.views.generic import CreateView, ListView, UpdateView, TemplateView, View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import *
from .serializers import SousTypeDocumentSerializer
from .forms import *
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from config.views import BaseCRUDView
from django.db import transaction
from web_project import TemplateLayout
import os
from django.utils.text import slugify

#occupant view
class NiveauAccesDocumentView(BaseCRUDView):
    model = NiveauAccesDocument
    form_class = NiveauAccesDocumentsForm
    list_route = 'niveauaccess_list'
    list_template = 'niveauaccesss_list.html'
    partial_template = 'partials/niveauaccesss_partial.html'
    context_object_name = 'niveauaccesss'
    search_fields = ["niveau","description_niveauaccess"]

class SousTypeDocumentView(BaseCRUDView):
    model = SousTypeDocument
    form_class = SousTypeDocumentsForm
    list_route = 'soustypedocument_list'
    list_template = 'soustypedocument_list.html'
    partial_template = 'partials/soustypedocument_partial.html'
    context_object_name = 'soustypedocuments'
    search_fields = ["libelle","description_soustypedocument"]

class ThemeListView(BaseCRUDView):
    model = Theme
    form_class = ThemesForm
    list_route = 'themes_list'
    list_template = 'themes_list.html'
    partial_template = 'partials/themes_partial.html'
    context_object_name = 'themes'
    search_fields = ["libelle","description_theme"]

class TypeDocumentView(BaseCRUDView):
    model = TypeDocument
    form_class = TypeDocumentsForm
    list_route = 'typedocument_list'
    list_template = 'typedocuments_list.html'
    partial_template = 'partials/typedocuments_partial.html'
    context_object_name = 'typedocuments'
    search_fields = ["libelle","description_typedocument"]

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
        if not files:
            messages.error(request, "Aucun fichier sélectionné.")
            return render(request, self.template_name, {"form": form})

        if form.is_valid():
            data = form.cleaned_data
            created = []
            with transaction.atomic():
                for f in files:
                    # créer un titre lisible à partir du nom de fichier
                    name = os.path.splitext(f.name)[0]
                    titre = name.replace('_', ' ').replace('-', ' ').strip()
                    # slug unique si besoin
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
                        #cree_par=request.user if request.user.is_authenticated else None,
                        metadonnees=data.get("metadonnees") or None,
                    )
                    if data.get("regles_classement"):
                        doc.regles_classement.set(data.get("regles_classement"))
                    created.append(doc)
            messages.success(request, f"{len(created)} document(s) créés.")
            return redirect("list_document")
        else:
            return render(request, self.template_name, {"form": form})


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
    success_url = reverse_lazy("list_document")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        layout_context = TemplateLayout.init(self, {})
        context.update(layout_context)
        context['document'] = self.object
        return context

    def form_valid(self, form):
        messages.success(self.request, "✅ Document mis à jour avec succès.")
        return super().form_valid(form)
