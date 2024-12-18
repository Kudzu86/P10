from rest_framework import serializers
from .models import Issue, Project


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'balise',
            'author', 'assignee', 'project', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'project']

    def validate_status(self, value):
        valid_choices = [choice[0] for choice in Issue.STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Le type doit être l'un des suivants : {', '.join(valid_choices)}."
            )
        return value

    def validate_priority(self, value):
        valid_choices = [choice[0] for choice in Issue.PRIORITY_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Le type doit être l'un des suivants : {', '.join(valid_choices)}."
            )
        return value

    def validate_balise(self, value):
        valid_choices = [choice[0] for choice in Issue.BALISE_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Le type doit être l'un des suivants : {', '.join(valid_choices)}."
            )
        return value

    def validate_assignee(self, value):
        """
        Vérifie que l'assignee est bien un contributeur du projet associé à l'issue.
        """
        # Récupérer l'ID du projet depuis le contexte de la requête
        project_id = self.context['view'].kwargs.get('project_id')

        try:
            project = Project.objects.get(id=project_id, is_deleted=False)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Le projet spécifié n'existe pas.")

        # Vérifie si l'assignee fait partie des contributeurs du projet
        if value and value not in project.contributors.all():
            raise serializers.ValidationError(
                "L'assignee doit être un contributeur du projet."
            )
        return value