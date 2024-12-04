from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.signals import user_logged_in
from rest_framework.response import Response
from .models import Project, Comment, Issue, Application
from .serializers import UserSerializer, ProjectSerializer, CommentSerializer, IssueSerializer, ApplicationSerializer
from .permissions import IsContributorOrReadOnly, IsAuthorOrReadOnly, IsContributor
from datetime import date
from django.shortcuts import render


# Récupère le modèle utilisateur défini dans le projet Django
User = get_user_model()

### --- AUTHENTIFICATION & UTILISATEURS --- ###

# Convertir CreateUserAPIView en ModelViewSet
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
    print("Request META:", request.META)
    print("Request Data:", request.data)
    print(f"Request body: {request.body}")
    try:
        email = request.data['email']
        password = request.data['password']
        
        # Récupérer l'utilisateur par son email
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)  # Recherche l'utilisateur avec l'email
            if user.check_password(password):  # Vérifie le mot de passe de l'utilisateur
                # Vérifier que l'utilisateur a bien donné son consentement RGPD, etc.
                if not user.consent or not user.can_be_contacted or not user.can_data_be_shared:
                    return Response({'erreur': 'L\'utilisateur doit fournir un consentement RGPD valide pour accéder à ce service.'},
                                    status=status.HTTP_403_FORBIDDEN)

                # Générer un token JWT
                refresh = RefreshToken.for_user(user)
                token = str(refresh.access_token)
                
                user_details = {
                    'name': f"{user.first_name} {user.last_name}",
                    'token': token
                }
                # Signaler l'utilisateur connecté
                user_logged_in.send(sender=user.__class__, request=request, user=user)
                return Response(user_details, status=status.HTTP_200_OK)
            else:
                return Response({'erreur': 'Identifiants invalides'}, status=status.HTTP_403_FORBIDDEN)
        
        except user_model.DoesNotExist:
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


### --- PROJETS --- ###

# Convertir ProjectListCreateAPIView en ModelViewSet
class ProjectViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer les projets (création, affichage, mise à jour, suppression).
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(contributors__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        contributors = self.request.data.get('contributors', [])
        if contributors:
            project.contributors.set(contributors)


# Convertir CommentListCreateAPIView en ModelViewSet
class CommentViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer les commentaires associés à un projet.
    """
    permission_classes = [IsContributor]
    serializer_class = CommentSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Comment.objects.filter(project__id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        serializer.save(author=self.request.user, project_id=project_id)


# Convertir IssueListCreateAPIView en ModelViewSet
class IssueViewSet(viewsets.ModelViewSet):
    """
    Permet de gérer les problèmes associés à un projet.
    """
    permission_classes = [IsContributor]
    serializer_class = IssueSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Issue.objects.filter(project__id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        serializer.save(author=self.request.user, project_id=project_id)


### --- UTILISATEURS --- ###

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


class UserProfileView(APIView):
    """
    Permet à l'utilisateur de consulter et de mettre à jour son profil.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'consent': user.consent,
        }
        return Response(user_data, status=status.HTTP_200_OK)

    def put(self, request):
        consent = request.data.get('consent')

        if consent is not None:
            request.user.consent = consent
            request.user.save()

        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')

        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        if email:
            request.user.email = email

        request.user.save()

        return Response({'message': 'Le profil a été mis à jour avec succès.'}, status=status.HTTP_200_OK)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsContributor]  # Ajouter la permission IsContributor

    def get_queryset(self):
        """
        Pour ne récupérer que les applications des projets dont l'utilisateur est contributeur.
        """
        user = self.request.user
        return Application.objects.filter(contributors=user)


def project_detail(request, project_id):
    project = Project.objects.get(id=project_id)
    applications = project.applications.all()  # Récupérer les applications liées à ce projet
    return render(request, 'project_detail.html', {'project': project, 'applications': applications})