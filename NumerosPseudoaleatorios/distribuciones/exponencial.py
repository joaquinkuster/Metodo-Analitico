import math

def calcular_probabilidades(tasa):
    valoresX = []
    valoresProbabilidad = []
    valoresAcumulados = []
    suma_acumulada = 0
    
    umbral = 0.99
    incremento = 0.1
    x = 0
    
    while suma_acumulada < umbral:
        valoresX.append(x)
        prob = tasa * math.exp(-tasa * x)
        valoresProbabilidad.append(prob)
        # suma_acumulada += prob
        # Lo podemos calcular así, sería equivalente, pero vamos a usar la fórmula de la cátedra
        suma_acumulada = 1 - math.exp(-tasa * x)
        valoresAcumulados.append(suma_acumulada)
        x += incremento

    return valoresX, valoresProbabilidad, valoresAcumulados

def calcular_esperanza(tasa):
    return 1 / tasa

def calcular_varianza(tasa):
    return 1 / math.pow(tasa, 2)
