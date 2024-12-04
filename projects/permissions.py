from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsContributorOrAuthor(BasePermission):
    """
    Permission permettant aux contributeurs ou à l'auteur du projet d'accéder/modifier.
    """

    def has_object_permission(self, request, view, obj):
        return request.user in obj.contributors.all() or obj.author == request.user


class IsContributorOrReadOnly(BasePermission):
    """
    Permet uniquement aux contributeurs ou à l'auteur d'accéder/modifier le projet.
    Les autres utilisateurs ont uniquement un accès en lecture.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return obj.author == request.user or obj.contributors.filter(id=request.user.id).exists()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permet à l'auteur d'une ressource de la modifier ou de la supprimer.
    Les autres utilisateurs peuvent uniquement lire.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return obj.author == request.user


class IsContributor(permissions.BasePermission):
    """
    Vérifie si l'utilisateur est contributeur du projet associé à la ressource.
    """

    def has_object_permission(self, request, view, obj):
        return request.user in obj.contributors.all()
