# Generated by Django 5.1.4 on 2024-12-18 14:55

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_comment_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
