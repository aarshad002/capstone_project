from django.contrib import admin
from .models import Task, Comment, TaskRequest


@admin.register(TaskRequest)
class TaskRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "requester", "status", "created_at")
    search_fields = ("title", "requester__username", "project__title")
    list_filter = ("status", "created_at")


admin.site.register(Task)
admin.site.register(Comment)