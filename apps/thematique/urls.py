from django.urls import path
from . import views

urlpatterns = [
    path('', views.ThematiqueView.as_view(), name='thematique'),
]