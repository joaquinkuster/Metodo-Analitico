#  supongamos que la probabilidad de que un cliente nuevo guste de un producto es 0.8, y llegan 5 clientes nuevos a la tienda.
#  Queremos saber la probabilidad de que exactamente 4 de ellos les guste el producto.

import numpy as np
from scipy.stats import binom, chisquare

def verificar_distribucion_binomial():
    """
    Verifica si los datos provienen de una distribución binomial con parámetros n y p.
    
    Args:
        n (int): Número de ensayos.
        p (float): Probabilidad de éxito.
        datos (list or np.array): Datos observados.
    
    Returns:
        tuple: (bool, str) donde el booleano indica si se cumple la hipótesis nula
               y el string contiene el mensaje correspondiente.
    """
    n = 5
    p = 0.8
    np.random.seed(42)
    datos = np.random.binomial(n, p, 100) 
    
    # Frecuencia observada de cada posible valor (0 a n)
    valores_posibles = np.arange(n + 1)
    frecuencia_observada = np.array([np.sum(datos == k) for k in valores_posibles])

    # Probabilidades teóricas para cada valor según la binomial
    probabilidades_teoricas = binom.pmf(valores_posibles, n, p)

    # Frecuencia esperada = probabilidad teórica * tamaño muestra
    frecuencia_esperada = probabilidades_teoricas * len(datos)

    # Test Chi-cuadrado
    chi2_stat, p_valor = chisquare(f_obs=frecuencia_observada, f_exp=frecuencia_esperada)

    # Resultado
    if p_valor > 0.05:
        return True, "No se rechaza la hipótesis nula: los datos pueden venir de la distribución binomial especificada."
    else:
        return False, "Se rechaza la hipótesis nula: los datos probablemente no vienen de la distribución binomial especificada."
