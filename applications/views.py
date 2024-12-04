from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Application
from .serializers import ApplicationSerializer
from projects.permissions import IsContributor

class ApplicationViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer les applications liées aux projets.
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsContributor]  # Ajouter la permission IsContributor

    def get_queryset(self):
        """
        Pour ne récupérer que les applications des projets dont l'utilisateur est contributeur.
        """
        user = self.request.user
        return Application.objects.filter(contributors=user)
