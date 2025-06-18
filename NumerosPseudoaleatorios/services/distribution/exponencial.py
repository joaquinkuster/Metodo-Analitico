import math
from .. import utils
from . import marcas_de_clase


def teorica(tasa):

    variable_aleatoria = []
    densidades = []
    acumuladas = []
    suma_acumulada = 0

    umbral = 0.99
    incremento = 0.1
    x = 0

    # Generar puntos x hasta alcanzar el umbral de probabilidad acumulada
    while suma_acumulada < umbral:
        variable_aleatoria.append(x)
        densidades.append(tasa * math.exp(-tasa * x))
        suma_acumulada = 1 - math.exp(-tasa * x)
        acumuladas.append(suma_acumulada)
        x += incremento
        
    # Agrupar en intervalos
    k = marcas_de_clase.calcular_cantidad_intervalos(len(variable_aleatoria))
    intervalos = marcas_de_clase.calcular_intervalos(variable_aleatoria, k)
    marcas = marcas_de_clase.calcular(intervalos)

    return intervalos, marcas, variable_aleatoria, densidades, acumuladas


def simular(tasa, numeros, x_max):
    # Convertir a números uniformes y calcular el tiempo aleatorio
    variable_aleatoria = []

    for n in numeros:
        u = utils.convertir_en_probabilidad(n, max(numeros))
        x = (
            -math.log(1 - u) / tasa
        )  # Transformar números aleatorios a tiempos (x) usando la inversa
        if x > x_max or x in variable_aleatoria:
            continue
        variable_aleatoria.append(x)

    variable_aleatoria.sort()

    # Calcular las densidades de probabilidades
    intervalos, marcas, densidades, acumuladas = marcas_de_clase.calcular_densidades(variable_aleatoria)

    return intervalos, marcas, variable_aleatoria, densidades, acumuladas


def calcular_esperanza(tasa):
    return 1 / tasa


def calcular_varianza(tasa):
    return 1 / math.pow(tasa, 2)
