# Generated by Django 5.1.6 on 2025-03-02 15:07

import chat.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vectordb',
            name='id_chat',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vectordb', to='chat.chat'),
        ),
        migrations.AlterField(
            model_name='vectordb',
            name='index_faiss',
            field=models.FileField(upload_to=chat.models.get_vectordb_upload_path),
        ),
        migrations.AlterField(
            model_name='vectordb',
            name='index_pkl',
            field=models.FileField(upload_to=chat.models.get_vectordb_upload_path),
        ),
    ]
