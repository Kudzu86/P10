from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Issue
from .serializers import IssueSerializer
from .permissions import IsContributorOrAuthorForIssue
from projects.models import Project
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response


class IssueViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer les issues (création, affichage, mise à jour, suppression).
    """
    permission_classes = [IsAuthenticated, IsContributorOrAuthorForIssue]
    serializer_class = IssueSerializer

    def get_queryset(self):
        """
        Récupère uniquement les issues actives du projet où l'utilisateur est contributeur ou assigné.
        Les administrateurs peuvent voir toutes les issues.
        Si l'utilisateur n'a pas les droits d'accès, une PermissionDenied sera levée (403).
        """
        project_id = self.kwargs['project_id']
        project = Project.objects.get(id=project_id, is_deleted=False)  # On récupère le projet

        # Vérifie si l'utilisateur est un contributeur, assigné ou administrateur
        if not self.request.user.is_superuser and not (self.request.user in project.contributors.all()):
            # Si l'utilisateur n'est pas contributeur ou assigné, lève une erreur 403
            raise PermissionDenied("Vous n'avez pas les droits pour accéder à ce projet ou à ses issues.")

        # Si l'utilisateur est un administrateur, il peut voir toutes les issues
        if self.request.user.is_superuser:
            return Issue.objects.filter(project__id=project_id, is_deleted=False).order_by('id')

        # L'utilisateur est contributeur ou assigné au projet, on filtre donc les issues liées à ce projet
        return Issue.objects.filter(
            project__id=project_id,
            is_deleted=False,
            project__contributors__in=[self.request.user]
        ).distinct().order_by('id')

    def perform_create(self, serializer):
        """
        Crée une nouvelle issue pour le projet et assigne l'utilisateur comme auteur.
        """
        project_id = self.kwargs['project_id']
        if self.request.user.is_superuser:
            project = Project.objects.get(id=project_id, is_deleted=False)
        else:
            try:
                project = Project.objects.get(id=project_id, is_deleted=False)
            except Project.DoesNotExist:
                raise PermissionDenied("Le projet spécifié n'existe pas ou a été supprimé.")

            if self.request.user not in project.contributors.all():
                raise PermissionDenied("Vous devez être contributeur du projet pour créer une issue.")

        serializer.save(author=self.request.user, project=project)

    def update(self, request, *args, **kwargs):
        """
        Met à jour une issue, uniquement si l'utilisateur est l'auteur ou un administrateur.
        """
        issue = self.get_object()
        if issue.author != request.user and not request.user.is_superuser:
            raise PermissionDenied("Seul l'auteur ou un administrateur peut modifier cette issue.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Supprime une issue, uniquement si l'utilisateur est l'auteur ou un administrateur.
        """
        issue = self.get_object()
        if issue.author != request.user and not request.user.is_superuser:
            return Response({'erreur': "Seul l'auteur ou un administrateur peut supprimer cette issue."}, status=403)
        issue.is_deleted = True  # Marque l'issue comme supprimée
        issue.save()
        return Response({'message': "L'issue a été supprimée."}, status=204)
