# apps/users/web/views.py
from django.views.generic import TemplateView, View
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apps.users.serializers import GroupSerializer
from ..models import *
from apps.administration.models import *
from ..forms import *
from web_project import TemplateLayout
from config.views import *
from django.conf import settings
from django.shortcuts import render, redirect
from rest_framework_simplejwt.tokens import RefreshToken
from ..services.user_service import UserService
from config.roles import *
from config.mixins.permissions import *
from django.db.models import Q

# login view

class LoginView(View):
    template_name = "login.html"

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
    list_template = "user_list.html"
    filters = [
        ('cellule', Cellule, 'Unité de traitement'),
        ('role', RoleUtilisateur),
    ]
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

    def post(self, request, *args, **kwargs):
        if request.user.role not in ["superadmin", "administrateur", "superviseur"]:
            return JsonResponse({"success": False}, status=403)
        return super().post(request, *args, **kwargs)

    def get_queryset(self, search_query=None):

        # queryset autorisé selon le role
        qs = UserService.get_users_queryset(self.request.user)

        request = self.request

        # 🔹 filtres dynamiques
        filters = {}
        for key, value in request.GET.items():
            if key in ['search', 'page']:
                continue
            if value:
                filters[key] = value

        if filters:
            qs = qs.filter(**filters)

        # 🔹 recherche texte
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            qs = qs.filter(q_objects)

        return qs.order_by('-Date_creation')

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
