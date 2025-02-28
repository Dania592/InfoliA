from django.db import models
from api.models import User  # Importer le modèle User depuis l'application api


class Chat(models.Model):
    nom_chat = models.CharField(max_length=50)
    id_chat = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)  # Référence directe au modèle importé
    id_vector = models.ForeignKey('Vectordb', on_delete=models.CASCADE)

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
        return f"{self.question[:30]}..."  # Ajouter une méthode __str__ pour Message


class Vectordb(models.Model):
    id_vector = models.AutoField(primary_key=True)
    index_faiss = models.FileField()  # Todo : voir ou stocker les vecteurs
    index_pkl = models.FileField()  # Todo : voir ou stocker les indexes

    def __str__(self):
        return f"Vector {self.id_vector}"  # Ajouter une méthode __str__ appropriée