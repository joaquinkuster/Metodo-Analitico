from .. import utils

def generar(semilla, cantidad, numeros=None):
    if numeros is None:  
        numeros = []

    cuadrado = str(semilla ** 2).zfill(8)  # rellena con ceros a la izquierda hasta 8 caracteres

    nueva_semilla = cuadrado[2:6]  # toma las 4 cifras del medio

    # agregamos '13' si termina en '00'
    if nueva_semilla[2:] == '00':
        nueva_semilla = nueva_semilla[:2] + "13"

    numeros.append(int(nueva_semilla))

    if cantidad == 1:
        return numeros

    return generar(int(nueva_semilla), cantidad - 1, numeros)