from django.db import models


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=255)
    contraseña = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Vehiculo(models.Model):
    id = models.AutoField(primary_key=True)
    placa = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=10)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.placa


class Tarifa(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_vehiculo = models.CharField(max_length=10)
    precio_hora = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.tipo_vehiculo}"


class PuestoParqueadero(models.Model):
    id = models.AutoField(primary_key=True)
    numero_puesto = models.CharField(max_length=10)
    estado = models.CharField(max_length=20)

    def __str__(self):
        return self.numero_puesto


class Estacionamiento(models.Model):
    id = models.AutoField(primary_key=True)
    id_vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, null=True, blank=True)
    id_puesto = models.ForeignKey(PuestoParqueadero, on_delete=models.CASCADE, null=True, blank=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    fecha_entrada = models.DateTimeField()
    fecha_salida = models.DateTimeField(null=True, blank=True)
    horas_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Estacionamiento {self.id}"
