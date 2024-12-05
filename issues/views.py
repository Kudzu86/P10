from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Issue
from .serializers import IssueSerializer
from .permissions import IsContributorOrAuthorForIssue
from projects.models import Project
from django.core.exceptions import PermissionDenied  # Import de l'exception

class IssueViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer les issues (création, affichage, mise à jour, suppression).
    """
    permission_classes = [IsAuthenticated, IsContributorOrAuthorForIssue]
    serializer_class = IssueSerializer

    def get_queryset(self):
        """
        Récupère uniquement les issues actives du projet où l'utilisateur est contributeur.
        """
        project_id = self.kwargs['project_id']
        return Issue.objects.filter(
            project__id=project_id,
            project__contributors__user=self.request.user,
            is_deleted=False  # Filtrer les issues non supprimées
        ).distinct()

    def perform_create(self, serializer):
        """
        Crée une nouvelle issue pour le projet et assigne l'utilisateur comme auteur.
        """
        project_id = self.kwargs['project_id']

        try:
            project = Project.objects.get(id=project_id, is_deleted=False)  # Vérifie que le projet n'est pas supprimé
        except Project.DoesNotExist:
            raise PermissionDenied("Le projet spécifié n'existe pas ou a été supprimé.")

        if self.request.user not in project.contributors.all():
            raise PermissionDenied("Vous devez être contributeur du projet pour créer une issue.")

        serializer.save(author=self.request.user, project=project)  # Lier l'issue au projet
