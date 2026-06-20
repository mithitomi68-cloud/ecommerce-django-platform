from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tienda import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('checkout/', views.checkout, name='checkout'),
    path('', views.home, name='home'),
    
    # Rutas del carrito para bluerdress
    path('agregar/<int:producto_id>/', views.agregar_producto, name="agregar"),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name="eliminar"),
    path('restar/<int:producto_id>/', views.restar_producto, name="restar"),
    path('limpiar/', views.limpiar_carrito, name="limpiar"),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('tienda/', views.tienda, name='tienda'),
    path('tienda/<str:categoria>/', views.tienda, name='tienda_categoria'), 

]
# Esto permite que se vean las fotos de tus tejidos
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    