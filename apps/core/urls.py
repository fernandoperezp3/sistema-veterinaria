from django.urls import path
from apps.core import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mantenimiento/', views.mantenimiento_index, name='mantenimiento_index'),
    path('mantenimiento/backup/', views.mantenimiento_backup, name='mantenimiento_backup'),
    path('mantenimiento/restore/', views.mantenimiento_restore, name='mantenimiento_restore'),
    path('mantenimiento/reset/', views.mantenimiento_reset, name='mantenimiento_reset'),
    path('microservicios/', views.microservicios_panel, name='microservicios_panel'),
]
