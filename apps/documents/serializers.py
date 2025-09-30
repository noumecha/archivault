from rest_framework import serializers
from .models import SousTypeDocument

class SousTypeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousTypeDocument
        fields = ['id', 'libelle']