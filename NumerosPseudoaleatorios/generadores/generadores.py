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

    # comprobar que el número tenga 4 dígitos únicamente
    if len(str(semilla)) != 4:
        return "El número debe tener 4 dígitos únicamente"
    
    # elevar al cuadrado y convertir a string
    cuadrado = str(semilla ** 2)

    # rellenar con ceros a la izquierda hasta que tenga 8 caracteres
    while len(cuadrado) < 8:
        cuadrado = "0" + cuadrado

    # tomar las 4 cifras del medio
    nueva_semilla = int(cuadrado[2:6])  # Convertir a número entero

    # Agregar el nuevo_seed a la lista de números
    numeros.append(nueva_semilla)  

    # casos base
    if cantidad == 1:
        return numeros

    # llamada recursiva, pasando la lista 'numeros'
    return von_neumann(nueva_semilla, cantidad - 1, numeros)