import math

def separar_digitos(numeros):
    digitos = []
    for numero in numeros:
        numero_str = str(abs(int(numero)))  # Por si hay negativos o floats
        for d in numero_str:
            digitos.append(int(d))
    return digitos

def normalizar_numero(x):
    x = abs(int(x))  
    digitos = len(str(x))
    return x / (10 ** digitos)


def calcular_probabilidades(tasa):
    valores_x_simulacion = []
    valores_probabilidad = []
    valores_acumulados = []
    suma_acumulada = 0
    
    umbral = 0.99
    incremento = 0.1
    x = 0
    
    while suma_acumulada < umbral:
        valores_x_simulacion.append(x)
        prob = tasa * math.exp(-tasa * x)
        valores_probabilidad.append(prob)
        suma_acumulada = 1 - math.exp(-tasa * x)
        valores_acumulados.append(suma_acumulada)
        x += incremento

    return valores_x_simulacion, valores_probabilidad, valores_acumulados

def calcular_esperanza(tasa):
    return 1 / tasa

def calcular_varianza(tasa):
    return 1 / math.pow(tasa, 2)

def calcular_exponencial_desde_datos(numeros_aleatorios, tasa):
    # 1. Calcular x simulados usando la inversa
    valores_x_simulacion = []
    
    numeros_aleatorios = separar_digitos(numeros_aleatorios)
    
    for u in numeros_aleatorios:
        u = normalizar_numero(u)
        if u == 1:
            u = 0.99999
        x = -math.log(1 - u) / tasa
        valores_x_simulacion.append(x)

    # 2. Ordenar los x simulados para hacer bien la acumulada empírica
    valores_x_simulacion.sort()

    # 3. Calcular las probabilidades (frecuencias relativas)
    valores_probabilidad = [tasa * math.exp(-tasa * x) for x in valores_x_simulacion]

    # 4. Calcular la acumulada empírica (ECDF)
    n = len(valores_x_simulacion)
    valores_acumulados = [(i + 1) / n for i in range(n)]

    # 5. Redondear si querés cortar decimales
    x_redondeados = [round(x, 5) for x in valores_x_simulacion]
    prob_redondeadas = [round(p, 5) for p in valores_probabilidad]
    acum_redondeadas = [round(a, 5) for a in valores_acumulados]

    # 6. Debug
    print("frecuencia relativa (agrupada): ", prob_redondeadas)
    print("valores acumulados simulacion (agrupados): ", acum_redondeadas)
    print("valores x (agrupados): ", x_redondeados)

    return x_redondeados, prob_redondeadas, acum_redondeadas