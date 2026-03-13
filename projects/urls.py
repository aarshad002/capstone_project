from django.urls import path
from .views import project_list, project_detail, ProjectCreateView, ProjectDeleteView

urlpatterns = [
    path("projects/", project_list, name="project_list"),
    path("projects/<int:project_id>/", project_detail, name="project_detail"),
    path("projects/create/", ProjectCreateView.as_view(), name="project_create"),
    path("projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="project_delete"),
]
