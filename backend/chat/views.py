from django.shortcuts import render
from core.model.rag_module import RagModule
from core.model.llm_module import LlmModule
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from api.models import User
from .models import Chat
from .serializers import ChatSerializer
from django.conf import settings
import os
import logging
import json

rag = RagModule()
llm = LlmModule()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def chat(request):
    return render(request, 'chat.html')

@api_view(['POST'])
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_name = data.get('chat_name')
        user_name = data.get('pseudo')
        question = data.get('question')
        logging.info(f"Chat: {chat_name}, Utilisateur: {user_name}, Question: {question}")

        faiss_path = get_chat_directory(user_name, chat_name)

        result = llm.generate_response(question, faiss_path=faiss_path)


        ## TODO : enregister le message dans la BD

        logging.info(f"Chat: {chat_name}, Utilisateur: {user_name}, Question: {question}, Result: {result}")

        return Response({
                "message": "Connexion réussie !",
                "response": result[0]['generated_text']
            }, status=status.HTTP_200_OK)
    return Response("serializer.errors", status=status.HTTP_400_BAD_REQUEST)

def get_chat_directory(user_id, chat_name):
    return os.path.join(settings.MEDIA_ROOT, f"user_{user_id}", f"chat_{chat_name}")

@api_view(['POST'])
def create_chat(request):
    try :
        data = json.loads(request.body)
        chat_name = data.get('chat_name')
        user_name = data.get('pseudo')

        ## Récupérer le fichier PDF dans le dossier du chat
        chat_directory = get_chat_directory(user_name, chat_name)
        print(chat_directory)

        # Vérifier que l'utilisateur existe
        user = get_object_or_404(User, pseudo=user_name)

        # TODO : Créer le Chat => remplacer par le serializer
        id_chat = f"user_{user.pseudo}.chat_{chat_name}"
        os.makedirs(chat_directory, exist_ok=True)
        pdf_path = os.path.join(chat_directory, data.get('pdf_name'))

        faiss_path = os.path.join(chat_directory, "index.faiss")
        pkl_path = os.path.join(chat_directory, "index.pkl")

        ## Création de la base FAISS
        rag.create_faiss_db([pdf_path], chat_directory)

        # ==> remplacer par le serializer
        chat = Chat.objects.create(
            id_chat=id_chat,
            nom_chat=chat_name,
            id_user=user,
            index_faiss=faiss_path.replace(settings.MEDIA_ROOT, "").lstrip("/"),
            index_pkl=pkl_path.replace(settings.MEDIA_ROOT, "").lstrip("/")
        )

        return Response({
            "message": "Chat créé avec succès",
            "chat_id": chat.id_chat,
            "vector_db": ChatSerializer(chat).data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def load_chat(request):
    try:
        data = json.loads(request.body)
        chat_name = data.get('chat_name')
        user_name = data.get('pseudo')

        user = get_object_or_404(User, pseudo=user_name)
        ## Récuperation du chat ? id ?
        chat = get_object_or_404(Chat, pseudo=chat_name)


    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
