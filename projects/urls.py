from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')

app_name = 'projects'

urlpatterns = router.urls
