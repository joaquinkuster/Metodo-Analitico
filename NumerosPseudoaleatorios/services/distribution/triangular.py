import math
from .. import utils
from . import marcas_de_clase

def teorica(a, b, c):
    variable_aleatoria = []
    densidades = []
    acumuladas = []
    
    # Generar puntos x desde a hasta b con incrementos adecuados
    incremento = (b - a) / 100  # 100 puntos para una curva suave
    x = a
    
    while x <= b:
        variable_aleatoria.append(x)
        densidades.append(calcular_densidad(x, a, b, c))
        acumuladas.append(calcular_acumulada(x, a, b, c))
        x += incremento
    
    # Agrupar en intervalos
    k = marcas_de_clase.calcular_cantidad_intervalos(len(variable_aleatoria))
    intervalos = marcas_de_clase.calcular_intervalos(variable_aleatoria, k)
    marcas = marcas_de_clase.calcular(intervalos)
    
    return intervalos, marcas, variable_aleatoria, densidades, acumuladas


def simular(a, b, c, numeros, x_max):
    variable_aleatoria = []
    
    for n in numeros:
        u = utils.convertir_en_probabilidad(n, max(numeros))
        x = inversa(a, b, c, u)
        if x > x_max or x in variable_aleatoria:
            continue
        variable_aleatoria.append(x)
    
    variable_aleatoria.sort()
    
    # Calcular densidades simuladads
    intervalos, marcas, densidades, acumuladas = marcas_de_clase.calcular_densidades(variable_aleatoria)
    
    return intervalos, marcas, variable_aleatoria, densidades, acumuladas


def calcular_densidad(x, a, b, c):
    if x < a:
        return 0
    elif a <= x <= c:
        return 2 * (x - a) / ((b - a) * (c - a))
    elif c <= x <= b:
        return 2 * (b - x) / ((b - a) * (b - c))
    else:
        return 0


def calcular_acumulada(x, a, b, c):
    if x < a:
        return 0
    elif a <= x <= c:
        return (x - a)**2 / ((b - a) * (c - a))
    elif c <= x <= b:
        return 1 - (b - x)**2 / ((b - a) * (b - c))
    else:
        return 1


def inversa(a, b, c, u):
    # Función inversa para generar pesos aleatorios
    if u < (c - a)/(b - a):
        return a + math.sqrt(u * (b - a) * (c - a))
    else:
        return b - math.sqrt((1 - u) * (b - a) * (b - c))


def calcular_esperanza(a, b, c):
    return (a + b + c) / 3


def calcular_varianza(a, b, c):
    return (a**2 + b**2 + c**2 - a*b - a*c - b*c) / 18