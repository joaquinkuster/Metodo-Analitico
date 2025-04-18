def congruencial_multiplicativo(semilla, a, m, n):
    numeros = []
    Xn = semilla
    for _ in range(n):
        Xn = (a * Xn) % m
        numeros.append(Xn)
    return numeros

def von_neumann(semilla, cantidad, numeros=None):
    if numeros is None:  
        numeros = []

    cuadrado = str(semilla ** 2).zfill(8)  # rellena con ceros a la izquierda hasta 8 caracteres

    nueva_semilla = cuadrado[2:6]  # toma las 4 cifras del medio

    # Sumar 13 si termina en '00'
    if nueva_semilla[2:] == '00':
        nueva_semilla = str(int(nueva_semilla) + 13).zfill(4)  # actualiza y vuelve a rellenar

    numeros.append(int(nueva_semilla))

    if cantidad == 1:
        return numeros

    return von_neumann(int(nueva_semilla), cantidad - 1, numeros)