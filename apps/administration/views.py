from apps.documents.models import Bailleurs, EtatDocument, ProfilDoc, SousTypeDocument, Theme, TypeDocument
from apps.users.models import RoleUtilisateur
from .models import *
from .forms import *
from config.views import BaseCRUDView
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.contrib import messages
from config.utils.utils import generates_filters

class CelluleView(BaseCRUDView):
    model = Cellule
    form_class = CellulesForm
    list_route = 'cellule_list'
    list_template = 'cellules_list.html'
    context_object_name = 'cellules'
    object_label = 'Unité de traitement'
    search_fields = ["nom","description_cellule"]
    headers = ["Nom", "Description"]
    fields = ["nom", "description_cellule"]
    delete_url = "cellule_delete"
    manage_url = "cellule_manage"
    manage_menu = [
        {"label": "Statistiques", "icon": "ri-bar-chart-line me-1", "section": "stats"},
        {"label": "Utilisateurs", "icon": "ri-user-2-line me-1", "section": "users"},
        {"label": "Documents", "icon": "ri-folders-line me-1", "section": "docs"},
        {"label": "Types de Documents", "icon": "ri-folder-settings-line me-1", "section": "docstypes"},
        {"label": "Bailleurs", "icon": "ri-wallet-2-fill me-1", "section": "bailleurs"},
        {"label": "Avenants", "icon": "ri-bill-fill me-1", "section": "avenants"},
    ]
    manage_template = 'cellules/manage_base.html'

    def manage_docstypes(self, request, context, obj):
        template = self.get_manage_template("docstypes")
        return render(request, template, context)

    def manage_docs(self, request, context, obj):
        template = self.get_manage_template("docs")
        filters = [
            ('type_document', TypeDocument),
            ('sous_type', SousTypeDocument),
            ('etat', EtatDocument),
            ('profil_document', ProfilDoc, 'Profil du Document'),
            ('theme', Theme)
        ]
        context['filters'] = generates_filters(filters)
        return render(request, template, context)

    def manage_bailleurs(self, request, context, obj):
        template = self.get_manage_template("bailleurs")
        return render(request, template, context)

    def manage_avenants(self, request, context, obj):
        template = self.get_manage_template("avenants")
        filters = [
            ('bailleur', Bailleurs),
        ]
        context['filters'] = generates_filters(filters)
        return render(request, template, context)

    def manage_users(self, request, context, obj):
        # Logiques personnalisées pour la section membres
        filters = [
            ('cellule', Cellule, 'Unité de traitement'),
            ('role', RoleUtilisateur),
        ]
        template = self.get_manage_template("users")
        context['filters'] = generates_filters(filters)
        return render(request, template, context)

    def manage_stats(self, request, context, obj):
        # Logiques personnalisées pour la section membres
        # context["membres"] = obj.membres.all() # Exemple
        template = self.get_manage_template("stats")
        return render(request, template, context)

class DivisionView(BaseCRUDView):
    model = Division
    form_class = DivisionForm
    list_route = 'division_list'
    list_template = 'divisions_list.html'
    context_object_name = 'divisions'
    search_fields = ["nom","description_division"]
    headers = ["Nom", "Description", "Statut"]
    fields = ["nom", "description_division", "statut"]
    delete_url = "division_delete"
    manage_url = "division_manage"
    # 🔹 Déclaration des actions personnalisées
    custom_actions = {
        "toggle_status": "toggle_status_action"
    }

    def toggle_status_action(self, request, pk):
        """Active ou désactive une division"""
        division = get_object_or_404(Division, pk=pk)
        if division.statut == 'activé':
            division.statut = 'desactivé'
        else:
            division.statut = 'activé'
        division.save()
        messages.success(request, f"La division '{division.nom}' a été {division.statut}.")
        return redirect(self.list_route)

class MinistereView(BaseCRUDView):
    model = Ministere
    form_class = MinistereForm
    list_route = 'ministere_list'
    list_template = 'ministeres_list.html'
    context_object_name = 'ministeres'
    search_fields = ["nom","description_ministere","code","abrevation"]
    headers = ["Nom", "Description","Code","abrevation"]
    fields = ["nom", "description_ministere","code","abrevation"]
    delete_url = "ministere_delete"
    manage_url = "ministere_manage"

class DirectionGeneraleView(BaseCRUDView):
    model = DirectionGenerale
    form_class = DirectionGeneraleForm
    list_route = 'directiongenerale_list'
    list_template = 'directiongenerales_list.html'
    context_object_name = 'directiongenerales'
    search_fields = ["nom","description_direction_generale"]
    headers = ["Nom", "Description", "Ministere"]
    fields = ["nom", "description_direction_generale", "ministere"]
    delete_url = "directiongenerale_delete"
    manage_url = "directiongenerale_manage"
    object_name = "directiongenerale"
