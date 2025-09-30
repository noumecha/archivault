from django.shortcuts import render
from django.views.generic import TemplateView

class RapportView(TemplateView):
    template_name = "rapports/rapports.html"