from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')


app_name = 'users'

urlpatterns = router.urls
