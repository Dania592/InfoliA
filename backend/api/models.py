from django.db import models
from django.contrib.auth.hashers import make_password

class User(models.Model):
    pseudo = models.CharField(max_length=50, primary_key=True, unique=True)
    password = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Vérifie si le mot de passe est déjà hashé
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.pseudo
