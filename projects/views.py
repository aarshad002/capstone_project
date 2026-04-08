from django.shortcuts import render, get_object_or_404
from .models import Project
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm


@login_required
def project_list(request):
    if request.user.role == request.user.Role.MANAGER:
        projects = Project.objects.filter(team__manager=request.user)
    else:
        projects = Project.objects.filter(team__members=request.user).distinct()

    context = {
        "projects": projects
    }

    return render(request, "projects/project_list.html", context)

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user.role == request.user.Role.MANAGER:
        if project.team.manager != request.user:
            raise PermissionDenied
    else:
        if not project.team.members.filter(pk=request.user.pk).exists():
            raise PermissionDenied

    tasks = project.tasks.all()

    context = {
        "project": project,
        "tasks": tasks
    }

    return render(request, "projects/project_detail.html", context)

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != request.user.Role.MANAGER:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)
    
class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "projects/project_confirm_delete.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        project = self.get_object()

        if request.user.role != request.user.Role.MANAGER:
            raise PermissionDenied

        if project.team.manager != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)