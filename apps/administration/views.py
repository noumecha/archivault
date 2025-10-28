from .models import *
from .forms import *
from config.views import BaseCRUDView

class CelluleView(BaseCRUDView):
    model = Cellule
    form_class = CellulesForm
    list_route = 'cellule_list'
    list_template = 'cellules_list.html'
    context_object_name = 'cellules'
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
    headers = ["Nom", "Description"]
    fields = ["nom", "description_division"]
    delete_url = "division_delete"

class MinistereView(BaseCRUDView):
    model = Ministere
    form_class = MinistereForm
    list_route = 'ministere_list'
    list_template = 'ministeres_list.html'
    context_object_name = 'ministeres'
    search_fields = ["nom","description_ministere"]
    headers = ["Nom", "Description"]
    fields = ["nom", "description_ministere"]
    delete_url = "ministere_delete"
