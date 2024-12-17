from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from users.serializers import UserSerializer
from users.permissions import IsAccountOwner
from rest_framework.views import APIView
from datetime import date


User = get_user_model()

# Vue pour la création des utilisateurs
class UserViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer la création et la récupération des utilisateurs.
    """
    queryset = User.objects.filter(is_deleted=False).order_by('id')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.user.is_superuser:
            return []  # Les admins ont tous les droits, donc on ne met aucune restriction
        elif self.action == 'create':
            return [AllowAny()]  # Tout le monde peut créer un utilisateur
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]  # Les utilisateurs authentifiés peuvent accéder à la liste ou au profil
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAccountOwner()]  # Seulement le propriétaire ou l'admin peuvent modifier ou supprimer
        return super().get_permissions()  # Retourne les permissions par défaut dans d'autres cas

    def create(self, request, *args, **kwargs):
        user_data = request.data
        birthdate = user_data.get('birthdate')

        # Vérification de la validité et de l'âge minimum (15 ans)
        if birthdate:
            try:
                birthdate_obj = date.fromisoformat(birthdate)
                today = date.today()
                age = today.year - birthdate_obj.year - (
                    (today.month, today.day) < (birthdate_obj.month, birthdate_obj.day)
                )
                if age < 15:
                    return Response(
                        {'erreur': "L'inscription est interdite aux utilisateurs de moins de 15 ans."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'erreur': "La date de naissance n'est pas valide. Format attendu : AAAA-MM-JJ."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'erreur': "La date de naissance est requise."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

# Vue de connexion (authentification) d'un utilisateur
@api_view(['POST'])
@permission_classes([AllowAny])
def authenticate_user(request):
    """
    Authentifie l'utilisateur et retourne un token JWT.
    """
    try:
        email = request.data['email']
        password = request.data['password']
        
        # Récupérer l'utilisateur par son email
        user = User.objects.get(email=email)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            user_details = {
                'name': f"{user.first_name} {user.last_name}",
                'token': token
            }
            user_logged_in.send(sender=user.__class__, request=request, user=user)
            return Response(user_details, status=status.HTTP_200_OK)
        return Response({'erreur': 'Identifiants invalides'}, status=status.HTTP_403_FORBIDDEN)

    except KeyError:
        return Response({'erreur': 'Veuillez fournir un e-mail et un mot de passe'}, status=status.HTTP_400_BAD_REQUEST)

# Vue pour récupérer et mettre à jour les informations d'un utilisateur
class UserRetrieveUpdateViewSet(viewsets.ModelViewSet):
    """
    Permet de récupérer ou mettre à jour les informations d'un utilisateur.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class UserDeleteView(APIView):
    """
    Permet de supprimer l'utilisateur connecté et toutes les données associées.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user

        # Demander une confirmation avant de supprimer l'utilisateur
        confirm_delete = request.data.get('confirm_delete', False)
        if not confirm_delete:
            return Response({"message": "Vous devez confirmer la suppression de votre compte."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({"message": "Votre compte et toutes les données associées ont été supprimés."},
                        status=status.HTTP_200_OK)

