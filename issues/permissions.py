from rest_framework.permissions import BasePermission

class IsContributorOrAuthorForIssue(BasePermission):
    """
    Permission permettant aux contributeurs ou à l'auteur ou à l'assignee de modifier une issue.
    """

    def has_object_permission(self, request, view, obj):
        # L'utilisateur doit être contributeur ou assignee ou auteur de l'issue.
        return (
            request.user in obj.project.contributors.all() or
            obj.author == request.user or
            obj.assignee == request.user
        )
