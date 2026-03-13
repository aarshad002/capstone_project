from django.urls import path
from .views import dashboard, task_detail, TaskCreateView, TaskUpdateView, TaskDeleteView
urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("tasks/create/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("tasks/<int:pk>/", task_detail, name="task_detail"),
]
