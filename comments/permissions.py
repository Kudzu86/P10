from rest_framework.permissions import BasePermission

class IsAuthorOrReadOnlyForComment(BasePermission):
    """
    Permet à l'auteur d'un commentaire ou à un administrateur de le modifier ou de le supprimer,
    tout en permettant à tout utilisateur ayant les droits de lecture de consulter le commentaire.
    """
    def has_object_permission(self, request, view, obj):
        # Autoriser la lecture uniquement pour les administrateurs, contributeurs ou assignés
        if request.method == 'GET':
            return (
                request.user.is_superuser or
                request.user in obj.issue.project.contributors.all() or
                obj.issue.assignee == request.user
            )

        # Si l'utilisateur veut modifier ou supprimer le commentaire, on vérifie qu'il est l'auteur ou admin.
        return obj.author == request.user or request.user.is_superuser
