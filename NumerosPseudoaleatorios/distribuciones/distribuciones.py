import numpy as np

def datos_binomial(ensayos, probabilidad, cantidad):
    valores = np.random.binomial(n=ensayos, p=probabilidad, size=cantidad)
    return valores.tolist()

def datos_exponencial(tasa_lambda, cantidad):
    if tasa_lambda <= 0:
        return []
    valores = np.random.exponential(scale=1/tasa_lambda, size=cantidad)
    return valores.tolist()