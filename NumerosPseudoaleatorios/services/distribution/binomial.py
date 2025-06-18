from collections import Counter
import math
from .. import utils


def factorial(n):
    res = 1
    for x in range(2, n + 1):
        res *= x
    return res


def combinatoria(n, x):
    return factorial(n) / (factorial(x) * factorial(n - x))


def teorica(p, n):
    variable_aleatoria = list(range(n + 1))        
    probabilidades, acumuladas = calcular_probabilidades(variable_aleatoria, p, n)
    return variable_aleatoria, probabilidades, acumuladas

def simular(p, n, numeros):
    experimentos = []
    numeros = utils.separar_digitos(numeros)

    for i in range(0, len(numeros), n):
        grupo = numeros[i:i + n]
        if len(grupo) < n:
            break  # Ignorar grupo incompleto

        exitos = 0
        for u in grupo:
            u = utils.convertir_en_probabilidad(u, max(numeros))
            if u < p:
                exitos += 1

        experimentos.append(exitos)

    # Conteo de frecuencias
    total = len(experimentos)
    frecuencias = Counter(experimentos)

    # Probabilidades
    variable_aleatoria = sorted(frecuencias.keys())
    probabilidades = [frecuencias[x] / total for x in variable_aleatoria]
    acumuladas = []
    acumulado = 0
    for p in probabilidades:
        acumulado += p
        acumuladas.append(acumulado)

    return variable_aleatoria, probabilidades, acumuladas

def calcular_probabilidades(variable_aleatoria, p, n):
    probabilidades = []
    suma_acumulada = 0
    acumuladas = []
    
    for x in variable_aleatoria:
        prob = combinatoria(n, x) * math.pow(p, x) * math.pow(1 - p, n - x)
        probabilidades.append(prob)
        suma_acumulada += prob
        acumuladas.append(suma_acumulada)
    
    return probabilidades, acumuladas

def calcular_esperanza(p, n):
    return n * p


def calcular_varianza(p, n):
    return n * p * (1 - p)