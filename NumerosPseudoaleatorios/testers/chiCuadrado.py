from scipy.stats import chi2
import numpy as np

def chi_squared_test(significancia, numeros: list[int], num_intervals=10):
    n = len(numeros)
    esperadas = [n / num_intervals] * num_intervals
    observadas = [0] * num_intervals

    # Contar cuántos valores caen en cada intervalo
    for num in numeros:
        index = min(int(num * num_intervals), num_intervals - 1)
        observadas[index] += 1

    # Calcular el estadístico chi-cuadrado
    chi_value = sum((o - e)**2 / e for o, e in zip(observadas, esperadas) if e > 0)

    # Grados de libertad = k - 1
    df = num_intervals - 1
    critical_value = chi2.ppf(1 - float(significancia), df)

    return {
        
        "valor_chi2": round(chi_value), 
        "valor_critico": round(critical_value), 
        "aprueba": bool(chi_value < critical_value)
    }
