from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Comment
from .serializers import CommentSerializer
from issues.models import Issue
from django.core.exceptions import PermissionDenied
from .permissions import IsAuthorOrReadOnlyForComment
from rest_framework.response import Response


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnlyForComment]
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        Récupère les commentaires liés à une issue spécifique, en filtrant ceux qui sont actifs (is_deleted=False).
        Les administrateurs peuvent voir tous les commentaires.
        """
        issue_id = self.kwargs['issue_id']
        # Vérification pour les administrateurs
        if self.request.user.is_superuser:
            return Comment.objects.filter(issue__id=issue_id, is_deleted=False).order_by('id')
        
        # Vérification pour les contributeurs ou les assignés du projet lié à l'issue
        issue = Issue.objects.filter(id=issue_id, is_deleted=False).first()
        if issue:
            if self.request.user not in issue.project.contributors.all() and not self.request.user.is_superuser:
                raise PermissionDenied("Vous n'êtes pas autorisé à accéder aux commentaires de ce projet.")
            return Comment.objects.filter(
                issue__id=issue_id,
                is_deleted=False,
                issue__project__contributors__in=[self.request.user]
            ).distinct().order_by('id')
        
        # Si l'issue n'existe pas ou a été supprimée, renvoie une permission refusée
        raise PermissionDenied("L'issue spécifiée n'existe pas ou a été supprimée.")

    def perform_create(self, serializer):
        """
        Crée un nouveau commentaire pour une issue spécifique.
        """
        issue_id = self.kwargs['issue_id']
        if self.request.user.is_superuser:
            issue = Issue.objects.get(id=issue_id, is_deleted=False)
        else:
            try:
                issue = Issue.objects.get(id=issue_id, is_deleted=False)
            except Issue.DoesNotExist:
                raise PermissionDenied("L'issue spécifiée n'existe pas ou a été supprimée.")

            if self.request.user not in issue.project.contributors.all():
                raise PermissionDenied("Vous devez être contributeur du projet pour créer un commentaire.")

        serializer.save(author=self.request.user, issue=issue)

    def update(self, request, *args, **kwargs):
        """
        Met à jour un commentaire, uniquement si l'utilisateur est l'auteur ou un administrateur.
        """
        comment = self.get_object()
        if comment.author != request.user and not request.user.is_superuser:
            raise PermissionDenied("Seul l'auteur ou un administrateur peut modifier ce commentaire.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Supprime un commentaire, uniquement si l'utilisateur est l'auteur ou un administrateur.
        """
        comment = self.get_object()
        if comment.author != request.user and not request.user.is_superuser:
            return Response({'erreur': "Seul l'auteur ou un administrateur peut supprimer ce commentaire."}, status=403)
        comment.is_deleted = True  # Marque le commentaire comme supprimé
        comment.save()
        return Response({'message': "Le commentaire a été supprimé."}, status=204)
