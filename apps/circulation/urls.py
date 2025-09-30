from django.urls import path
from . import views

urlpatterns = [
    path('', views.CirculationView.as_view(), name='circulation'),
]