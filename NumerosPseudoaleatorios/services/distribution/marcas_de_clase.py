import math
from ..test import chi_cuadrado

def calcular_intervalos(grupos, cantidad_intervalos):
    min_val = min(grupos)
    max_val = max(grupos)
    rango = max_val - min_val or 1  # Evita división por cero

    amplitud = rango / cantidad_intervalos
    limites = [min_val + i * amplitud for i in range(cantidad_intervalos + 1)]

    return [(limites[i], limites[i + 1]) for i in range(cantidad_intervalos)]


def calcular_cantidad_intervalos(n):
    k = int(1 + math.log2(n))
    # Si k es par, lo elevamos al siguiente impar
    if k % 2 == 0:
        k += 1
    return k

def calcular_densidades(variable_aleatoria):
    
    # Agrupar en intervalos
    k = calcular_cantidad_intervalos(len(variable_aleatoria))
    intervalos = calcular_intervalos(variable_aleatoria, k)
    marcas = calcular(intervalos)

    # Contar cuantos caen en cada intervalo (frec. simuladas)
    observadas, _ = chi_cuadrado.calcular_frecuencias(
        variable_aleatoria, intervalos
    )

    # Calcular densidades
    densidades = []
    total = len(variable_aleatoria)

    for i in range(k):
        ancho_bin = intervalos[i][1] - intervalos[i][0]
        frecuencia = observadas[i]
        densidad = frecuencia / (total * ancho_bin)
        densidades.append(densidad)

    # Calcular acumuladas
    acumuladas = []
    acumulada = 0

    for i in range(len(densidades)):
        ancho_bin = intervalos[i][1] - intervalos[i][0]
        area = densidades[i] * ancho_bin  # área del rectángulo
        acumulada += area
        acumuladas.append(acumulada)
        
    return intervalos, marcas, densidades, acumuladas


def calcular(intervalos):
    marcas_de_clase = []

    for li, ls in intervalos:
        marcas_de_clase.append(round((li + ls) / 2, 2))

    return marcas_de_clase
