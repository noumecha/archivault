from django.views.generic import TemplateView, View
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import *
from .forms import *
from .serializers import GroupSerializer, UserSerializer
from django.views.generic import TemplateView
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from config.views import *

class UserProfileView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

# views for login & logout
class LoginAPIView(APIView):
    permission_classes = [] # public
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error' : 'Identifiants invalides', 'status' : status.HTTP_401_UNAUTHORIZED})

class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        logout(request)
        return Response({'success': 'Déconnecé avec succès!'})

# user CRUD view
class UserView(BaseCRUDView):
    model = Utilisateur
    form_class = UtilisateurForm
    list_route = 'user_list'
    list_template = "user_list.html"
    partial_template = "users/partials/users_partial.html"
    context_object_name = 'users'
    search_fields = ['username', 'first_name']

class UserAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def get(self, request):
        users = Utilisateur.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class GroupAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        groups = RoleUtilisateur.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)
