from rest_framework import serializers
from .models import User, Project, Comment, Issue, Application


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField()  # La date d'inscription est en lecture seule.

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined', 'password', 'consent')
        extra_kwargs = {
            'password': {'write_only': True}  # Le mot de passe est en écriture seule.
        }
        
    def validate_birthdate(self, value):
        """
        Valider que l'utilisateur a au moins 15 ans.
        """
        today = datetime.today().date()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 15:
            raise serializers.ValidationError("Vous devez avoir au moins 15 ans pour vous inscrire.")
        return value

    # Pour hashage du mot de passe à la création d'un utilisateur
    def create(self, validated_data):
        consent = validated_data.get('consent', False)
        if not consent:
            raise serializers.ValidationError("Le consentement RGPD est requis.")
        user = User.objects.create_user(**validated_data)
        return user


class ProjectSerializer(serializers.ModelSerializer):
    contributors = UserSerializer(many=True, read_only=False)  # Permet de définir les contributeurs.
    author = serializers.ReadOnlyField(source='author.id')

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'contributors', 'author']
        read_only_fields = ['author']

    def create(self, validated_data):
        contributors_data = validated_data.pop('contributors', [])
        project = Project.objects.create(**validated_data)

        for contributor_data in contributors_data:
            contributor = User.objects.get(id=contributor_data['id'])
            project.contributors.add(contributor)  # Associer les contributeurs au projet
        return project



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'project', 'content', 'created_at']


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'status', 'priority', 'author', 'project', 'assignee', 'created_at']


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'