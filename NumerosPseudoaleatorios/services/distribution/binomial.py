from collections import Counter
import math
import numpy as np


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

def normalizar_numero(x):
    x = abs(int(x))  
    digitos = len(str(x))
    return x / (10 ** digitos)

def separar_digitos(numeros):
    digitos = []
    for numero in numeros:
        numero_str = str(abs(int(numero)))  # Por si hay negativos o floats
        for d in numero_str:
            digitos.append(int(d))
    return digitos

def simular_binomial(numeros_aleatorios, n, p):
    valores_x_simulacion = []
    numeros_aleatorios = separar_digitos(numeros_aleatorios)
    print(len(numeros_aleatorios))
    for i in range(0, len(numeros_aleatorios), n):
        grupo = numeros_aleatorios[i:i + n]
        exitos = 0

        for u in grupo:
            u = normalizar_numero(u)
            if u < p:
                exitos += 1

        print(f"Grupo {i // n + 1}: {grupo} => Éxitos: {exitos} (p={p})")
        valores_x_simulacion.append(exitos)
    
    total = len(valores_x_simulacion)
    frecuencias = Counter(valores_x_simulacion)
    valores_x_simulados = list(range(n))
    
    acumulado = 0
    valores_acumulados_simulados = []
    valores_probabilidad_simulados = []

    for x in valores_x_simulados:
        relativa = frecuencias.get(x, 0) / total
        valores_probabilidad_simulados.append(relativa)
        acumulado += relativa
        valores_acumulados_simulados.append(acumulado)

    # Copia editable
    x_vals = valores_x_simulados.copy()
    p_vals = valores_probabilidad_simulados.copy()

    for i, p in enumerate(p_vals):
        if p == 0:
            distancias = [
                (j, abs(x_vals[j] - x_vals[i]))
                for j in range(len(p_vals)) if p_vals[j] is not None and p_vals[j] > 0
            ]
            if distancias:
                j_mas_cercano = min(distancias, key=lambda x: x[1])[0]
                p_vals[j_mas_cercano] += p_vals[i]
            p_vals[i] = None

    # Reconstruir listas sin los descartados
    valores_x_final = []
    valores_probabilidad_final = []

    for x, p in zip(x_vals, p_vals):
        if p is not None:
            valores_x_final.append(x)
            valores_probabilidad_final.append(p)

    # Recalcular acumulados
    acumulado = 0
    valores_acumulados_final = []
    for p in valores_probabilidad_final:
        acumulado += p
        valores_acumulados_final.append(acumulado)

    print("frecuencia relativa (agrupada): ", valores_probabilidad_final)
    print("valores acumulados simulacion (agrupados): ", valores_acumulados_final)
    print("valores x (agrupados): ", valores_x_final)
    print("valores_x_simulacion:", valores_x_simulacion)

    return (
        [round(x, 5) for x in valores_x_final],
        [round(p, 5) for p in valores_probabilidad_final],
        [round(a, 5) for a in valores_acumulados_final]
    )
    return n * p * (1 - p)
