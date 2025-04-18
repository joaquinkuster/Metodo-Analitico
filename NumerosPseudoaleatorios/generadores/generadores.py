def generador_congruencial_multiplicativo(semilla, a, m, n):
    numeros = []
    Xn = semilla
    for _ in range(n):
        Xn = (a * Xn) % m
        numeros.append(Xn)
    return numeros

def generador_numeros_aleatorios_neumann(seed, cantidad):
    global numeros

    # comprobar que el número tenga 4 dígitos únicamente
    if len(seed) != 4:
        return "El número debe tener 4 dígitos únicamente"
    
    # elevar al cuadrado y convertir a string
    cuadrado = str(int(seed) ** 2)

    # rellenar con ceros a la izquierda hasta que tenga 8 caracteres
    while len(cuadrado) < 8:
        cuadrado = "0" + cuadrado

    # tomar las 4 cifras del medio
    nuevo_seed = cuadrado[2:6]
    
    if nuevo_seed.endswith("00") or nuevo_seed == "0000":
        
        return "semilla invalida"
    
    numeros.append(nuevo_seed)

    # casos base
    if cantidad == 1:
        return numeros
    if cantidad == 0:
        return

    # llamada recursiva
    return generador_numeros_aleatorios_neumann(nuevo_seed, cantidad - 1)