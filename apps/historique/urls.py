from django.urls import path
from . import views

urlpatterns = [
    path('', views.HistoriqueView.as_view(), name='historique'),
]