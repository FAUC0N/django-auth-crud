from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.utils.timezone import now  # Importar para obtener la fecha y hora actual

from utilities.validations import validate_username, validate_passwords
from .models import Task, Status, Priority
from .forms import TaskForm

# Create your views here.

def home(request):
    # Verifica si el usuario está autenticado
    if request.user.is_authenticated:
        pending_tasks = Task.objects.filter(
            created_by=request.user,
            status__status__in=['To Do', 'In Progress', 'Past Due']
        )
    else:
        pending_tasks = []  # No hay tareas para usuarios no autenticados

    return render(request, 'home.html', {
        'pending_tasks': pending_tasks
    })


def signup(request):
    if request.method == "GET":
        return render(request, 'signup.html', {
            'form': UserCreationForm()
        })
    elif request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            try:
                # Llama a las funciones de validación
                validate_username(username)
                validate_passwords(password1, password2)
                try:
                    # Guarda el usuario
                    user = form.save()  # Guarda el usuario en la base de datos
                    # Inicia sesión automáticamente
                    login(request, user)  # Autentica y crea la cookie de sesión
                    return redirect('home')
                except IntegrityError:
                    # Si ocurre un error de integridad, muestra un mensaje
                    form.add_error(None, "El nombre de usuario ya está en uso. Por favor, elige otro.")                        
            except ValidationError as e:
                form.add_error(None, e)  # Agrega los errores al formulario

        # Si hay errores, vuelve a renderizar el formulario
        return render(request, 'signup.html', {
            'form': form
        })
    else:
        return HttpResponseNotAllowed(["GET", "POST"])


@login_required
def tasks(request):
    # Filtra las tareas creadas por el usuario autenticado y que no tienen una fecha de finalización 
    # (es decir, tareas que aún no están completadas).
    # tasks = Task.objects.filter(created_by=request.user, completion_date__isnull=True)
    tasks = Task.objects.filter(created_by=request.user, status__status__in=['To Do', 'In Progress', 'Past Due'])
    return render(request,'tasks/tasks.html',{
        'tasks': tasks
    })


@login_required
def tasks_completed(request):
    # Filtra las tareas creadas por el usuario autenticado y que ya tiene fecha de terminación y un progreso del 100% 
    tasks = Task.objects.filter(
        created_by=request.user, 
        status__status__in=['Completed'], 
        completion_date__isnull=False,
        progress=100).order_by('-priority', '-completion_date')
    return render(request,'tasks/tasks.html',{
        'tasks': tasks
    })


@login_required
def task_add(request):
    if request.method == "GET":
        return render(request, 'tasks/task_create.html', {
            'form': TaskForm()
        })
    elif request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                # Guardar la tarea
                new_task = form.save(commit=False)
                new_task.created_by = request.user  # Asignar el usuario actual
                new_task.save()
                return redirect('tasks')
            except IntegrityError:
                # Manejo de errores de integridad, como duplicados o restricciones de base de datos
                form.add_error(None, "Ocurrió un error de integridad al guardar la tarea. Verifica los datos.")
            except ValueError as ve:
                # Manejo de errores relacionados con valores no válidos
                form.add_error(None, f"Valor inválido: {str(ve)}")
            except Exception as e:
                # Manejo genérico de errores
                form.add_error(None, f"Ocurrió un error inesperado: {str(e)}")
        else:
            # Si el formulario no es válido, volver a renderizar con errores
            form.add_error(None, "Por favor corrige los errores antes de enviar.")

        # Renderizar el formulario con los mensajes de error
        return render(request, 'tasks/task_create.html', {'form': form})
    else:
        return HttpResponseNotAllowed(["GET", "POST"])


@login_required
def task_detail(request, task_id):
    try:
        # Verificar que la tarea exista y pertenezca al usuario actual
        task = get_object_or_404(Task, pk=task_id, created_by=request.user)

        if request.method == "GET":
            # Si es un GET, renderizar el formulario con los datos existentes
            form = TaskForm(instance=task)
            return render(request, 'tasks/task_detail.html', {
                'task_detail': task,
                'form': form
            })

        elif request.method == "POST":
            # Procesar el formulario enviado en un POST
            task = get_object_or_404(Task, id=task_id, created_by=request.user)
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                # Actualizar la tarea y guardarla
                task = form.save(commit=False)
                task.save()  # Guarda los cambios en la tarea
                messages.success(request, "Task updated successfully!")  # Notificar éxito
                return redirect('tasks')
            else:
                # Si el formulario no es válido, mostrar errores
                messages.error(request, "There were errors updating the task.")
                return render(request, 'tasks/task_detail.html', {
                    'task_detail': task,
                    'form': form
                })
        else:
            # Manejar métodos no permitidos
            return HttpResponseNotAllowed(["GET", "POST"])

    except Task.DoesNotExist:
        # Manejo de error si la tarea no existe
        messages.error(request, "Task not found or you do not have permission to access it.")
        return redirect('tasks')

    except Exception as e:
        # Manejo general de errores
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('tasks')


@login_required
def task_complete(request, task_id):
    # Obtener la tarea o lanzar un 404 si no existe o no pertenece al usuario actual
    task = get_object_or_404(Task, pk=task_id, created_by=request.user)
    if request.method == 'POST':
        try:
            # Actualizar los valores de la tarea
            task.status = Status.objects.get(status="Completed")  # Asegúrate de que "Completed" exista en tu base de datos
            task.progress = 100
            task.completion_date = now()
            task.save()
            # Agregar un mensaje de éxito
            messages.success(request, f"Task '{task.name}' marked as completed successfully!")
            return redirect('tasks')
        except Exception as e:
            # Manejar errores y notificar al usuario
            messages.error(request, f"An error occurred while marking the task as completed: {str(e)}")
            return redirect('tasks')
    else:
        # Si el método no es POST, devolver un error HTTP
        return HttpResponseNotAllowed(['POST'])


@login_required
def task_delete(request, task_id):
    # Obtener la tarea o lanzar un 404 si no existe o no pertenece al usuario actual
    task = get_object_or_404(Task, pk=task_id, created_by=request.user)
    if request.method == 'POST':
        try:
            task.delete()
            # Agregar un mensaje de éxito
            messages.success(request, f"Task '{task.name}' deleted successfully!")
            return redirect('tasks')
        except Exception as e:
            # Manejar errores y notificar al usuario
            messages.error(request, f"An error occurred while deleting the task: {str(e)}")
            return redirect('tasks')
    else:
        # Si el método no es POST, devolver un error HTTP
        return HttpResponseNotAllowed(['POST'])


def signin(request):
    if request.method == "GET":
        return render(request, 'signin.html', {
            'form': AuthenticationForm()
        })
    elif request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            # Autentica al usuario si las credenciales son correctas
            user = form.get_user()
            login(request, user)  # Inicia sesión creando la cookie de sesión
            return redirect('home')  # Redirige al usuario al home
        else:
            # Agrega un mensaje de error al formulario
            form.add_error(None, "Usuario o contraseña incorrectos")

        # Renderiza nuevamente el formulario con los errores
        return render(request, 'signin.html', {
            'form': form
        })

    else:
        return HttpResponseNotAllowed(["GET", "POST"])


@login_required
def signout(request):
    logout(request)
    return redirect('home')
