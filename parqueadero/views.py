from django.shortcuts import redirect, render
from .models import Usuario, Vehiculo, Tarifa, PuestoParqueadero, Estacionamiento
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from decimal import Decimal

# Create your views here.

def inicio(request):
    
    total_vehiculos = Vehiculo.objects.count()
    total_usuarios = Usuario.objects.count()
    total_puestos = PuestoParqueadero.objects.count()
    puestos_disponibles = PuestoParqueadero.objects.filter(estado="disponible").count()
    vehiculos_ingresados = PuestoParqueadero.objects.filter(estado="ocupado").count()

    context = {
        "total_vehiculos": total_vehiculos,
        "total_usuarios": total_usuarios,
        "total_puestos": total_puestos,
        "puestos_disponibles": puestos_disponibles,
        "vehiculos_ingresados": vehiculos_ingresados,
    }

    
    return render(request, 'inicio.html', context )

def crear_cuenta(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        telefono = request.POST.get("telefono")
        password = request.POST.get("password")

        if Usuario.objects.filter(nombre=nombre).exists():
            error="El nombre ya está registrado."
            return render(request,"crear_cuenta.html", {"error": error})

        user = Usuario.objects.create(
            nombre=nombre,
            telefono=telefono,
            contraseña=password
        )

        return redirect("inicio")

    return render(request, "crear_cuenta.html")

def registrar_vehiculo(request):
    if request.method == "POST":
        id_usuario = request.POST.get("id_usuario")
        placa = request.POST.get("placa")
        tipo = request.POST.get("tipo_vehiculo")

        if Vehiculo.objects.filter(placa=placa).exists():
            error="La placa ya está registrada."
            return render(request,"registrar_vehiculo.html", {"error": error})
        
        usuario= Usuario.objects.get(id=id_usuario)

        vehiculo = Vehiculo.objects.create(
            placa=placa,
            tipo=tipo,
            id_usuario=usuario

        )

        return redirect("inicio")

    usuarios = Usuario.objects.all()
    return render(request, "registrar_vehiculo.html", {"usuarios": usuarios})

def gestionar_puestos(request):
    puestos = PuestoParqueadero.objects.all()

    lista_puestos = []
    for puesto in puestos:
        estacionamiento = Estacionamiento.objects.filter(id_puesto=puesto, fecha_salida__isnull=True).first()
        
        if estacionamiento:
            # Puesto ocupado - obtener información del vehículo y propietario
            vehiculo = estacionamiento.id_vehiculo
            propietario = vehiculo.id_usuario
            
            info_puesto = {
                "numero_puesto": puesto.numero_puesto,
                "estado": puesto.estado,
                "placa": vehiculo.placa,
                "propietario": propietario.nombre,
                "telefono": propietario.telefono,
                "ocupado": True
            }
        else:
            # Puesto vacío
            info_puesto = {
                "numero_puesto": puesto.numero_puesto,
                "estado": puesto.estado,
                "placa": "—",
                "propietario": "—",
                "telefono": "—",
                "ocupado": False
            }
        
        lista_puestos.append(info_puesto)

    return render(request, "gestionar_puestos.html", {"puestos": lista_puestos}) 
  
@require_http_methods(["GET"])
def obtener_vehiculos_usuario(request):
    id_usuario = request.GET.get("id_usuario")
    
    if not id_usuario:
        return JsonResponse({"error": "ID de usuario no proporcionado"}, status=400)
    
    try:
        vehiculos = Vehiculo.objects.filter(id_usuario=id_usuario)
        data = [
            {"id": v.id, "placa": v.placa, "tipo": v.tipo}
            for v in vehiculos
        ]
        return JsonResponse({"vehiculos": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def ingresar_vehiculo(request):
    if request.method == "POST":
        id_vehiculo = request.POST.get("id_vehiculo")
        id_puesto = request.POST.get("id_puesto")
        id_usuario = request.POST.get("id_usuario")

        vehiculo = Vehiculo.objects.get(id=id_vehiculo)
        puesto = PuestoParqueadero.objects.get(id=id_puesto)
        usuario = Usuario.objects.get(id=id_usuario)

        if puesto.estado == "ocupado":
            error="El puesto ya está ocupado."
            vehiculos = Vehiculo.objects.all()
            puestos = PuestoParqueadero.objects.filter(estado="disponible")
            return render(request,"ingresar_vehiculo.html", {"error": error, "vehiculos": vehiculos, "puestos": puestos})

        estacionamiento = Estacionamiento.objects.create(
            id_vehiculo=vehiculo,
            id_puesto=puesto,
            id_usuario=usuario,
            fecha_entrada=timezone.now()
        )

        puesto.estado = "ocupado"
        puesto.save()

        return redirect("inicio")

    vehiculos = Vehiculo.objects.all()
    puestos = PuestoParqueadero.objects.filter(estado="disponible")
    usuarios = Usuario.objects.all()
    return render(request, "ingresar_vehiculo.html", {"vehiculos": vehiculos, "puestos": puestos, "usuarios": usuarios})

def retirar_vehiculo(request):
    # Obtener todos los estacionamientos activos (sin fecha de salida)
    estacionamientos = Estacionamiento.objects.filter(fecha_salida__isnull=True)
    
    lista_vehiculos = []
    for estacionamiento in estacionamientos:
        vehiculo = estacionamiento.id_vehiculo
        usuario = estacionamiento.id_usuario
        puesto = estacionamiento.id_puesto
        
        info_vehiculo = {
            "id_estacionamiento": estacionamiento.id,
            "numero_puesto": puesto.numero_puesto,
            "placa": vehiculo.placa,
            "tipo": vehiculo.tipo,
            "propietario": usuario.nombre,
            "telefono": usuario.telefono,
            "fecha_entrada": estacionamiento.fecha_entrada,
        }
        lista_vehiculos.append(info_vehiculo)
    
    return render(request, "retirar_vehiculo.html", {"vehiculos": lista_vehiculos})

def procesar_retiro(request):
    if request.method == "POST":
        id_estacionamiento = request.POST.get("id_estacionamiento")
        
        try:
            estacionamiento = Estacionamiento.objects.get(id=id_estacionamiento)
            puesto = estacionamiento.id_puesto
            
            estacionamiento.fecha_salida = timezone.now()
            
            tiempo_estacionado = estacionamiento.fecha_salida - estacionamiento.fecha_entrada
            horas_total = Decimal(str(tiempo_estacionado.total_seconds() / 3600))
            estacionamiento.horas_total = horas_total
            
            vehiculo = estacionamiento.id_vehiculo
            tarifa = Tarifa.objects.filter(tipo_vehiculo=vehiculo.tipo).first()
            if tarifa:
                monto_total = horas_total * tarifa.precio_hora
                estacionamiento.monto_total = monto_total
            
            estacionamiento.save()
            
            puesto.estado = "disponible"
            puesto.save()
            
            return redirect("detalles_vehiculo", id_estacionamiento=estacionamiento.id)
        except Estacionamiento.DoesNotExist:
            return redirect("retirar_vehiculo")
    
    return redirect("retirar_vehiculo")

def detalles_vehiculo(request, id_estacionamiento):
    try:
        estacionamiento = Estacionamiento.objects.get(id=id_estacionamiento)
        vehiculo = estacionamiento.id_vehiculo
        usuario = estacionamiento.id_usuario
        puesto = estacionamiento.id_puesto
        
        detalles = {
            "id_estacionamiento": estacionamiento.id,
            "numero_puesto": puesto.numero_puesto,
            "placa": vehiculo.placa,
            "tipo_vehiculo": vehiculo.tipo,
            "propietario": usuario.nombre,
            "telefono": usuario.telefono,
            "fecha_entrada": estacionamiento.fecha_entrada,
            "fecha_salida": estacionamiento.fecha_salida if estacionamiento.fecha_salida else "Pendiente",
            "horas_total": estacionamiento.horas_total if estacionamiento.horas_total else "Pendiente",
            "monto_total": estacionamiento.monto_total if estacionamiento.monto_total else "Pendiente",
            "estado": "Retirado" if estacionamiento.fecha_salida else "Activo",
        }
        
        return render(request, "detalles_vehiculos.html", {"detalles": detalles})
    except Estacionamiento.DoesNotExist:
        return redirect("inicio")

def gestionar_vehiculos(request):
    vehiculos = Vehiculo.objects.all()
    
    lista_vehiculos = []
    for vehiculo in vehiculos:
        usuario = vehiculo.id_usuario

        estacionamiento = Estacionamiento.objects.filter(id_vehiculo=vehiculo).last()
        
        info_vehiculo = {
            "id_vehiculo": vehiculo.id,
            "placa": vehiculo.placa,
            "tipo": vehiculo.tipo,
            "propietario": usuario.nombre if usuario else "—",
            "telefono": usuario.telefono if usuario else "—",
            "id_estacionamiento": estacionamiento.id if estacionamiento else None,
            "estado_estacionamiento": "Activo" if estacionamiento and not estacionamiento.fecha_salida else "Sin registros",
        }
        lista_vehiculos.append(info_vehiculo)
    
    return render(request, "gestionar_vehiculos.html", {"vehiculos": lista_vehiculos})