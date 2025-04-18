from django.urls import path, include
from . import views

secuencia_patterns = [
    path('generar/', views.generar_secuencia, name='generar'),
    path('ver/<int:id>/<str:tipo>/', views.ver_secuencia, name='ver'),
    path('eliminar/<int:id>/<str:tipo>/', views.eliminar_secuencia, name='eliminar'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('secuencia/', include((secuencia_patterns, 'NumerosPseudoaleatorios'), namespace='secuencia')),
]