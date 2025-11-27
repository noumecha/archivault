from django.views.generic import TemplateView, View
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import *
from apps.administration.models import *
from .forms import *
from .serializers import GroupSerializer, UserSerializer
from web_project import TemplateLayout
from config.views import *
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.shortcuts import render, redirect
from rest_framework_simplejwt.tokens import RefreshToken

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

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            # ✅ Création des tokens JWT
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            response = redirect("index")
            # ✅ Cookies sécurisés
            response.set_cookie(
                "access_token", access,
                httponly=True, secure=not settings.DEBUG,
                samesite="Lax", max_age=60*15
            )
            response.set_cookie(
                "refresh_token", str(refresh),
                httponly=True, secure=not settings.DEBUG,
                samesite="Lax", max_age=60*60*24*7
            )
            login(request, user)
            return response

        return render(request, self.template_name, {"error": "Identifiants invalides"})

class LogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect('login')
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

# api view
class LoginAPIView(TokenObtainPairView):
    """
    Authentifie l’utilisateur et crée les cookies JWT (access + refresh).
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            data = response.data
            access = data.get('access')
            refresh = data.get('refresh')

            # ✅ Crée la réponse finale avec cookies sécurisés
            res = Response({'message': 'Connexion réussie'}, status=status.HTTP_200_OK)
            res.set_cookie(
                'access_token',
                access,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=60 * 15  # 15 min
            )
            res.set_cookie(
                'refresh_token',
                refresh,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=60 * 60 * 24 * 7  # 7 jours
            )
            return res
        return response

class LogoutAPIView(APIView):
    """
    Supprime les cookies JWT.
    """
    def post(self, request):
        res = Response({'message': 'Déconnexion réussie'}, status=status.HTTP_200_OK)
        res.delete_cookie('access_token')
        res.delete_cookie('refresh_token')
        return res

# user CRUD view
class UserView(BaseCRUDView):
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
