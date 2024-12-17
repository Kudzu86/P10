from rest_framework import serializers
from .models import Issue


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'author', 'assignee', 'project', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'project']
