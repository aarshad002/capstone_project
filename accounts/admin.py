from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Team


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "manager", "created_at")
    filter_horizontal = ("members",)