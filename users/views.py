from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from users.serializers import UserSerializer
from rest_framework.views import APIView


User = get_user_model()

# Vue pour la création des utilisateurs
class UserViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer la création et la récupération des utilisateurs.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [AllowAny()]  # Autorisé à tout le monde pour l'inscription
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]  # Seuls les utilisateurs authentifiés peuvent accéder/modifier
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        user_data = request.data
        consent = user_data.get('consent', False)
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

        # Vérification du consentement RGPD
        if not consent:
            return Response(
                {'erreur': 'Le consentement RGPD est requis pour créer un compte.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=user_data)

        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            if not user.consent:
                return Response({'erreur': 'Le consentement RGPD est requis pour accéder à ce service.'},
                                status=status.HTTP_403_FORBIDDEN)
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
        user.delete()
        return Response({"message": "Votre compte et toutes les données associées ont été supprimés."},
                        status=status.HTTP_200_OK)


class ContactUserView(APIView):
    """
    Permet à l'utilisateur de donner ou de modifier son consentement RGPD.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        consent = request.data.get('consent')

        if consent is None:
            return Response({'erreur': 'Le consentement est requis pour continuer.'}, status=status.HTTP_400_BAD_REQUEST)

        if consent not in ['can_be_contacted', 'can_data_be_shared']:
            return Response({"erreur": "Les consentements doivent être valides (can_be_contacted ou can_data_be_shared)."}, status=status.HTTP_400_BAD_REQUEST)

        if consent == 'can_be_contacted':
            request.user.can_be_contacted = request.data.get('value', False)
        elif consent == 'can_data_be_shared':
            request.user.can_data_be_shared = request.data.get('value', False)

        request.user.save()

        return Response({'message': 'Le consentement a été mis à jour avec succès.'}, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Affiche les informations du profil de l'utilisateur connecté.
        """
        user = request.user
        user_data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'consent': user.consent,
        }
        return Response(user_data)

    def update(self, request):
        """
        Met à jour les informations du profil de l'utilisateur connecté.
        """
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()
        return Response({'message': 'Le profil a été mis à jour avec succès.'})