# apps/administration/api/serializers.py
from rest_framework import serializers
from apps.users.models import RoleUtilisateur
from apps.administration.models import *

class MinistereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ministere
        fields = ['nom', 'code', 'abrevation', 'description_ministere', 'Date_creation', 'Date_miseajour']
        read_only_fields = ['id', 'Date_creation', 'Date_miseajour']

class DirectionGeneraleSerializer(serializers.ModelSerializer):
    ministere_display = serializers.StringRelatedField(source='ministere', read_only=True)

    class Meta:
        model = DirectionGenerale
        fields = ['id', 'nom', 'description_direction_generale', 'ministere', 'ministere_display', 'Date_creation', 'Date_miseajour']
        read_only_fields = ['id', 'Date_creation', 'Date_miseajour']

class DivisionSerializer(serializers.ModelSerializer):
    direction_generale_display = serializers.StringRelatedField(source='direction_generale', read_only=True)
    ministere_display = serializers.StringRelatedField(source='ministere', read_only=True)

    class Meta:
        model = Division
        fields = ['id', 'nom', 'ministere', 'ministere_display', 'direction_generale', 'direction_generale_display', 'statut', 'description_division', 'Date_creation', 'Date_miseajour']
        read_only_fields = ['id', 'Date_creation', 'Date_miseajour']

class CelluleSerializer(serializers.ModelSerializer):
    division_display = serializers.StringRelatedField(source='division', read_only=True)
    ministere_display = serializers.StringRelatedField(source='ministere', read_only=True)
    class Meta:
        model = Cellule
        fields = ['id', 'nom', 'description_cellule', 'division', 'division_display', 'ministere', 'ministere_display', 'accepte_bailleurs', 'Date_creation', 'Date_miseajour']
        read_only_fields = ['id', 'Date_creation', 'Date_miseajour']
