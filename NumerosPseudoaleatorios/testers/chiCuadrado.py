from scipy.stats import chi2
import numpy as np

def chi_squared_test(significancia, numeros: list[int], num_intervals=10):
    n = len(numeros)
    
    # Obtener el rango de los números
    min_valor = min(numeros)
    max_valor = max(numeros)
    rango = max_valor - min_valor
    
    # Crear intervalos
    intervalos = [min_valor + i * rango / num_intervals for i in range(num_intervals + 1)]
    
    esperadas = [n / num_intervals] * num_intervals
    observadas = [0] * num_intervals

    # Contar cuántos valores caen en cada intervalo
    for num in numeros:
        for i in range(num_intervals):
            if intervalos[i] <= num < intervalos[i+1] or (i == num_intervals-1 and num == intervalos[i+1]):
                observadas[i] += 1
                break

    # Calcular el estadístico chi-cuadrado
    chi_value = sum((o - e)**2 / e for o, e in zip(observadas, esperadas) if e > 0)

    # Grados de libertad = k - 1
    df = num_intervals - 1
    critical_value = chi2.ppf(1 - float(significancia), df)
    
    # p-valor
    p_valor = 1 - chi2.cdf(chi_value, df)

    return {
        "estadistico_prueba": round(chi_value, 4), 
        "valor_critico": round(critical_value, 4), 
        "pvalor": round(p_valor, 4),
        "aprobado": bool(chi_value < critical_value),
        "intervalos": [f"{round(intervalos[i], 2)}-{round(intervalos[i+1], 2)}" for i in range(num_intervals)],
        "frecuencias_observadas": observadas,
        "frecuencias_esperadas": esperadas
    }
