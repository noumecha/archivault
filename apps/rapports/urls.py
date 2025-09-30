from django.urls import path
from . import views

urlpatterns = [
    path('', views.RapportView.as_view(), name='rapports'),
]