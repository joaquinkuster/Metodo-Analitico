import random
from .. import utils


def generar(semilla, cantidad, li, ls):
    numeros = []

    intentos = 0
    max_intentos = cantidad * 10

    while len(numeros) < cantidad and intentos < max_intentos:
        cuadrado = str(semilla**2).zfill(8)

        # Asegurarte de que el resultado tenga solo números
        nueva_semilla = "".join(filter(str.isdigit, cuadrado[2:6]))

        if nueva_semilla[2:] == "00":
            random_2dig = f"{random.randint(10,99)}"
            nueva_semilla = nueva_semilla[:2] + random_2dig

        # Normalización al rango deseado
        nuevo_num = utils.normalizar(
            li, int(nueva_semilla), 9999, ls
        )  # 9999 porque ese es el valor máx. de 4 dígitos

        numeros.append(nuevo_num)

        semilla = nuevo_num
        intentos += 1

    return numeros
