from django.urls import path
from apps.grooming import views

urlpatterns = [
    path('', views.grooming_lista, name='grooming_lista'),
    path('nueva/', views.grooming_crear, name='grooming_crear'),
    path('<int:pk>/editar/', views.grooming_editar, name='grooming_editar'),
    path('<int:pk>/estado/', views.grooming_estado, name='grooming_estado'),
]
