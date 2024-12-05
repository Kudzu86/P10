from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Comment
from .serializers import CommentSerializer
from issues.models import Issue
from django.core.exceptions import PermissionDenied  # Import pour lever une exception personnalisée

class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        Récupère les commentaires liés à une issue spécifique, en filtrant ceux qui sont actifs (is_deleted=False).
        """
        issue_id = self.kwargs['issue_id']
        return Comment.objects.filter(
            issue__id=issue_id,
            issue__project__contributors__user=self.request.user,
            is_deleted=False  # Ne retourne que les commentaires non supprimés
        ).distinct()

    def perform_create(self, serializer):
        """
        Crée un nouveau commentaire pour une issue spécifique.
        """
        issue_id = self.kwargs['issue_id']
        try:
            issue = Issue.objects.get(id=issue_id, is_deleted=False)  # Vérifie que l'issue n'est pas supprimée
        except Issue.DoesNotExist:
            raise PermissionDenied("L'issue spécifiée n'existe pas ou a été supprimée.")

        if self.request.user not in issue.project.contributors.all():
            raise PermissionDenied("Vous devez être contributeur du projet pour créer un commentaire.")

        serializer.save(author=self.request.user, issue=issue)
