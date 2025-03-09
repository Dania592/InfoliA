from django.db import models
from api.models import User  # Importer le modèle User depuis l'application api

def get_vectordb_upload_path(instance, filename):
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

from django.db import models

def get_file_upload_path(instance, filename):
    """Génère un chemin valide pour l'upload de fichiers"""
    # Nettoyer le nom du chat pour éviter les caractères problématiques
    safe_chat_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in instance.chat_name)
    # Assurer que les répertoires existent
    import os
    from django.conf import settings
    directory = os.path.join(settings.MEDIA_ROOT, f"user_{instance.user_name}", f"chat_{safe_chat_name}")
    os.makedirs(directory, exist_ok=True)
    
    return f"user_{instance.user_name}/chat_{safe_chat_name}/{filename}"

class UploadedFile(models.Model):
    chat_name = models.CharField(max_length=100, null=True, blank=True)
    user_name = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to=get_file_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)