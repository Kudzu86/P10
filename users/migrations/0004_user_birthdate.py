# Generated by Django 5.1.3 on 2024-12-03 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_can_be_contacted_user_can_data_be_shared_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='birthdate',
            field=models.DateField(null=True),
        ),
    ]
