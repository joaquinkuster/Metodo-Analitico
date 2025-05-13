from collections import Counter
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

def normalizar_numero(x):
    x = abs(int(x))  
    digitos = len(str(x))
    return x / (10 ** digitos)

def simular_binomial(numeros_aleatorios, n, p):
    valores_x_simulacion = []
    
    for i in range(0, len(numeros_aleatorios), n):
        grupo = numeros_aleatorios[i:i + n]
        exitos = 0

        for u in grupo:
            u = normalizar_numero(u)
            if u < p:
                exitos += 1

        valores_x_simulacion.append(exitos)
    
    total = len(valores_x_simulacion)
    frecuencias = Counter(valores_x_simulacion)
    valores_x_simulados = list(range(n + 1))
    
    acumulado = 0
    valores_acumulados_simulados = []
    valores_probabilidad_simulados = []

    for x in valores_x_simulados:
        relativa = frecuencias.get(x, 0) / total
        valores_probabilidad_simulados.append(relativa)
        acumulado += relativa
        valores_acumulados_simulados.append(acumulado)
    print("frecuencia relativa (lo mismo que valores probabilidad): ", valores_probabilidad_simulados)
    print("valores acumulados simulacion: ", valores_acumulados_simulados)
    print("valores x: ", valores_x_simulados)

    return valores_x_simulados, valores_acumulados_simulados, valores_probabilidad_simulados
