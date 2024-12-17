from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import IssueViewSet

router = DefaultRouter()
router.register(r'projects/(?P<project_id>\d+)/issues', IssueViewSet, basename='issue')

app_name = 'issues'

urlpatterns = [
    path('', include(router.urls)),
]
