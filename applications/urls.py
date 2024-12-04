from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'applications', views.ApplicationViewSet, basename='application')

app_name = 'applications'

urlpatterns = [
    path('', include(router.urls)),  # Inclure toutes les routes du routeur
]