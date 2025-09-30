from django.shortcuts import render
from django.views.generic import TemplateView

class HistoriqueView(TemplateView):
    template_name = "historique/historique.html"