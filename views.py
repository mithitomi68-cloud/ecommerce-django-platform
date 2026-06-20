from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import Producto
from .carrito import Carrito

def home(request):
    productos = Producto.objects.all()
    # Creamos la instancia del carrito para que el HTML la reconozca
    carrito = Carrito(request) 
    return render(request, 'home.html', {'productos': productos, 'carrito': carrito})

def tienda(request, categoria=None):
    # Si recibimos una categoría desde la URL, filtramos los productos
    if categoria:
        # __iexact hace que coincida 'men' con 'Men' o 'MEN'
        productos = Producto.objects.filter(categoria__nombre__iexact=categoria)
    else:
        # Si no hay categoría (entró a /tienda/ normal), mostramos todos
        productos = Producto.objects.all()
    
    carrito = Carrito(request) 
    
    # Calculamos el total para la tienda
    total_carrito = 0
    for key, value in carrito.carrito.items():
        total_carrito += float(value['precio'])
    
    meta = 200
    faltante = meta - total_carrito if total_carrito < meta else 0

    return render(request, 'tienda.html', {
        'productos': productos, 
        'carrito': carrito,
        'total_carrito': total_carrito,
        'faltante': int(faltante),
        'categoria_actual': categoria # Para saber qué estamos viendo en el HTML
    })

# --- FUNCIONES DEL CARRITO ---

def agregar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.agregar(producto=producto)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def eliminar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.eliminar(producto=producto)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.restar(producto=producto)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect("home")

def detalle_producto(request, producto_id):
    # Cambia .get por get_object_or_404 para mayor seguridad
    producto = get_object_or_404(Producto, id=producto_id)
    
    carrito = Carrito(request)
    total_carrito = 0
    
    for key, value in carrito.carrito.items():
        total_carrito += float(value['precio']) * int(value['cantidad']) # Multiplicar por cantidad es más exacto
    
    meta = 200
    faltante = max(0, meta - total_carrito)
    porcentaje = min(100, (total_carrito / meta) * 100)

    context = {
        'producto': producto,
        'total_carrito': total_carrito,
        'faltante': int(faltante),
        'porcentaje_envio': porcentaje
    }
    return render(request, 'detalle.html', context)

def checkout(request):
    carrito = Carrito(request)
    
    if request.method == "POST":
        # 1. Atrapamos todos los datos del formulario
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion') # <--- Nuevo
        ciudad = request.POST.get('ciudad')       # <--- Nuevo
        cp = request.POST.get('codigo_postal')    # <--- Nuevo
        
        # 2. Armamos la lista de productos
        detalles_pedido = ""
        for key, value in carrito.carrito.items():
            detalles_pedido += f"- {value['nombre']} (x{value['cantidad']})\n"
        
        # 3. Creamos el mensaje súper detallado
        cuerpo_mensaje = (
            f"El cliente {nombre} hizo un pedido.\n\n"
            f"DATOS DE ENVÍO:\n"
            f"Dirección: {direccion}\n"
            f"Ciudad: {ciudad}\n"
            f"Código Postal: {cp}\n"
            f"Teléfono: {telefono}\n\n"
            f"PRODUCTOS:\n{detalles_pedido}"
        )
        
        # 4. Enviamos a la terminal
        send_mail(
            f'PEDIDO NUEVO: {nombre}', 
            cuerpo_mensaje, 
            'ventas@bluerdress.com',
            ['tu_correo@ejemplo.com'],
            fail_silently=False,
        )
        
        carrito.limpiar()
        return redirect('home')

    return render(request, 'checkout.html', {'carrito': carrito})
