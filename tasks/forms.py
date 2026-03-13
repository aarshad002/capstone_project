from django import forms
from .models import Task, Comment

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
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]