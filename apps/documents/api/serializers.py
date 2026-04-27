# apps/documents/api/serializers.py
from rest_framework import serializers
from ..models import Document, TypeDocument, Theme, SousTypeDocument, Bailleurs, Avenants

class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'API Documents.
    Fournit les données nécessaires pour le rendu de la table et des formulaires.
    """
    # Champs en lecture seule pour l'affichage (utilisés par DocumentUI.js)
    type_document_display = serializers.StringRelatedField(source='type_document', read_only=True)
    theme_display = serializers.StringRelatedField(source='theme', read_only=True)
    etat_display = serializers.CharField(source='get_etat_display', read_only=True)
    cree_par_name = serializers.CharField(source='cree_par.username', read_only=True)

    # URL du fichier pour un accès direct si nécessaire
    fichier_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id',
            'titre',
            'type_document',
            'type_document_display',
            'theme',
            'theme_display',
            'etat',
            'etat_display',
            'fichier',
            'fichier_url',
            'metadonnees',
            'cree_par',
            'cree_par_name',
            'Date_creation',
        ]
        read_only_fields = ['id', 'Date_creation', 'cree_par']

    def get_fichier_url(self, obj):
        if obj.fichier and hasattr(obj.fichier, 'url'):
            return obj.fichier.url
        return None


class ThemeSerializer(serializers.ModelSerializer):
    cellule_info = serializers.SerializerMethodField()
    class Meta:
        model = Theme
        fields = ['id', 'libelle', 'description_theme', 'cellule', 'cellule_info', 'Date_creation']
        read_only_fields = ['id']

    def get_cellule_info(self, obj):
        if obj.cellule:
            return {
                "id": obj.cellule.id,
                "nom": obj.cellule.nom
            }
        return None

class TypeDocumentSerializer(serializers.ModelSerializer):
    cellule_info = serializers.SerializerMethodField()
    parent_type_display = serializers.StringRelatedField(source='parent_type', read_only=True)

    class Meta:
        model = TypeDocument
        fields = ['id', 'libelle', 'description_typedocument', 'cellule', 'cellule_info', 'parent_type', 'parent_type_display', 'Date_creation']
        read_only_fields = ['id']
        extra_kwargs = {
            'parent_type': {'required': False, 'allow_null': True}
        }

    def get_cellule_info(self, obj):
        if obj.cellule:
            return {
                "id": obj.cellule.id,
                "nom": obj.cellule.nom
            }
        return None

    def validate(self, data):
        parent = data.get('parent_type')
        cellule = data.get('cellule')
        if parent and not cellule:
            data['cellule'] = parent.cellule
        return data


class SousTypeDocumentSerializer(serializers.ModelSerializer):
    cellule_info = serializers.SerializerMethodField()
    type_document_display = serializers.StringRelatedField(source='type_document', read_only=True)

    class Meta:
        model = SousTypeDocument
        fields = ['id', 'libelle', 'description_soustypedocument', 'type_document', 'cellule_info', 'type_document_display', 'Date_creation']
        read_only_fields = ['id', 'Date_creation']
        extra_kwargs = {
            'type_document': {'required': True}
        }

    def get_cellule_info(self, obj):
        if obj.type_document and obj.type_document.cellule:
            return {
                "id": obj.type_document.cellule.id,
                "nom": obj.type_document.cellule.nom
            }
        return None


class AvenantSerializer(serializers.ModelSerializer):
    bailleur_display = serializers.StringRelatedField(source='bailleur', read_only=True)

    class Meta:
        model = Avenants
        fields = ['id', 'bailleur', 'bailleur_display', 'libelle', 'numero', 'Date_creation']
        read_only_fields = ['id', 'Date_creation']

class BailleurSerializer(serializers.ModelSerializer):
    cellule_display = serializers.StringRelatedField(source='cellule', read_only=True)
    class Meta:
        model = Bailleurs
        fields = ['id', 'libelle', 'Date_creation', 'cellule', 'cellule_display', 'abrevation', 'description']
        read_only_fields = ['id', 'Date_creation']
