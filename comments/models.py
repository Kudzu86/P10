from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from issues.models import Issue

User = get_user_model()


def validate_comment_length(value):
    if len(value) < 10:
        raise ValidationError("Le commentaire doit contenir au moins 10 caractères.")


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(validators=[validate_comment_length])
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete

    def __str__(self):
        return f"Comment by {self.author} on {self.issue.title}"

    def delete(self):
        """Soft delete du commentaire."""
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
