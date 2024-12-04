from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/completed', views.tasks_completed, name='tasks_completed'),
    path('tasks/add', views.task_add, name='task_add'),
    path('tasks/<int:task_id>', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/complete', views.task_complete, name='task_complete'),
    path('tasks/<int:task_id>/delete', views.task_delete, name='task_delete'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
]
