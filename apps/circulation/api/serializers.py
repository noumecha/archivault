# apps/circulation/api/serializers.py
from rest_framework import serializers
from apps.circulation.models import *
from config.roles import *
from ..services.permission_service import *
from django.utils import timezone
from django.db import transaction

class EtapeCirculationSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle EtapeCirculation.
    """
    destinataire_name = serializers.SerializerMethodField()
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    circulation = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = EtapeCirculation
        fields = '__all__'

    def get_destinataire_name(self, obj):
        """
        Logique pour retourner le Full Name ou le Username
        """
        if obj.destinataire:
            full_name = obj.destinataire.get_full_name()
            # On retourne le full_name s'il n'est pas vide, sinon le username
            return full_name if full_name.strip() else obj.destinataire.username
        return None

class CirculationDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle CirculationDocument.
    """
    document_titre = serializers.ReadOnlyField(source='document.titre')
    initie_par_name = serializers.ReadOnlyField(source='initie_par.username')
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    etapes_count = serializers.SerializerMethodField()
    etapes = EtapeCirculationSerializer(many=True, required=True)
    etape_actuelle = serializers.SerializerMethodField()
    can_update = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = CirculationDocument
        fields = [
            'id', 'document', 'document_titre', 'titre', 'description',
            'initie_par', 'initie_par_name', 'statut', 'statut_display',
            'date_debut', 'date_fin', 'etapes_count',
            'Date_creation', 'Date_miseajour', 'etapes', 'etape_actuelle', 'can_update', 'can_delete'
        ]
        read_only_fields = ['initie_par', 'Date_creation', 'Date_miseajour']

    def validate(self, data):
        if self.instance:
            if self.instance.statut in [StatutCirculation.CLOS, StatutCirculation.VALIDE]:
                raise serializers.ValidationError(
                    "Cette circulation est terminée. Aucune modification n'est autorisée."
                )
        return data

    def get_can_delete(self, obj):
        user = self.context['request'].user
        return PermissionService.can_delete_circulation(user, obj)

    def get_can_update(self, obj):
        user = self.context['request'].user
        return PermissionService.can_update_circulation(user, obj)

    def update(self, instance, validated_data):
        etapes_data = validated_data.pop('etapes', None)
        print("données recues : ", etapes_data)
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if etapes_data is not None:
                # Logique : on ne peut modifier que les étapes "en attente" ou "en cours"
                # Pour faire simple et propre : on identifie les étapes existantes
                # Si vous voulez permettre l'ajout/suppression/réorganisation :

                # Récupérer les IDs des étapes envoyées pour savoir quoi supprimer
                keep_etapes_ids = [item.get('id') for item in etapes_data if item.get('id')]

                # Optionnel : Supprimer les étapes qui ne sont plus dans la liste
                # (uniquement celles non traitées pour la sécurité)
                instance.etapes.exclude(id__in=keep_etapes_ids).filter(
                    statut=StatutCirculation.EN_ATTENTE
                ).delete()

                for i, etape_item in enumerate(etapes_data):
                    etape_id = etape_item.get('id')

                    # Si l'étape existe, on la met à jour
                    if etape_id:
                        etape_inst = EtapeCirculation.objects.filter(id=etape_id, circulation=instance).first()
                        if etape_inst and etape_inst.statut in [StatutCirculation.EN_ATTENTE, StatutCirculation.EN_COURS]:
                            etape_inst.titre_etape = etape_item.get('titre_etape', etape_inst.titre_etape)
                            etape_inst.destinataire = etape_item.get('destinataire', etape_inst.destinataire)
                            etape_inst.date_echeance = etape_item.get('date_echeance', etape_inst.date_echeance)
                            etape_inst.ordre = etape_item.get('ordre', i + 1)
                            etape_inst.save()
                    else:
                        etape_item.pop('id', None)
                        etape_item.pop('circulation', None)
                        ordre_val = etape_item.pop('ordre', i + 1)

                        EtapeCirculation.objects.create(
                            circulation=instance,
                            ordre=ordre_val,
                            statut=StatutCirculation.EN_ATTENTE,
                            **etape_item
                        )
        return instance

    def get_etapes_count(self, obj):
        return obj.etapes.count()

    def get_etape_actuelle(self, obj):
        etape = obj.etapes.filter(est_actuelle=True).first()
        return EtapeCirculationSerializer(etape).data if etape else None

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
        if value and value < timezone.now().date():
            raise serializers.ValidationError("La date d'échéance ne peut pas être dans le passé.")
        return value
