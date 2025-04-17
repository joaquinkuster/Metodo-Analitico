from django.shortcuts import render
from .forms import GeneradorForm
import scipy.stats as stats
from collections import Counter

def generador_congruencial_multiplicativo(semilla, a, m, n):
    numeros = []
    Xn = semilla
    for _ in range(n):
        Xn = (a * Xn) % m
        numeros.append(Xn)
    return numeros

def index(request):
    form = GeneradorForm()
    resultados = None

    if request.method == "POST":
        form = GeneradorForm(request.POST)
        if form.is_valid():
            semilla = form.cleaned_data["semilla"]
            a = form.cleaned_data["a"]
            m = form.cleaned_data["m"]
            n = form.cleaned_data["n"]

            numeros_congruencial_multiplicativo = generador_congruencial_multiplicativo(semilla, a, m, n)
            
            resultados = {
                "numeros_congruencial_multiplicativo": numeros_congruencial_multiplicativo,
            }
            
    return render(request, "index.html", {"form": form, "resultados": resultados})