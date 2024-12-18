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
        fields = ['id', 'title', 'description', 'type', 'created_at', 'updated_at', 'contributors', 'author']
        read_only_fields = ['author']

    def validate_type(self, value):
        valid_choices = [choice[0] for choice in Project.TYPE_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Le type doit être l'un des suivants : {', '.join(valid_choices)}."
            )
        return value

    def create(self, validated_data):
        contributors_data = validated_data.pop('contributors', [])
        project = Project.objects.create(**validated_data)
        project.contributors.set(contributors_data)  # Associer les contributeurs directement
        return project

    def update(self, instance, validated_data):
        contributors_data = validated_data.pop('contributors', None)
        instance = super().update(instance, validated_data)
        if contributors_data is not None:
            instance.contributors.set(contributors_data)  # Mettre à jour les contributeurs
        if instance.author: 
            instance.contributors.add(instance.author)
        return instance