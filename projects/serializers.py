from rest_framework import serializers
from .models import Project, Contributor
from users.models import User


class ProjectSerializer(serializers.ModelSerializer):
    contributors = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )
    author = serializers.ReadOnlyField(source='author.id')

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'contributors', 'author']
        read_only_fields = ['author']

    def create(self, validated_data):
        contributors_data = validated_data.pop('contributors', [])
        project = Project.objects.create(**validated_data)
        project.contributors.set(contributors_data)  # Associer les contributeurs directement
        return project

    def update(self, instance, validated_data):
        contributors_data = validated_data.pop('contributors', [])
        instance = super().update(instance, validated_data)
        instance.contributors.set(contributors_data)  # Mettre à jour les contributeurs
        return instance