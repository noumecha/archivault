# apps/users/api/serializers.py

from rest_framework import serializers
from apps.users.models import RoleUtilisateur, Utilisateur
from config.roles import *


class UtilisateurSerializer(serializers.ModelSerializer):
    """Serializer pour l'API utilisateurs."""

    role_display = serializers.CharField(source='get_role_display', read_only=True)
    #cellule_nom = serializers.CharField(source='cellule.__str__', read_only=True)
    cellule_nom = serializers.StringRelatedField(source='cellule', read_only=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

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
            'password'
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

    def validate(self, data):
        request = self.context.get('request')
        if not request:
            return data

        current_user = request.user
        target_role = data.get('role')
        target_cellule = data.get('cellule')

        if is_admin(current_user):
            if target_role == RoleUtilisateur.SUPERADMIN or target_role == RoleUtilisateur.ADMIN:
                raise serializers.ValidationError({"role": "Vous ne pouvez pas créer de Super Administrateur ou Administrateur."})

        elif is_superviseur(current_user):
            allowed = [RoleUtilisateur.GESTIONNAIRE, RoleUtilisateur.RESPONSABLE]
            if target_role not in allowed:
                raise serializers.ValidationError({"role": "Vous n'avez pas le droit d'assigner ce rôle."})
            if target_cellule and target_cellule != current_user.cellule:
                raise serializers.ValidationError({"cellule": "Vous ne pouvez créer des utilisateurs que dans votre propre cellule."})

        return data

class UtilisateurProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'username', 'email', 'avatar']
        read_only_fields = ['username'] # Sécurité : on ne change pas le username ici

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data
