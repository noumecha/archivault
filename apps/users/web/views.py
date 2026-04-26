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
    def get_context_data(self, **kwargs):
        # On initialise le layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user

        # --- FILTRAGE DES RÔLES ---
        all_roles = list(RoleUtilisateur)
        if user.role == RoleUtilisateur.SUPERADMIN:
            filtered_roles = all_roles
        elif user.role == RoleUtilisateur.ADMIN:
            # Exclure superadmin et admin
            filtered_roles = [r for r in all_roles if r.value != RoleUtilisateur.SUPERADMIN and r.value != RoleUtilisateur.ADMIN]
        else: # Superviseur
            # Uniquement gestionnaire et responsable
            allowed = [RoleUtilisateur.GESTIONNAIRE, RoleUtilisateur.RESPONSABLE]
            filtered_roles = [r for r in all_roles if r.value in allowed]

        # --- FILTRAGE DES CELLULES ---
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            filtered_cellules = Cellule.objects.all()
        else:
            # Le superviseur est limité à SA cellule
            filtered_cellules = Cellule.objects.filter(id=user.cellule_id) if user.cellule else Cellule.objects.none()

        context['roles'] = filtered_roles
        context['cellules'] = filtered_cellules

        # IMPORTANT: Mettre à jour les filtres de recherche pour qu'ils
        # correspondent aux options autorisées
        for f in context.get('filters', []):
            if f['name'] == 'role':
                f['items'] = filtered_roles
            if f['name'] == 'cellule':
                f['items'] = filtered_cellules

        return context
    context_object_name = 'users'
    search_fields = ['username', 'first_name']
    headers = ["Nom", "Prenom", "Role", "Email"]
    fields = ['username', 'first_name', 'role', 'email']
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
    template_name = "pages/profile.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

class UserPasswordView(TemplateView):
    template_name = "pages/password_update.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
