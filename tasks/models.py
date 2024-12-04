from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Priority(models.Model):
    level = models.IntegerField()
    name = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.level})"

# Modelo Status
class Status(models.Model):
    status = models.CharField(max_length=15)

    def __str__(self):
        return self.status

def get_default_status():
    # Obtiene el estado "To Do" como valor predeterminado
    return Status.objects.get(status="To Do").id

# Modelo Task
class Task(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    objectives = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    priority = models.ForeignKey(Priority, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=get_default_status)
    progress = models.IntegerField(default=0)  # Valor por defecto
    
    def __str__(self):
        return self.name + " - by " + self.created_by.username.upper()
