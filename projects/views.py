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
        Retourne tous les projets non supprimés, avec des permissions appliquées selon l'utilisateur.
        """
        user = self.request.user

        # Si l'utilisateur est un super utilisateur, il peut voir tous les projets
        if user.is_superuser:
            return Project.objects.filter(is_deleted=False).distinct().order_by('id')

        # Sinon, on filtre les projets auxquels l'utilisateur est contributeur
        return Project.objects.filter(
            is_deleted=False,
            contributors__in=[user],
            contributors__is_active=True,
            contributors__is_deleted=False
        ).distinct().order_by('id')

    def check_object_permissions(self, request, project):
        user = request.user
        if not user.is_superuser:
            is_contributor = project.contributors.filter(
                id=user.id,
                is_active=True,
                is_deleted=False
            ).exists()
            if not is_contributor:
                raise PermissionDenied("Vous n'avez pas les droits pour accéder à ce projet.")

    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()
        self.check_object_permissions(request, project)
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        contributors_data = self.request.data.get('contributors', [])
        
        # Filtrer les contributeurs valides
        valid_contributors = User.objects.filter(
            id__in=contributors_data,
            is_active=True,
            is_deleted=False
        )
        
        if valid_contributors.exists():
            project.contributors.set(valid_contributors)
        
        # Toujours ajouter l'auteur comme contributeur
        project.contributors.add(self.request.user)

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        self.check_object_permissions(request, project)
        
        if project.author != request.user and not request.user.is_superuser:
            raise PermissionDenied("Seul l'auteur ou un administrateur peut modifier ce projet.")

        # Vérifier les nouveaux contributeurs
        if 'contributors' in request.data:
            contributors_data = request.data.get('contributors', [])
            invalid_contributors = User.objects.filter(
                id__in=contributors_data,
                is_active=False
            ).values('id', 'email')
            
            if invalid_contributors:
                invalid_users = [f"{user['email']} (ID: {user['id']})" for user in invalid_contributors]
                return Response({
                    'erreur': f"Les utilisateurs suivants ne sont pas actifs : {', '.join(invalid_users)}"
                }, status=400)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        self.check_object_permissions(request, project)
        if project.author != request.user and not request.user.is_superuser:
            return Response({'erreur': "Seul l'auteur ou un administrateur peut supprimer ce projet."}, status=403)
        project.is_deleted = True  # Marque le projet comme supprimé
        project.save()
        return Response({'message': "Le projet a été supprimé."}, status=204)
