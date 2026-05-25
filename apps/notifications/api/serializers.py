from rest_framework import serializers
from django.utils.timesince import timesince
from django.utils import timezone
from ..models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Notification.
    Gère l'affichage dynamique du temps et des métadonnées liées à l'objet source.
    """
    categorie_display = serializers.CharField(source='get_categorie_display', read_only=True)
    created_at_since = serializers.SerializerMethodField()
    notification_actions = serializers.SerializerMethodField()
    target_model = serializers.CharField(source='content_type.model', read_only=True, default='')

    class Meta:
        model = Notification
        fields = [
            'id', 'titre', 'message', 'categorie', 'categorie_display',
            'url_action', 'is_read', 'created_at', 'created_at_since',
            'notification_actions', 'object_id', 'content_type', 'target_model'
        ]
        read_only_fields = ['id', 'created_at', 'created_at_since', 'target_model']

    def get_created_at_since(self, obj):
        """Retourne le temps écoulé (ex: 'il y a 2 minutes')"""
        try:
            return timesince(obj.created_at, timezone.now())
        except Exception:
            return "à l'instant"

    def get_notification_actions(self, obj):
        """
        Définit ce que l'utilisateur peut faire avec cette notification.
        """
        objet_existe = True
        if obj.content_type_id and obj.object_id:
            objet_existe = (obj.content_object is not None)

        return {
            'can_mark_read': not obj.is_read,
            'can_delete': True, # Généralement un utilisateur peut supprimer ses notifs
            'has_target': obj.url_action is not None and objet_existe
        }

    def validate_url_action(self, value):
        """Vérifie que l'URL commence bien par un slash si c'est interne."""
        if value and not value.startswith('/') and not value.startswith('http'):
            return f"/{value}"
        return value
