# Generated by Django 5.1.3 on 2024-12-02 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_project_issue_comment_contributor'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='can_be_contacted',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='can_data_be_shared',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='consent',
            field=models.BooleanField(default=False),
        ),
    ]