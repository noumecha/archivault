from django.views.generic import TemplateView, View
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import Utilisateur, RoleUtilisateur
from .serializers import GroupSerializer, UserSerializer
from django.views.generic import TemplateView
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

# views for user management
class UserView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

class UserProfileView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
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

class UserAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
