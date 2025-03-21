# Generated by Django 5.1.6 on 2025-03-02 19:55

import chat.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_vectordb_id_chat_alter_chat_id_vector'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='id_vector',
        ),
        migrations.AddField(
            model_name='chat',
            name='index_faiss',
            field=models.FileField(blank=True, null=True, upload_to=chat.models.get_vectordb_upload_path),
        ),
        migrations.AddField(
            model_name='chat',
            name='index_pkl',
            field=models.FileField(blank=True, null=True, upload_to=chat.models.get_vectordb_upload_path),
        ),
        migrations.AlterField(
            model_name='chat',
            name='id_chat',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
        migrations.DeleteModel(
            name='Vectordb',
        ),
    ]
