from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    ProjectViewSet,
    CommentViewSet,
    IssueViewSet,
    authenticate_user,
    ApplicationViewSet,
    UserRetrieveUpdateViewSet,
    UserDeleteView,
    ContactUserView,
    UserProfileView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'applications', ApplicationViewSet, basename='application')

app_name = 'users'

urlpatterns = [
    path('obtain_token/', authenticate_user, name='obtain_token'),
    path('profile/', UserRetrieveUpdateViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='profile'),
    path('profile/delete/', UserDeleteView.as_view(), name='delete_user'),
    path('profile/consent/', ContactUserView.as_view(), name='update_consent'),
    path('profile/view/', UserProfileView.as_view(), name='view_profile'),
    path('', include(router.urls)),
]
