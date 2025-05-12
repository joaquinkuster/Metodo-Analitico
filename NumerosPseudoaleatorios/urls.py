from django.urls import path, include
from . import views

secuencia_patterns = [
    path('generar/', views.generar_secuencia, name='generar'),
    path('ver/<int:id>/<str:tipo>/', views.ver_secuencia, name='ver'),
    path('eliminar/<int:id>/<str:tipo>/', views.eliminar_secuencia, name='eliminar'),
    path('testear/<int:id>/<str:tipo>/', views.testear_secuencia, name='testear'), 
]

test_patterns = [
    path('generar/', views.generar_test, name='generar'),
    path('ver/<int:id>/<str:tipo>/', views.ver_test, name='ver'),
    path('eliminar/<int:id>/<str:tipo>/', views.eliminar_test, name='eliminar')
]

distribucion_patterns = [
    path('binomial/', views.binomial, name='binomial'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('secuencia/', include((secuencia_patterns, 'NumerosPseudoaleatorios'), namespace='secuencia')),
    path('test/', include((test_patterns, 'NumerosPseudoaleatorios'), namespace="test")),
    path('distribucion/', include((distribucion_patterns, 'NumerosPseudoaleatorios'), namespace='distribucion')),
    
]