from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class AuthService:
    @staticmethod
    def generate_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def authenticate_user(username, password):
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            return user
        return None
