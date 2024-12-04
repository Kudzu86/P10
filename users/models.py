from django.db import models
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
