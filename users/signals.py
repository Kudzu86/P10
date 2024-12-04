from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import User
from projects.models import Project
from issues.models import Issue
from comments.models import Comment

@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    # Supprime les projets créés par l'utilisateur
    Project.objects.filter(author=instance).delete()
    # Supprime les issues assignées à cet utilisateur
    Issue.objects.filter(author=instance).delete()
    # Supprime les commentaires écrits par cet utilisateur
    Comment.objects.filter(author=instance).delete()
