from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import EmailValidator


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """ 
        Crée et sauvegarde un utilisateur avec l'email et le mot de passe donnés. 
        """
        if not email:
            raise ValueError("L'e-mail donné doit être défini")

        email = self.normalize_email(email)
        try:
            with transaction.atomic():
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except Exception as e:
            raise ValueError(f"Une erreur est survenue lors de la création de l'utilisateur : {e}")

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """ 
    Modèle d'utilisateur personnalisé basé sur l'email. 
    """
    email = models.EmailField(max_length=40, unique=True, validators=[EmailValidator()])
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    birthdate = models.DateField(null=True, blank=True)  # Correction du champ blank=False, trop restrictif
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Champs RGPD
    can_be_contacted = models.BooleanField(default=False)  # Consentement pour être contacté
    can_data_be_shared = models.BooleanField(default=False)  # Consentement pour partager les données

    is_deleted = models.BooleanField(default=False)  # Soft delete

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def delete(self):
        """Soft delete de l'utilisateur."""
        self.is_deleted = True
        self.is_active = False  # Désactivation de l'utilisateur lors de la suppression
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({'Actif' if self.is_active else 'Supprimé'})"
