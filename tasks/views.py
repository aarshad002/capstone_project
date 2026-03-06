from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Task


@login_required
def dashboard(request):
    qs = Task.objects.filter(assignee=request.user)

    context = {
        "tasks": qs.order_by("due_date", "priority"),
        "pending_count": qs.filter(status=Task.Status.PENDING).count(),
        "in_progress_count": qs.filter(status=Task.Status.IN_PROGRESS).count(),
        "completed_count": qs.filter(status=Task.Status.COMPLETED).count(),
    }
    return render(request, "tasks/dashboard.html", context)