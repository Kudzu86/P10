from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()  # Permet de récupérer le modèle User dynamique

class Issue(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed')
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    BALISE_CHOICES = [
        ('bug', 'Bug'),
        ('feature', 'Feature'),
        ('task', 'Task')
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, default='open')
    priority = models.CharField(max_length=10, default='medium')
    balise = models.CharField(max_length=10, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_issues')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issues")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    

    def __str__(self):
        return f"{self.title} - {self.status}"

    def delete(self):
        """Soft delete de l'issue."""
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
