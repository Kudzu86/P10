from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    # Champ personnalisé pour l'auteur
    author = serializers.SerializerMethodField()

    # Champ personnalisé pour l'issue
    issue = serializers.SerializerMethodField()

    # Champ personnalisé pour le projet
    project = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'uuid', 'content', 'created_at', 'author', 'issue', 'project']
        read_only_fields = ['id', 'author', 'issue', 'project', 'uuid']

    def get_author(self, obj):
        # Retourne l'auteur sous forme de nom d'utilisateur (ou d'autres infos si nécessaire)
        return obj.author.id

    def get_issue(self, obj):
        # Retourne l'ID de l'issue associée
        return obj.issue.id

    def get_project(self, obj):
        # Retourne l'ID du projet associé à l'issue
        return obj.issue.project.id
