from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Issue
from .serializers import IssueSerializer
from .permissions import IsContributorOrAuthorForIssue


class IssueViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer les issues (création, affichage, mise à jour, suppression).
    """
    permission_classes = [IsAuthenticated, IsContributorOrAuthorForIssue]
    serializer_class = IssueSerializer

    def get_queryset(self):
        """
        Récupère uniquement les issues du projet où l'utilisateur est contributeur.
        """
        project_id = self.kwargs['project_id']
        return Issue.objects.filter(
            project__id=project_id,
            project__contributors__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        """
        Crée une nouvelle issue pour le projet et assigne l'utilisateur comme auteur.
        """
        project_id = self.kwargs['project_id']
        project = serializer.validated_data['project']

        if self.request.user not in project.contributors.all():
            raise PermissionError("Vous devez être contributeur du projet pour créer une issue.")

        serializer.save(author=self.request.user, project_id=project_id)
