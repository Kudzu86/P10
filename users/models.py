from __future__ import unicode_literals
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.db import transaction
from django.core.validators import EmailValidator


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """ 
        Crée et sauvegarde un utilisateur avec l'email et le mot de passe donnés. 
        """
        if not email:
            raise ValueError("L'e-mail donné doit être défini")
        try:
            with transaction.atomic():
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except:
            raise

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """ 
    Modèle d'utilisateur personnalisé basé sur l'email. 
    """
    email = models.EmailField(max_length=40, unique=True, validators=[EmailValidator()])
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    consent = models.BooleanField(default=False)  # Champ pour enregistrer le consentement RGPD
    birthdate = models.DateField(null=True, blank=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Champs RGPD
    can_be_contacted = models.BooleanField(default=True)  # Consentement pour être contacté
    can_data_be_shared = models.BooleanField(default=False)  # Consentement pour partager les données

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    contributors = models.ManyToManyField(User, related_name="contributed_projects")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_projects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contributor(models.Model):
    """
    Modèle de table intermédiaire pour gérer les contributeurs d'un projet.
    """
    ROLE_CHOICES = [
        ('AUTHOR', 'Author'),
        ('CONTRIBUTOR', 'Contributor'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='CONTRIBUTOR')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user.email} - {self.project.title} ({self.role})"


class Issue(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')])
    priority = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issues")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def validate_comment_length(value):
    if len(value) < 10:
        raise ValidationError("Le commentaire doit contenir au moins 10 caractères.")


class Comment(models.Model):
    content = models.TextField(validators=[validate_comment_length])
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.project}"


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    # Supprime les projets créés par l'utilisateur
    Project.objects.filter(author=instance).delete()
    # Supprime les issues assignées à cet utilisateur
    Issue.objects.filter(author=instance).delete()
    # Supprime les commentaires écrits par cet utilisateur
    Comment.objects.filter(author=instance).delete()


class Application(models.Model):
    name = models.CharField(max_length=255)  # Le nom de l'application
    description = models.TextField()         # La description de l'application
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="applications")  # Lien avec un projet
    contributors = models.ManyToManyField(User, related_name="applications")  # Les utilisateurs associés à l'application
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
