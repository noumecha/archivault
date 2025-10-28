from django.urls import path
from .views import *
from config.utils.urls import *

urlpatterns = [
    *get_crud_urls(CelluleView, "cellule/cellules", "cellule"),
    *get_crud_urls(MinistereView, "ministere/ministeres", "ministere"),
    *get_crud_urls(DivisionView, "division/divisions", "division"),
]
