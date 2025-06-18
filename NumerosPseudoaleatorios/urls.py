from django.urls import path, include
from . import views

generador_patterns = [
    path("", views.generar_secuencia, name="generar"),
    path("ver/<int:id>/", views.ver_secuencia, name="ver"),
    path("eliminar/<int:id>/", views.eliminar_secuencia, name="eliminar"),
    path("testear/<int:id>/", views.testear_secuencia, name="testear"),
    path("distribuir/<int:id>/", views.distribuir_secuencia, name="distribuir"),
]

test_patterns = [
    path("", views.generar_test, name="generar"),
    path("ver/<int:id>/", views.ver_test, name="ver"),
    path("eliminar/<int:id>/", views.eliminar_test, name="eliminar"),
]

distribucion_ejemplos_patterns = [
    path("", views.menu_ejemplos, name="menu"),
    path("<str:distribucion>/", views.ejemplos_distribucion, name="ejemplo"),
]

distribucion_patterns = [
    path("", views.generar_distribucion, name="generar"),
    path("ver/<int:id>/", views.ver_distribucion, name="ver"),
    path("eliminar/<int:id>/", views.eliminar_distribucion, name="eliminar"),
    path("simular/<int:id>/", views.simular_distribucion, name="simular"),
    path(
        "ejemplos/",
        include(
            (distribucion_ejemplos_patterns, "NumerosPseudoaleatorios"),
            namespace="ejemplos",
        ),
    ),
]

simulacion_patterns = [
    path("", views.generar_simulacion, name="generar"),
    path("guardar-camion/", views.guardar_camion, name="guardar.camion"),
    path("simulacion/ver/<int:id>/", views.ver_simulacion, name="ver"),
    path("simulacion/eliminar/<int:id>/", views.eliminar_simulacion, name="eliminar"),
    path("eliminar-camion/<int:id>/", views.eliminar_camion, name="eliminar.camion"),
]

camion_patterns = [
    path("", views.guardar_camion, name="guardar"),
    path("eliminar/<int:id>/", views.eliminar_camion, name="eliminar"),
]

urlpatterns = [
    path(
        "",
        include(
            (simulacion_patterns, "NumerosPseudoaleatorios"), namespace="simulacion"
        ),
    ),
    path(
        "camion/",
        include((camion_patterns, "NumerosPseudoaleatorios"), namespace="camion"),
    ),
    path(
        "generador/",
        include((generador_patterns, "NumerosPseudoaleatorios"), namespace="generador"),
    ),
    path(
        "test/", include((test_patterns, "NumerosPseudoaleatorios"), namespace="test")
    ),
    path(
        "distribucion/",
        include(
            (distribucion_patterns, "NumerosPseudoaleatorios"), namespace="distribucion"
        ),
    ),
]
