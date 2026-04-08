from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings



class User(AbstractUser):
    class Role(models.TextChoices):
        MANAGER = "MANAGER", "Manager"
        EMPLOYEE = "EMPLOYEE", "Employee"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="managed_teams",
        limit_choices_to={"role": "MANAGER"},
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="teams",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name