from rest_framework.permissions import BasePermission

class IsAccountOwner(BasePermission):
    """
    Permet uniquement au propriétaire du compte de le modifier ou de le supprimer.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user
