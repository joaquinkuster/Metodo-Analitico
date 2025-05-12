import math

def factorial(n):
    res = 1
    for x in range (2, n + 1):
        res *= x
    return res

def combinatoria(n, x):
    return factorial(n) / (factorial(x) * factorial(n - x))

def calcular_probabilidades(p, n):
    valoresX = []
    valoresProbabilidad = []
    valoresAcumulados = []
    suma_acumulada = 0
    
    for x in range (n + 1):
        valoresX.append(x)
        prob = combinatoria(n, x) * math.pow(p, x) * math.pow(1 - p, n - x)
        valoresProbabilidad.append(prob)
        suma_acumulada += prob
        valoresAcumulados.append(suma_acumulada)

    return valoresX, valoresProbabilidad, valoresAcumulados

def calcular_esperanza(p, n):
    return n * p

def calcular_varianza(p, n):
    return n * p * (1 - p)
