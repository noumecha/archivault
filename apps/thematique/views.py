from django.shortcuts import render
from django.views.generic import TemplateView

class ThematiqueView(TemplateView):
    template_name = "thematique/list.html"