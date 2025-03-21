# Generated by Django 5.1.3 on 2025-03-04 22:29

import chat.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_alter_chat_index_faiss_alter_chat_index_pkl'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_name', models.CharField(blank=True, max_length=100, null=True)),
                ('user_name', models.CharField(blank=True, max_length=100, null=True)),
                ('file', models.FileField(upload_to=chat.models.get_file_upload_path)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
