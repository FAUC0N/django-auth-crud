from django.contrib import admin
from .models import Task, Priority, Status

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ("created_date",)

# Register your models here.
admin.site.register(Task, TaskAdmin)
admin.site.register(Priority)
admin.site.register(Status)
