from rest_framework.permissions import BasePermission

class IsContributorOrAuthorForIssue(BasePermission):
    """
    Permission permettant aux contributeurs, à l'auteur ou à l'assigné de modifier ou voir une issue.
    """

    def has_object_permission(self, request, view, obj):
        # Autoriser la lecture uniquement pour les administrateurs, contributeurs ou assignés.
        if request.method == 'GET':
            return (
                request.user.is_superuser or
                request.user in obj.project.contributors.all() or
                obj.assignee == request.user
            )
        
        # Si l'utilisateur veut modifier ou supprimer, on vérifie qu'il est l'auteur ou admin.
        return (
            obj.author == request.user or  # L'auteur peut modifier ou supprimer
            request.user.is_superuser      # Un admin peut aussi
        )
