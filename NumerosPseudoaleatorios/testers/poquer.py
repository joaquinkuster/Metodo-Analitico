from math import isclose
from scipy.stats import chi2
from collections import Counter
from .funcionesPoquer import unir_numeros_como_string, separar_en_bloques_de_5


# funcion para prueba de chi cuadrado
def chi_cuadrado_test(observadas, esperadas, significancia):
    # calculamos los grados de libertad (cantidad de categorias - 1)
    df = len(esperadas) - 1
    # calculamos el valor de chi cuadrado utilizando la formula 
    chi_value = sum((o - e)**2 / e for o, e in zip(observadas, esperadas) if e > 0)
    # calculamos el valor critico de chi cuadrado
    chi_crit = chi2.ppf(1 - float(significancia), df)
    # comprobamos si se acepta la hipotesis nula
    pasa = chi_value < chi_crit or isclose(chi_value, chi_crit)
    # de volvemos el valor del chi cuadrado, el valor critico, y un booleano que nos dice si se acepta o se rechaza H0
    return chi_value, chi_crit, pasa

#   Realiza la prueba de Poker a una lista de números pseudoaleatorios.
def test_poker(significancia, numeros: list[int]):

    # transformamos la lista de numeros a numeros de 5 cifras
    numeros = unir_numeros_como_string(numeros)
    numeros = separar_en_bloques_de_5(numeros)
    # Categorías de manos
    categorias = ["todos_diferentes", "un_par", "dos_pares", "tercia", "full", "quintilla"]

    # Probabilidades teóricas
    probabilidades = {
        "todos_diferentes": 0.3024,
        "un_par": 0.5040,
        "dos_pares": 0.1080,
        "tercia": 0.0720,
        "full": 0.0090,
        "quintilla": 0.0001,
    }
    
    # Frecuencias observadas
    observadas = {cat: 0 for cat in categorias}
    
    

    for numero in numeros:
        
        conteo = sorted(Counter(numero).values(), reverse=True)

        # Clasificación
        if conteo == [5]:
            observadas["quintilla"] += 1
        elif conteo == [3, 2]:
            observadas["full"] += 1
        elif conteo == [3, 1, 1]:
            observadas["tercia"] += 1
        elif conteo == [2, 2, 1]:
            observadas["dos_pares"] += 1
        elif conteo == [2, 1, 1, 1]:
            observadas["un_par"] += 1
        elif conteo == [1, 1, 1, 1, 1]:
            observadas["todos_diferentes"] += 1
            
    total = len(numeros)
    esperadas = [total * probabilidades[cat] for cat in categorias]
    obs_list = [observadas[cat] for cat in categorias]
    
    chi, crit, pasa = chi_cuadrado_test(obs_list, esperadas, significancia)

    return {
        "frecuencia_observada": {k: int(v) for k, v in observadas.items()},  # Asegurar que sean enteros
        "frecuencia_esperada": {k: round(v, 4) for k, v in zip(categorias, esperadas)},  # Redondear valores
        "valor_chi2": round(chi, 4),
        "valor_critico": round(crit, 4),
        "aprueba": bool(pasa)  # Asegurar que sea un booleano
    }