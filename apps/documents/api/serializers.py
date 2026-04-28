# apps/documents/api/serializers.py
from rest_framework import serializers
from ..models import *

# Serializer principal du Document
class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'API Documents.
    Fournit les données nécessaires pour le rendu de la table et des formulaires.
    """
    # Champs calculés pour l'affichage (read_only)
    cellulle_display =  serializers.StringRelatedField(source='cellule', read_only=True, allow_null=True)
    theme_display =  serializers.StringRelatedField(source='theme', read_only=True, allow_null=True)
    type_doc_display =  serializers.StringRelatedField(source='type_document', read_only=True, allow_null=True)
    cree_par_display =  serializers.StringRelatedField(source='cree_par', read_only=True)
    modifier_par_display = serializers.StringRelatedField(source='modifier_par', read_only=True)
    sous_type_display = serializers.StringRelatedField(source='sous_type', read_only=True)

    # Pour l'upload, on accepte l'ID ou l'objet (géré par le write)
    # Mais pour la liste, on veut les détails
    class Meta:
        model = Document
        fields = [
            'id', 'titre', 'fichier', 'type_document', 'type_doc_display',
            'sous_type', 'sous_type_display', 'theme', 'theme_display', 'cellule', 'cellulle_display',
            'etat', 'niveau_acces', 'profil_document', 'metadonnees',
            'cree_par', 'cree_par_display', 'modifier_par', 'modifier_par_display',
            'Date_creation', 'Date_miseajour', 'bailleur', 'avenant'
        ]
        read_only_fields = ['cree_par', 'modifier_par', 'Date_creation', 'Date_miseajour']

class VersionDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionDocument
        fields = ['id', 'numero_version', 'fichier', 'Date_creation', 'cree_par_username']

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
