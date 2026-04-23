# apps/users/api/serializers.py

from rest_framework import serializers
from apps.users.models import Utilisateur


class UtilisateurSerializer(serializers.ModelSerializer):
    """Serializer pour l'API utilisateurs."""

    role_display = serializers.CharField(source='get_role_display', read_only=True)
    cellule_nom = serializers.CharField(source='cellule.__str__', read_only=True)

    class Meta:
        model = Utilisateur
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'role_display',
            'cellule',
            'cellule_nom',
            'is_active',
            'Date_creation',
        ]
        read_only_fields = ['id', 'Date_creation']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        """Création avec hashage du password."""
        password = validated_data.pop('password', None)
        user = Utilisateur(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Mise à jour avec hashage du password si fourni."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
