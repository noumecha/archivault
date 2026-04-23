# apps/users/web/views.py
from django.views.generic import TemplateView, View
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from apps.users.serializers import GroupSerializer, UserSerializer
from ..models import *
from apps.administration.models import *
from ..forms import *
from web_project import TemplateLayout
from config.views import *
from config.api.base_api_view import BaseAPIView
from django.conf import settings
from django.shortcuts import render, redirect
from rest_framework_simplejwt.tokens import RefreshToken
from ..services.user_service import UserService
from config.roles import *
from config.mixins.permissions import *
from django.db.models import Q

# login view

class LoginView(View):
    template_name = "pages/login.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, {})
        return context

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("index")
        return render(request, self.template_name)

class LogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect('login')
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

# user CRUD view
class UserView(RoleRequiredMixin, BaseCRUDView):
    model = Utilisateur
    form_class = UtilisateurForm
    list_route = 'utilisateur_list'
    list_template = "pages/user_list.html"
    filters = [
        ('cellule', Cellule, 'Unité de traitement'),
        ('role', RoleUtilisateur),
    ]
    # list of all roles for the form
    roles = RoleUtilisateur
    cellules = Cellule.objects.all()

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['roles'] = self.roles
        context['cellules'] = self.cellules
        return context
    context_object_name = 'users'
    search_fields = ['username', 'first_name']
    headers = ["Nom", "Prenom", "Role", "Email"]
    fields = ['username', 'first_name', 'role', 'email']
    delete_url = "utilisateur_delete"
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]

class GroupAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        groups = RoleUtilisateur.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

# users views
class UserProfileView(TemplateView):
    template_name = "user_profile.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

class UserPasswordView(TemplateView):
    template_name = "user_password_update.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
