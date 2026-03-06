from django.shortcuts import render, get_object_or_404
from .models import Project


def project_list(request):
    projects = Project.objects.all()

    context = {
        "projects": projects
    }

    return render(request, "projects/project_list.html", context)


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    tasks = project.tasks.all()

    context = {
        "project": project,
        "tasks": tasks
    }

    return render(request, "projects/project_detail.html", context)