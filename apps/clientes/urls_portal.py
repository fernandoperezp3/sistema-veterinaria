from django.urls import path

from apps.clientes import views_portal

urlpatterns = [
    path('', views_portal.portal_inicio, name='portal_inicio'),
    path('perfil/', views_portal.portal_perfil, name='portal_perfil'),
    path('mascota/nueva/', views_portal.portal_mascota_nueva, name='portal_mascota_nueva'),
]
