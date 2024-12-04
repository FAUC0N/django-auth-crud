from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'objectives', 'start_date', 'due_date', 'priority']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'White a task name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Write a task description'}),
            'objectives': forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Write a task objectives'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),            
            'start_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',  # Muestra un selector de fecha y hora
                'class': 'form-control',
            }),
            'due_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
        }
