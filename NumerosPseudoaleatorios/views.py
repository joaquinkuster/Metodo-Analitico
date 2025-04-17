from django.shortcuts import render
from .models import SecuenciaPseudoaleatoria

# Create your views here.

def index(request):
    return render(request, "numerospseudoleatorios/index.html")

def generar(request):
    secuencias = SecuenciaPseudoaleatoria.objects.all()
    return render(request, "numerospseudoleatorios/generador.html", {"secuencias": secuencias})