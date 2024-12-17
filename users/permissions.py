from rest_framework.permissions import BasePermission

class IsAccountOwner(BasePermission):
    """
    Permet uniquement au propriétaire du compte de le modifier ou de le supprimer.
    """

    def has_object_permission(self, request, view, obj):
        # Autoriser si l'utilisateur est admin ou le propriétaire du compte
        return request.user.is_staff or obj == request.user
