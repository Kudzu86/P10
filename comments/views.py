from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Comment
from .serializers import CommentSerializer
from projects.permissions import IsContributor

class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsContributor]
    serializer_class = CommentSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Comment.objects.filter(project__id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        serializer.save(author=self.request.user, project_id=project_id)


