from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsContributorOrAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Vérifiez si l'utilisateur est contributeur ou auteur du projet
        return request.user in obj.contributors.all() or obj.author == request.user


class IsContributorOrAuthorForIssue(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Vérifiez les permissions sur le projet lié à ce problème
        return request.user in obj.project.contributors.all() or obj.project.author == request.user



class IsContributorOrReadOnly(BasePermission):
    """
    Permet uniquement aux contributeurs ou à l'auteur d'accéder/modifier le projet.
    Les autres utilisateurs n'ont qu'un accès en lecture.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # L'utilisateur est l'auteur du projet ou est contributeur
        return obj.author == request.user or obj.contributors.filter(user=request.user).exists()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permet à l'auteur d'une ressource de la modifier ou de la supprimer.
    Les autres utilisateurs peuvent uniquement la lire.
    """

    def has_object_permission(self, request, view, obj):
        # Les permissions sont uniquement en lecture pour les requêtes GET, HEAD ou OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        # Seul l'auteur de la ressource peut la modifier ou la supprimer
        return obj.author == request.user


class IsContributor(permissions.BasePermission):
    """
    Vérifie si l'utilisateur est contributeur du projet associé à la ressource.
    """

    def has_object_permission(self, request, view, obj):
        # Vérifie si l'utilisateur est contributeur du projet associé à la ressource
        return request.user in obj.project.contributors.all()
