from .models import *
from .forms import *
from config.views import BaseCRUDView
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages

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
    object_name = "directiongenerale"
