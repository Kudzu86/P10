from rest_framework.permissions import BasePermission

class IsContributorOrAuthorForIssue(BasePermission):
    """
    Permission permettant aux contributeurs ou à l'auteur du projet lié à l'issue de la modifier.
    """

    def has_object_permission(self, request, view, obj):
        # L'utilisateur doit être contributeur du projet ou auteur de l'issue.
        return request.user in obj.project.contributors.all() or obj.project.author == request.user
