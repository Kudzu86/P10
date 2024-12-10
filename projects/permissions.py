from rest_framework.permissions import BasePermission
from rest_framework import permissions
from .models import Contributor


class IsAuthorOrContributorReadOnly(permissions.BasePermission):
    """
    L'auteur du projet a tous les droits.
    Les contributeurs ont un accès en lecture seule.
    """

    def has_object_permission(self, request, view, obj):
        # Autoriser l'accès en lecture pour tout contributeur
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True

        # Seul l'auteur peut modifier ou supprimer le projet
        return obj.author == request.user


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

    def has_permission(self, request, view):
        # Autorise les utilisateurs authentifiés à créer un projet
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        # Lecture seule autorisée pour tout le monde
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        # Modification autorisée pour l'auteur ou les contributeurs
        return request.user == obj.author or request.user in obj.contributors.all()



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
