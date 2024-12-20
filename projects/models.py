from django.db import models
from users.models import User  # Importer le modèle User

class Project(models.Model):
    TYPE_CHOICES = [
        ('backend', 'Back-end'),
        ('frontend', 'Front-end'),
        ('ios', 'iOS'),
        ('android', 'Android'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    contributors = models.ManyToManyField(User, related_name="projects")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_projects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    type = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.title

    def delete(self):
        """Soft delete du projet."""
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Contributor(models.Model):
    ROLE_CHOICES = [
        ('AUTHOR', 'Author'),
        ('CONTRIBUTOR', 'Contributor'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='CONTRIBUTOR')
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete 
    

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user.email} - {self.project.title} ({self.role})"

    def delete(self):
        """Soft delete du contributeur."""
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
