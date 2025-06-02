from scipy.stats import chi2

def test_chi_cuadrado(significancia: 0.05, numeros: list[int], cantidad_digitos):
    
    grupos = []

    for num in numeros:
        num_str = str(abs(num))  # convertir a string y evitar negativos
        for i in range(0, len(num_str) - cantidad_digitos + 1, cantidad_digitos):
            grupo = num_str[i:i + cantidad_digitos]
            grupos.append(int(grupo))
    
    n = len(grupos)
    min_valor = min(grupos)
    max_valor = max(grupos)
    rango = max_valor - min_valor or 1
    
    # Crear intervalos
    cantidad_intervalos = 10
    intervalos = [min_valor + i * rango / cantidad_intervalos for i in range(cantidad_intervalos + 1)]
    
    esperadas = [n / cantidad_intervalos] * cantidad_intervalos
    observadas = [0] * cantidad_intervalos

    # Contar cuántos valores caen en cada intervalo
    for valor in grupos:
        for i in range(cantidad_intervalos):
            if intervalos[i] <= valor < intervalos[i + 1] or (i == cantidad_intervalos - 1 and valor == intervalos[i + 1]):
                observadas[i] += 1
                break
            
    # Calcular el estadístico chi-cuadrado
    valor_chi2 = sum((o - e)**2 / e for o, e in zip(observadas, esperadas) if e > 0)

    # Grados de libertad = k - 1
    df = cantidad_intervalos - 1
    valor_critico = chi2.ppf(1 - float(significancia), df)
    
    # p-valor
    p_valor = 1 - chi2.cdf(valor_chi2, df)

    return {
        "estadistico_prueba": round(valor_chi2, 4), 
        "valor_critico": round(valor_critico, 4), 
        "pvalor": round(p_valor, 4),
        "aprobado": bool(valor_chi2 < valor_critico),
        "intervalos": [round(intervalos[i], 2) for i in range(cantidad_intervalos)],
        "frecuencias_observadas": observadas,
        "frecuencias_esperadas": esperadas
    }
