from .. import utils

def generar(semilla, a, m, n):
    numeros = []
    Xn = semilla
    for _ in range(n):
        Xn = (a * Xn) % m
        numeros.append(Xn)
    return numeros
