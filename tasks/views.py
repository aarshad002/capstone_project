from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from .forms import TaskForm, CommentForm
from .models import Task
from projects.models import Project
from django.core.exceptions import PermissionDenied


@login_required
def dashboard(request):
    my_tasks = Task.objects.filter(assignee=request.user).order_by("due_date", "priority")

    if request.user.role == request.user.Role.MANAGER:
        managed_projects = Project.objects.filter(creator=request.user)
        summary_qs = Task.objects.filter(project__creator=request.user)
    else:
        managed_projects = None
        summary_qs = my_tasks

    context = {
        "my_tasks": my_tasks,
        "managed_projects": managed_projects,
        "pending_count": summary_qs.filter(status=Task.Status.PENDING).count(),
        "in_progress_count": summary_qs.filter(status=Task.Status.IN_PROGRESS).count(),
        "completed_count": summary_qs.filter(status=Task.Status.COMPLETED).count(),
    }
    return render(request, "tasks/dashboard.html", context)

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("dashboard")
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != request.user.Role.MANAGER:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()

        if request.user.role == request.user.Role.MANAGER:
            if task.project.creator != request.user:
                raise PermissionDenied
        else:
            if task.assignee != request.user:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.request.user.role != self.request.user.Role.MANAGER:
            allowed_fields = {"status"}
            for field_name in list(form.fields.keys()):
                if field_name not in allowed_fields:
                    del form.fields[field_name]

        return form


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("dashboard")
    
    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()

        if request.user.role != request.user.Role.MANAGER:
            raise PermissionDenied

        if task.project.creator != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
    
@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.user.role == request.user.Role.MANAGER:
        if task.project.creator != request.user:
            raise PermissionDenied
    else:
        if task.assignee != request.user:
            raise PermissionDenied

    comments = task.comments.all().order_by("-timestamp")

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            return redirect("task_detail", pk=task.pk)
    else:
        form = CommentForm()

    context = {
        "task": task,
        "comments": comments,
        "form": form,
    }
    return render(request, "tasks/task_detail.html", context)