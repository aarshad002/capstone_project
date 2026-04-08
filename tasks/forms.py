from django import forms
from django.contrib.auth import get_user_model
from .models import Task, Comment, TaskRequest
from projects.models import Project

User = get_user_model()


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "project",
            "assignee",
            "due_date",
        ]

    def __init__(self, *args, user=None, project=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None and user.role == user.Role.MANAGER:
            self.fields["project"].queryset = Project.objects.filter(team__manager=user)

        if project is not None:
            self.fields["project"].queryset = Project.objects.filter(id=project.id)
            self.fields["project"].initial = project
            self.fields["project"].empty_label = None

            if project.team is not None:
                member_ids = project.team.members.values_list("id", flat=True)
                allowed_ids = list(member_ids) + [project.team.manager.id]
                self.fields["assignee"].queryset = User.objects.filter(id__in=allowed_ids).distinct()
            else:
                self.fields["assignee"].queryset = User.objects.none()
        else:
            self.fields["assignee"].queryset = User.objects.none()


class TaskRequestForm(forms.ModelForm):
    class Meta:
        model = TaskRequest
        fields = [
            "title",
            "description",
            "project",
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields["project"].queryset = Project.objects.filter(team__members=user).distinct()

class TaskRequestReviewForm(forms.ModelForm):
    class Meta:
        model = TaskRequest
        fields = ["status"]
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]