# Generated by Django 5.1.4 on 2024-12-18 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='type',
            field=models.CharField(blank=True, choices=[('BACKEND', 'Back-end'), ('FRONTEND', 'Front-end'), ('IOS', 'iOS'), ('ANDROID', 'Android')], error_messages={'invalid_choice': "Le type doit être l'un des suivants : BACKEND, FRONTEND, IOS, ANDROID."}, max_length=10, null=True),
        ),
    ]