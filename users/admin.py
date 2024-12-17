from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    def delete_model(self, request, obj):
        """Méthode de soft delete pour l'admin"""
        obj.delete()  # Utilisera votre méthode personnalisée

    def delete_queryset(self, request, queryset):
        """Soft delete pour une sélection multiple"""
        for obj in queryset:
            obj.delete()

    list_display = ['email', 'is_active'] #email remplace username (par default)
    ordering = ['id'] # Trier par email

    
admin.site.register(User, CustomUserAdmin)