from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'issues', views.IssueViewSet, basename='issue')

app_name = 'issues'

urlpatterns = router.urls
