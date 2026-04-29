# apps/circulation/api/serializers.py

from rest_framework import serializers
from apps.circulation.models import Tache, CirculationDocument, CommentaireTache
from config.roles import *
from ..services.permission_service import *

class CirculationDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle CirculationDocument.
    """
    document_titre = serializers.ReadOnlyField(source='document.titre')
    initie_par_name = serializers.ReadOnlyField(source='initie_par.username')
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    etapes_count = serializers.SerializerMethodField()

    class Meta:
        model = CirculationDocument
        fields = [
            'id', 'document', 'document_titre', 'titre', 'description',
            'initie_par', 'initie_par_name', 'statut', 'statut_display',
            'date_debut', 'date_fin', 'etapes_count',
            'Date_creation', 'Date_miseajour'
        ]
        read_only_fields = ['initie_par', 'Date_creation', 'Date_miseajour']

    def get_etapes_count(self, obj):
        return obj.etapes.count()

class CommentaireTacheSerializer(serializers.ModelSerializer):
    auteur_name = serializers.ReadOnlyField(source='auteur.username')

    class Meta:
        model = CommentaireTache
        fields = ['id', 'auteur', 'auteur_name', 'contenu', 'ancien_statut', 'nouveau_statut', 'Date_creation']

class TacheSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Tache.
    Inclut les informations sur le document, l'assignateur et l'assigné.
    """
    document_titre = serializers.ReadOnlyField(source='document.titre')
    assignee_par_name = serializers.ReadOnlyField(source='assignee_par.username')
    assignee_a_name = serializers.ReadOnlyField(source='assignee_a.username')
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    priorite_display = serializers.CharField(source='get_priorite_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    commentaires = CommentaireTacheSerializer(many=True, read_only=True)
    tache_actions = serializers.SerializerMethodField()

    class Meta:
        model = Tache
        fields = [
            'id', 'document', 'document_titre', 'titre', 'description',
            'assignee_par', 'assignee_par_name', 'assignee_a', 'assignee_a_name',
            'statut', 'statut_display', 'priorite', 'priorite_display',
            'date_echeance', 'date_cloture', 'is_overdue', 'commentaires',
            'Date_creation', 'Date_miseajour', 'tache_actions'
        ]
        read_only_fields = ['assignee_par', 'date_cloture', 'Date_creation', 'Date_miseajour']

    def get_tache_actions(self, obj):
        user = self.context['request'].user
        return {
            'can_edit': PermissionService.peut_valider_tache(user, obj),
            'can_delete': PermissionService.peut_supprimer_tache(user, obj),
            'can_view': PermissionService.peut_voir_tache(user, obj),
        }

    def validate_date_echeance(self, value):
        from django.utils import timezone
        if value and value < timezone.now().date():
            raise serializers.ValidationError("La date d'échéance ne peut pas être dans le passé.")
        return value
