from django.db import models
from projects.models import Project  # Importer le modèle Project
from users.models import User  # Importer le modèle User

class Application(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="applications")
    contributors = models.ManyToManyField(User, related_name="applications")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete

    def __str__(self):
        return self.name

    def delete(self):
        """Soft delete de l'application."""
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
