from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Project
from users.models import User

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
