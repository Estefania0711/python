from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear_cuenta/', views.crear_cuenta, name='crear_cuenta'),
    path('registrar_vehiculo/', views.registrar_vehiculo, name='registrar_vehiculo'),
    path('gestionar_puestos/', views.gestionar_puestos, name='gestionar_puestos'),
    path('ingresar_vehiculo/', views.ingresar_vehiculo, name='ingresar_vehiculo'),
    path('obtener-vehiculos/', views.obtener_vehiculos_usuario, name='obtener_vehiculos'),
    path('retirar_vehiculo/', views.retirar_vehiculo, name='retirar_vehiculo'),
    path('procesar_retiro/', views.procesar_retiro, name='procesar_retiro'),
    path('detalles_vehiculo/<int:id_estacionamiento>/', views.detalles_vehiculo, name='detalles_vehiculo'),
    path('gestionar_vehiculos/', views.gestionar_vehiculos, name='gestionar_vehiculos'),
]