from .. import utils

def generar(semilla, a, m, n, li, ls):
    numeros = []
    Xn = semilla
    intentos = 0
    max_intentos = n * 10  # Para evitar bucles infinitos si el rango es muy restrictivo

    while len(numeros) < n and intentos < max_intentos:
        Xn = utils.normalizar(li, (a * Xn) % m, m, ls)
        if li <= Xn <= ls:
            numeros.append(Xn)
        intentos += 1

    return numeros