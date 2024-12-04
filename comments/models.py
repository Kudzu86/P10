from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project


User = get_user_model()


def validate_comment_length(value):
    if len(value) < 10:
        raise ValidationError("Le commentaire doit contenir au moins 10 caractères.")


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(validators=[validate_comment_length])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.project}"