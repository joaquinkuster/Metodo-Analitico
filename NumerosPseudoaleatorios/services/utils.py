def separar_digitos(numeros):
    digitos = []
    for numero in numeros:
        for d in str(numero):
            digitos.append(int(d))
    return digitos