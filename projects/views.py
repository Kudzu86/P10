from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer
from .permissions import IsContributorOrReadOnly, IsAuthorOrReadOnly, IsAuthorOrContributorReadOnly 
from users.models import User
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied

class ProjectViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer les projets (création, affichage, mise à jour, suppression).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Récupère uniquement les projets où l'utilisateur est contributeur et non supprimés.
        """
        return Project.objects.filter(contributor__user=self.request.user, is_deleted=False).distinct()

def perform_create(self, serializer):
    """
    Crée un projet et ajoute l'auteur et les contributeurs (avec vérification).
    """
    print("Création du projet en cours...")

    # Créer le projet en affectant directement l'auteur
    project = serializer.save(author=self.request.user)  # L'auteur est assigné directement ici

    # Vérifier si l'utilisateur est dans la liste des contributeurs, sinon l'ajouter
    contributors_data = self.request.data.get('contributors', [])
    
    if self.request.user.id not in contributors_data:
        contributors_data.append(self.request.user.id)  # S'assurer que l'auteur est un contributeur aussi
    
    contributors = []
    for contributor_id in contributors_data:
        try:
            contributor = User.objects.get(id=contributor_id)
            contributors.append(contributor)
        except User.DoesNotExist:
            continue  # Ignore si l'utilisateur n'existe pas
    
    # Associer les contributeurs au projet
    project.contributors.set(contributors)
    
    # Sauvegarder le projet après avoir mis à jour les contributeurs
    project.save()  # Sauvegarde après mise à jour des contributeurs

    print(f"Projet créé avec succès, auteur : {project.author.id}, contributeurs : {[contributor.id for contributor in contributors]}")


    def perform_update(self, serializer):
        """
        Limite la modification du projet uniquement à l'auteur.
        """
        project = self.get_object()
        if project.author != self.request.user or project.is_deleted:
            raise PermissionDenied("Seul l'auteur peut modifier ce projet ou ce projet a été supprimé.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Effectue une suppression logique du projet (soft delete) si l'utilisateur est l'auteur.
        """
        project = self.get_object()
        if project.author != request.user:
            return Response({'error': "Seul l'auteur peut supprimer ce projet."}, status=403)
        project.is_deleted = True  # Marque le projet comme supprimé
        project.save()
        return Response({'message': "Le projet a été supprimé."}, status=204)  # Retourne une réponse avec code 204 (pas de contenu après suppression)
