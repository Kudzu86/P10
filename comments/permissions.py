from rest_framework.permissions import BasePermission

class IsAuthorOrReadOnlyForComment(BasePermission):
    """
    Permet à l'auteur d'un commentaire de le modifier ou de le supprimer,
    tout en permettant à tout utilisateur ayant les droits de lecture de consulter le commentaire.
    """
    def has_object_permission(self, request, view, obj):
        # Si l'opération est une lecture, on autorise tout le monde (GET, HEAD).
        if request.method in ['GET', 'HEAD']:
            return True

        # Si l'opération est d'écrire/modifier/supprimer, seul l'auteur est autorisé.
        return obj.author == request.user
