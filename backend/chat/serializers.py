from rest_framework import serializers
from .models import Chat, Message, UploadedFile

from rest_framework import serializers
from .models import Chat

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id_chat', 'nom_chat', 'id_user', 'index_faiss', 'index_pkl']

    def create(self, validated_data):
        user = validated_data['id_user']
        chat_name = validated_data['nom_chat']

        validated_data['id_chat'] = f"user_{user.pseudo}.chat_{chat_name}"

        return Chat.objects.create(**validated_data)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id_message', 'id_chat', 'question', 'reponse', 'date', 'source']

    def create(self, validated_data):
        return Message.objects.create(**validated_data)

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = "__all__"