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
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UploadedFileSerializer
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
            import traceback
            logging.error(traceback.format_exc())
            return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chat_id = data.get('chat_id')
            user_name = data.get('pseudo')
            question = data.get('message')
            
            # Logs de debugging
            logging.info(f"Recherche de chat avec id_chat={chat_id}, type={type(chat_id).__name__}")
            
            # Liste tous les chats disponibles
            all_chats = Chat.objects.all()
            logging.info(f"Chats disponibles: {[(c.id_chat, c.nom_chat) for c in all_chats]}")
            
            # Stratégie fallback: si on ne trouve pas le chat par ID, on prend le premier chat disponible
            try:
                # Essayer d'abord avec l'ID exact
                chat = Chat.objects.get(id_chat=chat_id)
            except Chat.DoesNotExist:
                if len(all_chats) > 0:
                    # Fallback: utiliser le premier chat disponible
                    logging.warning(f"Chat {chat_id} non trouvé. Utilisation du chat {all_chats[0].id_chat} comme fallback.")
                    chat = all_chats[0]
                else:
                    raise Chat.DoesNotExist("Aucun chat disponible")
            
            chat_name = chat.nom_chat
            logging.info(f"Chat trouvé/utilisé - ID: {chat.id_chat}, Nom: {chat_name}")
            
            # Déterminer le chemin du dossier FAISS
            # 1. Utiliser d'abord le chemin du chat actuel
            faiss_path = get_chat_directory(user_name, chat_name)
            logging.info(f"Utilisation du chemin FAISS (depuis chat): {faiss_path}")
            
            # 2. Si ce chemin n'existe pas, essayer avec le dossier chat_test explicitement
            if not os.path.exists(faiss_path):
                alt_path = os.path.join(settings.MEDIA_ROOT, f"user_{user_name}", "chat_test")
                logging.info(f"Chemin FAISS non trouvé, essai avec chemin alternatif: {alt_path}")
                
                if os.path.exists(alt_path):
                    faiss_path = alt_path
                    logging.info(f"Utilisation du chemin FAISS alternatif: {faiss_path}")
            
            # Générer une réponse
            result = llm.generate_response(question, faiss_path=faiss_path)
            
            # Vérifier le format de la réponse et la traiter en conséquence
            logging.info(f"Type de résultat LLM: {type(result)}")
            
            if isinstance(result, str):
                # Si le résultat est déjà une chaîne de caractères
                response_text = result
                logging.info(f"Réponse LLM (string): {response_text[:100]}...")
            elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                # Format standard des pipelines Hugging Face
                response_text = result[0].get('generated_text', 'Pas de texte généré')
                logging.info(f"Réponse LLM (dict): {response_text[:100]}...")
            else:
                # Autre format, tenter de convertir en string
                response_text = str(result)
                logging.info(f"Réponse LLM (autre format): {response_text[:100]}...")
            
            # Retourner la réponse
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
    print("==============> path",os.path.join(settings.MEDIA_ROOT, f"user_{user_id}", f"chat_{chat_name}"))
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
def load_chat(request):
    try:
        data = json.loads(request.body)
        chat_name = data.get('chat_name')
        user_name = data.get('pseudo')

        user = get_object_or_404(User, pseudo=user_name)
        id_chat = f"user_{user.pseudo}.chat_{chat_name}"
        chat = get_object_or_404(Chat, id_chat=id_chat)


        chat_download_dir = get_chat_directory(user.pseudo, chat_name)
        print(chat_download_dir)
        os.makedirs(chat_download_dir, exist_ok=True)

        file_paths = {}

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