from rest_framework import serializers
from .models import Chat, Message, Vectordb

class VectordbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vectordb
        fields = ['id_vector', 'index_faiss', 'index_pkl']

    def create(self, validated_data):
        return Vectordb.objects.create(**validated_data)

