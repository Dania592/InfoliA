from datetime import datetime
import os
import logging
import json

from core.model.rag_module import RagModule
from core.model.llm_module import LlmModule

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from django.conf import settings
from django.shortcuts import get_object_or_404

from api.models import User
from .models import Chat, Message
from .serializers import ChatSerializer, UploadedFileSerializer


rag = RagModule()
llm = LlmModule()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            logging.info(f"Début de l'upload de fichier: {request.data}")
            file_serializer = UploadedFileSerializer(data=request.data)
            if file_serializer.is_valid():
                logging.info(f"Données valides, sauvegarde du fichier")
                instance = file_serializer.save()
                logging.info(f"Fichier sauvegardé avec succès: {instance.file.path}")
                return Response({"message": "Fichier uploadé avec succès", "data": file_serializer.data}, status=201)
            else:
                logging.error(f"Erreurs de validation: {file_serializer.errors}")
                return Response(file_serializer.errors, status=400)

        except Exception as e:
            logging.error(f"Erreur lors de l'upload: {str(e)}")
            return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chat_id = data.get('chat_id')
            user_name = data.get('pseudo')
            question = data.get('message')
            try:
                chat = Chat.objects.get(id_chat=chat_id)

            except Chat.DoesNotExist:
                raise Chat.DoesNotExist("Chat inexistent dans le profil utilisateur")

            chat_name = chat.nom_chat
            logging.info(f"Chat trouvé/utilisé - ID: {chat.id_chat}, Nom: {chat_name}")
            faiss_path = get_chat_directory(user_name, chat_name)

            # Générer une réponse
            response, sources = llm.generate_response(question, faiss_path=faiss_path)

            message = Message.objects.create(
                id_chat=chat,
                question=question,
                reponse=response,
                date= datetime.now(),
                source=sources
            )

            result = response + "\n\n" + sources

            if isinstance(result, str):
                response_text = result
            else:
                # Autre format, tenter de convertir en string
                response_text = str(result)

            logging.info(f"Réponse LLM : {response_text[:50]}...")

            return Response({
                "message": "Message envoyé avec succès",
                "response": response_text
            }, status=status.HTTP_200_OK)
            
        except Chat.DoesNotExist as e:
            logging.error(f"Aucun chat trouvé: {str(e)}")
            return Response({"error": f"Aucun chat trouvé: {str(e)}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error(f"Erreur lors du traitement du message: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"error": "Méthode non autorisée"}, status=status.HTTP_400_BAD_REQUEST)

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
        # Créer le répertoire utilisateur s'il n'existe pas
        user_directory = os.path.join(settings.MEDIA_ROOT, f"user_{user_name}")
        os.makedirs(user_directory, exist_ok=True)
        logging.info(f"Répertoire utilisateur créé: {user_directory}")

        id_chat = f"user_{user.pseudo}.chat_{chat_name}"
        os.makedirs(chat_directory, exist_ok=True)
        pdf_path = os.path.join(chat_directory, data.get('pdf_name'))
        faiss_path = os.path.join(chat_directory, "index.faiss")
        pkl_path = os.path.join(chat_directory, "index.pkl")

        ## Création de la base FAISS
        rag.create_faiss_db([pdf_path], chat_directory)

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
def get_user_chats(request):
    try:
        data = json.loads(request.body)
        user_name = data.get('pseudo')
        
        # Vérifier que l'utilisateur existe
        user = get_object_or_404(User, pseudo=user_name)
        
        # Récupérer tous les chats de l'utilisateur
        chats = Chat.objects.filter(id_user=user)
        
        # Sérialiser les données
        serializer = ChatSerializer(chats, many=True)
        
        return Response({
            "chats": serializer.data
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({"error": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des chats: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)