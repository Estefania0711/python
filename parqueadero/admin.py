from django.contrib import admin
from .models import Usuario, Vehiculo, Tarifa, PuestoParqueadero, Estacionamiento

admin.site.register(Usuario)
admin.site.register(Vehiculo)
admin.site.register(Tarifa)
admin.site.register(PuestoParqueadero)
admin.site.register(Estacionamiento)
