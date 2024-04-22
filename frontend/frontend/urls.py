"""
URL configuration for frontend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.urls import path
from ITGSA import views

urlpatterns = [
    path('', views.home, name='home'),
    path('limpiarDatos', views.reiniciar_datos, name='reiniciar_datos'),
    path('configuracion', views.configuracion, name='configuracion'),
    path('transaccion', views.transaccion, name='transaccion'),
    path('configuracion/guardarConfiguracion', views.guardar_configuracion, name='guardar_configuracion'),
    path('transaccion/guardarTransaccion', views.guardar_transaccion, name='guardar_transaccion'),
    path('Ayuda', views.ayuda, name='ayuda'),
    path('clientes', views.clientes, name='clientes'),
    path('estado_cuenta/', views.estado_cuenta, name='estado_cuenta')

]

