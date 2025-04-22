from math import isclose
from scipy.stats import chi2
from collections import Counter
from .funcionesPoquer import unir_numeros_como_string, separar_en_bloques_de_5

# función para prueba de chi cuadrado
def chi_cuadrado_test(observadas, esperadas, significancia):
    # calculamos los grados de libertad (cantidad de categorías - 1)
    df = len(esperadas) - 1
    # calculamos el valor de chi cuadrado utilizando la fórmula 
    chi_value = sum((o - e)**2 / e for o, e in zip(observadas, esperadas) if e > 0)
    # calculamos el valor crítico de chi cuadrado
    chi_crit = chi2.ppf(1 - float(significancia), df)
    # comprobamos si se acepta la hipótesis nula
    pasa = chi_value < chi_crit or isclose(chi_value, chi_crit)
    # Calcular p-valor para interpretación estadística
    p_valor = 1 - chi2.cdf(chi_value, df)
    # Devolvemos el valor del chi cuadrado, el valor crítico y un booleano que nos dice si se acepta o se rechaza H0
    return chi_value, chi_crit, pasa, p_valor

# Realiza la prueba de Poker a una lista de números pseudoaleatorios.
def test_poker(significancia, numeros: list[int]):
    # Validación de entrada de datos
    if not numeros:
        return {"error": "La lista de números está vacía"}
    
    # QUITAR ESTA VALIDACIÓN o modificarla para aceptar los números que tienes
    # if not all(0 <= num < 1 for num in numeros):
    #    return {"error": "Los números deben estar en el intervalo [0,1)"}

    # Convertir números a cadena y normalizar para que estén en el rango adecuado
    # Primero encontrar el valor máximo para normalizar
    max_value = max(numeros) if numeros else 1
    
    # Convertir números a dígitos (cada número se convierte en sus dígitos)
    numeros_digitos = ''.join(str(num).zfill(5)[:5] for num in numeros)
    
    # Asegurar que podemos hacer grupos completos de 5
    num_completos = len(numeros_digitos) // 5 * 5
    numeros_digitos = numeros_digitos[:num_completos]
    grupos_poker = [numeros_digitos[i:i+5] for i in range(0, num_completos, 5)]
    
    # Categorías de manos
    categorias = ["todos_diferentes", "un_par", "dos_pares", "tercia", "full", "poker", "quintilla"]

    # Probabilidades teóricas corregidas
    probabilidades = {
        "todos_diferentes": 0.3024,
        "un_par": 0.5040,
        "dos_pares": 0.1080,
        "tercia": 0.0720,
        "full": 0.0090,
        "poker": 0.0045,
        "quintilla": 0.0001,
    }
    
    # Frecuencias observadas
    observadas = {cat: 0 for cat in categorias}
    
    for grupo in grupos_poker:
        conteo = sorted(Counter(grupo).values(), reverse=True)
        
        # Clasificación
        if conteo == [5]:
            observadas["quintilla"] += 1
        elif conteo == [4, 1]:
            observadas["poker"] += 1
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
            
    total = len(grupos_poker)
    esperadas = [total * probabilidades[cat] for cat in categorias]
    obs_list = [observadas[cat] for cat in categorias]
    
    # Evitar división por cero si hay categorías con frecuencia esperada 0
    if any(e == 0 for e in esperadas):
        return {
            "error": "Algunas categorías tienen frecuencia esperada 0. Intenta con más datos."
        }
    
    chi, crit, pasa, p_valor = chi_cuadrado_test(obs_list, esperadas, significancia)

    return {
        "frecuencia_observada": {k: int(v) for k, v in observadas.items()},
        "frecuencia_esperada": {k: round(v, 4) for k, v in zip(categorias, esperadas)},
        "valor_chi2": round(chi, 4),
        "valor_critico": round(crit, 4),
        "p_valor": round(p_valor, 4),
        "aprueba": bool(pasa),
        "grupos_analizados": total
    }
