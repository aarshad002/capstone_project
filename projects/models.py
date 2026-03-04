from django.conf import settings
from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    start_date = models.DateField()
    end_date = models.DateField()

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_projects",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title