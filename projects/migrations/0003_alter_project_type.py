# Generated by Django 5.1.4 on 2024-12-18 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_project_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='type',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
