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

    """def post(self, request):
        form = self.form_class(request.POST, request.FILES, user=request.user)
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
                        cellule = data.get("cellule")
                        if not is_admin(request.user) and not is_superadmin(request.user):
                            cellule = request.user.cellule
                        if not doc_exist and action == "create":
                            doc = Document.objects.create(
                                titre=titre,
                                fichier=f,
                                type_document=data.get("type_document"),
                                sous_type=data.get("sous_type"),
                                theme=data.get("theme"),
                                cellule=cellule,
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
            return e"""

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
    template_name = "pages/document_card_list.html"
    context_object_name = "documents"
    paginate_by = 24

    def apply_filters(self, qs):
        q = self.request.GET.get('q')
        type_id = self.request.GET.get('type')
        sous_type_id = self.request.GET.get('sous_type')
        profil = self.request.GET.get('profil')
        etat = self.request.GET.get('etat')
        theme_id = self.request.GET.get('theme')
        extension = self.request.GET.get('ext')
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')
        if q:
            qs = qs.filter(titre__icontains=q)
        if type_id:
            qs = qs.filter(type_document_id=type_id)
        if sous_type_id:
            qs = qs.filter(sous_type_id=sous_type_id)
        if profil:
            qs = qs.filter(profil_document=profil)
        if etat:
            qs = qs.filter(etat=etat)
        if theme_id:
            qs = qs.filter(theme_id=theme_id)
        if extension:
            qs = qs.filter(fichier__iendswith='.' + extension.lstrip('.'))
        if date_debut:
            qs = qs.filter(Date_creation__date__gte=date_debut)
        if date_fin:
            qs = qs.filter(Date_creation__date__lte=date_fin)
        return qs.order_by('-Date_creation')

    def get_queryset(self):
        user = self.request.user
        qs = DocumentPermissionService.get_visible_documents(user)
        return self.apply_filters(qs)

    def get_context_data(self, **kwargs):
        ctx = TemplateLayout.init(self, super().get_context_data(**kwargs))
        #ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['types'] = DocumentMetadataService.get_types(user)
        ctx['sous_types'] = DocumentMetadataService.get_sous_types(user)
        ctx['themes'] = DocumentMetadataService.get_themes(user)
        ctx['profils'] = ProfilDoc.choices
        ctx['etats'] = EtatDocument.choices
        ctx['selected_type'] = self.request.GET.get('type', '')
        ctx['selected_theme'] = self.request.GET.get('theme', '')
        ctx['selected_profil'] = self.request.GET.get('profil', '')
        ctx['selected_etat'] = self.request.GET.get('etat', '')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['ext'] = self.request.GET.get('ext', '')
        ctx['date_debut'] = self.request.GET.get('date_debut', '')
        ctx['date_fin'] = self.request.GET.get('date_fin', '')
        return ctx

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
