"""
URL configuration for django_auth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin
    path('users/', include(('users.urls', 'users'), namespace='users')),  # Users app
    path('projects/', include(('projects.urls', 'projects'), namespace='projects')),  # Projects app
    path('comments/', include(('comments.urls', 'comments'), namespace='comments')),  # Comments app
    path('issues/', include(('issues.urls', 'issues'), namespace='issues')),  # Issues app
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT Token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT Refresh
]