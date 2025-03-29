from django.db import IntegrityError
# Renderizar plantalli, redireccionar
from django.shortcuts import render, redirect, get_object_or_404
# Platilla Formulario
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User  # Metodo creación formulario
# Generar una sesión en cookies
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse  # Respuesta simple Http
from .forms import TaskForm  # Importar formulario creado por nosotros mismos
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:  # validar contraseñas
            try:
                user = User.objects.create_user(
                    # crear usuario en variable
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()  # guardar usuario en la bd
                login(request, user)  # crear sesión en cookies
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': "Usuario ya existente"
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': "Contraseñas no coiciden"
        })

@login_required
def tasks(request):
    # Devuelve tareas del usuario logeado
    tasks = Task.objects.filter(user=request.user, datacompleted__isnull=True)

    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def tasks_completed(request):
    # Devuelve tareas del usuario logeado
    tasks = Task.objects.filter(user=request.user, datacompleted__isnull=False).order_by('-datacompleted')

    return render(request, 'tasks.html', {
        'tasks': tasks
    })


@login_required
def create_task(request):

    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()  # Este es el commit para ingresar los datos a la base de datos
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': "Por favor provee datos validos"
            })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': "Error al actualizar"})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method  == 'POST':
        task.datacompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required    
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method  == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'User or pass is incorrec'
            })
        else:
            login(request, user)
            return redirect('tasks')
