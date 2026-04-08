from urllib import request

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .forms import TaskForm, CommentForm, TaskRequestForm, TaskRequestReviewForm
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from .models import Task, TaskRequest, Comment
from projects.models import Project
from django.core.exceptions import PermissionDenied
from collections import defaultdict

def send_task_assignment_email(task):
    assignee = task.assignee

    if not assignee or not assignee.email:
        return

    subject = f"You have been assigned a new task: {task.title}"
    message = (
        f"Hello {assignee.username},\n\n"
        f"You have been assigned a new task in TaskFlow.\n\n"
        f"Task: {task.title}\n"
        f"Project: {task.project.title}\n"
        f"Team: {task.project.team.name}\n"
        f"Status: {task.get_status_display()}\n"
        f"Due date: {task.due_date}\n\n"
        f"Please log in to TaskFlow to view the task details."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [assignee.email],
        fail_silently=False,
    )

@login_required
def dashboard(request):
    my_tasks = Task.objects.filter(assignee=request.user).select_related("project__team").order_by("project__title", "due_date")
    grouped_tasks = defaultdict(list)

    for task in my_tasks:
        grouped_tasks[task.project].append(task)
    
    if request.user.role == request.user.Role.MANAGER:
        managed_projects = Project.objects.filter(team__manager=request.user)
        summary_qs = Task.objects.filter(project__team__manager=request.user)
    else:
        managed_projects = None
        summary_qs = my_tasks

    context = {
        "my_tasks": my_tasks,
        "grouped_tasks": dict(grouped_tasks),
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

        task_request = self.get_task_request()
        if task_request and hasattr(task_request, "created_task"):
            return redirect("task_detail", pk=task_request.created_task.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_task_request(self):
        request_id = self.request.GET.get("request") or self.request.POST.get("request")
        if not request_id:
            return None

        try:
            return TaskRequest.objects.get(
                id=request_id,
                project__team__manager=self.request.user,
                status=TaskRequest.Status.APPROVED,
            )
        except TaskRequest.DoesNotExist:
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user

        project = None
        project_id = self.request.POST.get("project") or self.request.GET.get("project")
        if project_id:
            try:
                project = Project.objects.get(
                    id=project_id,
                    team__manager=self.request.user
                )
            except Project.DoesNotExist:
                project = None

        task_request = self.get_task_request()
        if task_request is not None:
            project = task_request.project

        kwargs["project"] = project
        return kwargs

    def get_initial(self):
        initial = super().get_initial()

        project_id = self.request.GET.get("project")
        if project_id:
            initial["project"] = project_id

        task_request = self.get_task_request()
        if task_request is not None:
            initial["title"] = task_request.title
            initial["description"] = task_request.description
            initial["project"] = task_request.project.id

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_request"] = self.get_task_request()
        return context

    def form_valid(self, form):
        task_request = self.get_task_request()

        if task_request is not None:
            if hasattr(task_request, "created_task"):
                return redirect("task_detail", pk=task_request.created_task.pk)

            if form.instance.project != task_request.project:
                form.add_error("project", "Project must match the approved request.")
                return self.form_invalid(form)

            form.instance.source_request = task_request

        response = super().form_valid(form)
        send_task_assignment_email(self.object)
        return response
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()

        if request.user.role == request.user.Role.MANAGER:
            if task.project.team.manager != request.user:
                raise PermissionDenied
        else:
            if task.assignee != request.user:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["project"] = self.get_object().project
        return kwargs

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

        if task.project.team.manager != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
    
@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.user.role == request.user.Role.MANAGER:
        if task.project.team.manager != request.user:
            raise PermissionDenied
    else:
        if task.assignee != request.user:
            raise PermissionDenied

    sort_order = request.GET.get("sort", "newest")

    if sort_order == "oldest":
        comments = task.comments.all().order_by("timestamp")
    else:
        sort_order = "newest"
        comments = task.comments.all().order_by("-timestamp")

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            return redirect(f"{reverse('task_detail', kwargs={'pk': task.pk})}?sort={sort_order}")
    else:
        form = CommentForm()

    context = {
        "task": task,
        "comments": comments,
        "form": form,
        "sort_order": sort_order,
    }
    return render(request, "tasks/task_detail.html", context)

class TaskRequestCreateView(LoginRequiredMixin, CreateView):
    model = TaskRequest
    form_class = TaskRequestForm
    template_name = "tasks/task_request_form.html"
    success_url = reverse_lazy("dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.requester = self.request.user
        return super().form_valid(form)
    
class TaskRequestListView(LoginRequiredMixin, ListView):
    model = TaskRequest
    template_name = "tasks/task_request_list.html"
    context_object_name = "task_requests"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != request.user.Role.MANAGER:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return TaskRequest.objects.filter(
            project__team__manager=self.request.user
        ).order_by("-created_at")


class TaskRequestUpdateView(LoginRequiredMixin, UpdateView):
    model = TaskRequest
    form_class = TaskRequestReviewForm
    template_name = "tasks/task_request_review_form.html"
    success_url = reverse_lazy("task_request_list")

    def dispatch(self, request, *args, **kwargs):
        task_request = self.get_object()

        if request.user.role != request.user.Role.MANAGER:
            raise PermissionDenied

        if task_request.project.team.manager != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.status != TaskRequest.Status.PENDING:
            return redirect("task_request_review", pk=self.object.pk)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.object.status == TaskRequest.Status.APPROVED:
            if hasattr(self.object, "created_task"):
                return redirect("task_detail", pk=self.object.created_task.pk)

            return redirect(
                f"{reverse_lazy('task_create')}?project={self.object.project.id}&request={self.object.id}"
            )

        return response