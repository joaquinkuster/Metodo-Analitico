def separar_digitos(numeros):
    digitos = []
    for numero in numeros:
        for d in str(numero):
            if d.isdigit():
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

def convertir_en_probabilidad(x, max_valor):
    x = abs(float(x))
    x_normalizado = x / max_valor
    if x_normalizado >= 1:
        x_normalizado = 0.99999  # Evita u=1
    elif x_normalizado == 0:
        x_normalizado = 0.00001  # Evita u=0
    return x_normalizado

def normalizar(li, Xn, m, ls):
    return round(li + (Xn / m) * (ls - li), 2)