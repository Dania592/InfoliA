from django.db import models
from api.models import User  # Importer le modèle User depuis l'application api

def get_vectordb_upload_path(instance, filename):
    """
    Génère dynamiquement le chemin de stockage des fichiers
    media/user_<id>/chat_<id>/filename
    TODO : adapter selon l'enregistrement de Ilyes
    """
    return f"user_{instance.id_chat.id_user.pseudo}/chat_{instance.id_chat.id_chat}/{filename}"

class Chat(models.Model):
    nom_chat = models.CharField(max_length=50)
    id_chat = models.CharField(primary_key=True, max_length=100)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)  # Référence directe au modèle importé
    index_faiss = models.FileField(upload_to=get_vectordb_upload_path)
    index_pkl = models.FileField(upload_to=get_vectordb_upload_path)

    def __str__(self):
        return self.nom_chat  # Utiliser nom_chat au lieu de pseudo


class Message(models.Model):
    id_message = models.AutoField(primary_key=True)
    id_chat = models.ForeignKey('Chat', on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    reponse = models.CharField(max_length=510)
    date = models.DateTimeField(auto_now_add=True)
    # La où le Rag a trouver la réponse (page.source)
    source = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id_chat}:{self.id_message}"  # Ajouter une méthode __str__ pour Message
