from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profile', views.UserProfileViewSet, basename='user_profile')

app_name = 'users'

urlpatterns = router.urls
