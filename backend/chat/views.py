from django.shortcuts import render
from core.model.rag_module import RagModule
from core.model.llm_module import LlmModule
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import VectordbSerializer
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

        faiss_path = 'core/model/' + chat_name #TODO : adapter selon le user et le chat

        result = llm.generate_response(question, faiss_path=faiss_path)

        logging.info(f"Chat: {chat_name}, Utilisateur: {user_name}, Question: {question}, Result: {result}")

        return Response({
                "message": "Connexion réussie !",
                "response": result[0]['generated_text']
            }, status=status.HTTP_200_OK)
    return Response("serializer.errors", status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_chat(request):
    data = json.loads(request.body)
    chat_name = data.get('chat_name')
    user_name = data.get('pseudo')
    pdf_path = "core/model/docs/" + data.get('pdf_name')

    faiss_path = 'core/model/' + chat_name  # TODO : adapter selon le user et le chat

    faiss = rag.create_faiss_db([pdf_path], faiss_path)

#    serializer = VectordbSerializer(data=request.data)

#    if serializer.is_valid():
#        serializer.save()
#        return Response(serializer.data, status=status.HTTP_201_CREATED)
 #   return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        "message": "Création réussie !",
    }, status=status.HTTP_200_OK)