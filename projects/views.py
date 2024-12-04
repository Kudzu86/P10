from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer
from .permissions import IsContributorOrReadOnly, IsAuthorOrReadOnly

class ProjectViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer les projets (création, affichage, mise à jour, suppression).
    """
    permission_classes = [IsAuthenticated, IsContributorOrReadOnly]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Récupère uniquement les projets où l'utilisateur est contributeur.
        """
        return Project.objects.filter(contributors__user=self.request.user).distinct()

    def perform_create(self, serializer):
        """
        Crée un projet et ajoute les contributeurs.
        """
        project = serializer.save(author=self.request.user)

        contributors = self.request.data.get('contributors', [])
        if contributors:
            project.contributors.set(contributors)
        else:
            # Si aucun contributeur n'est défini, l'auteur devient le seul contributeur.
            project.contributors.add(self.request.user)

    def perform_update(self, serializer):
        """
        Limite la modification du projet uniquement à l'auteur.
        """
        if self.get_object().author != self.request.user:
            raise PermissionError("Seul l'auteur peut modifier ce projet.")
        serializer.save()
