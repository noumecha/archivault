from django.shortcuts import render
from django.views.generic import TemplateView

class CirculationView(TemplateView):
    template_name = "circulation/circulation.html"