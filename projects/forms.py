from django import forms
from .models import Project
from accounts.models import Team


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "start_date",
            "end_date",
            "team",
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields["team"].queryset = Team.objects.filter(manager=user)