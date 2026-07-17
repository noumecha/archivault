from rest_framework import serializers
from .models import Utilisateur, RoleUtilisateur
from apps.administration.models import Cellule

class UserSerializer(serializers.ModelSerializer):
    # En lecture : liste d'objets ou IDs
    cellules_supervisees_details = serializers.SerializerMethodField()
    # En écriture : liste d'IDs de cellules
    cellules_supervisees = serializers.PrimaryKeyRelatedField(
        queryset=Cellule.objects.all(),
        many=True,
        required=False
    )
    class Meta:
        model = Utilisateur
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'role', 'cellule', 'cellules_supervisees',
            'cellules_supervisees_details', 'is_active'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def get_cellules_supervisees_details(self, obj):
        return [
            {"id": c.id, "nom": c.nom}
            for c in obj.cellules_supervisees.all()
        ]

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleUtilisateur
        fields = ['id', 'nom']
