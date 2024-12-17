from django.contrib import admin
from .models import Project, Contributor


class ProjectAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        """Méthode de soft delete pour l'admin"""
        obj.delete()  # Utilisera votre méthode personnalisée

    def delete_queryset(self, request, queryset):
        """Soft delete pour une sélection multiple"""
        for obj in queryset:
            obj.delete()

admin.site.register(Project, ProjectAdmin)


class ContributorAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

admin.site.register(Contributor, ContributorAdmin)