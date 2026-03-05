from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Task


@login_required
def dashboard(request):
    tasks = Task.objects.filter(assignee=request.user)

    context = {
        "tasks": tasks
    }

    return render(request, "tasks/dashboard.html", context)