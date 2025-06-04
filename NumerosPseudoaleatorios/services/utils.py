def separar_digitos(numeros):
    digitos = []
    for numero in numeros:
        for d in str(numero):
            digitos.append(int(d))
    return digitos

def agrupar_por_digitos(numeros, n):
    grupos = []
    for i in range(0, len(numeros), n):
        grupo = numeros[i:i + n]
        # Convertir lista de dígitos a número usando for anidado
        numero_str = ""
        for digito in grupo: 
            numero_str += str(digito)
        grupos.append(int(numero_str))
    return grupos