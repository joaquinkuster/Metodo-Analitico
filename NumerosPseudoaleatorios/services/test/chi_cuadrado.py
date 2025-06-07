from scipy.stats import chi2

def calcular_intervalos(grupos, cantidad_intervalos: int = 10):
    min_val = min(grupos)
    max_val = max(grupos)
    rango = max_val - min_val or 1  # Evita división por cero
    
    amplitud = rango / cantidad_intervalos
    limites = [min_val + i * amplitud for i in range(cantidad_intervalos + 1)]
    
    return [(limites[i], limites[i+1]) for i in range(cantidad_intervalos)]

def calcular_frecuencias(grupos, intervalos):
    n = len(grupos)
    cantidad_intervalos = len(intervalos)
    
    observadas = [0] * cantidad_intervalos
    for valor in grupos:
        for i, (li, ls) in enumerate(intervalos):
            if (li <= valor < ls) or (i == cantidad_intervalos - 1 and valor == ls):
                observadas[i] += 1
                break
    
    esperadas = [n / cantidad_intervalos] * cantidad_intervalos
    return observadas, esperadas

def calcular_estadistico(observadas, esperadas):
    dif = []
    dif_cuad = []
    dif_cuad_fe = []
    estadistico = 0

    for i, (fo, fe) in enumerate(zip(observadas, esperadas)): 
        if fe > 0:
            dif.append(fo - fe)  # Diferencia entre observado y esperado
            dif_cuad.append(dif[i] ** 2)  # Diferencia al cuadrado (^ no funciona en Python, usa **)
            dif_cuad_fe.append(dif_cuad[i] / fe)  # Diferencia cuadrática sobre fe
            estadistico += dif_cuad_fe[i]  # Suma al estadístico

    return dif, dif_cuad, dif_cuad_fe, estadistico

def calcular_grados_libertad(cantidad_intervalos: int = 10):
    return cantidad_intervalos - 1

def calcular_valor_critico(grados_libertad, significancia: float = 0.05):
    return chi2.ppf(1 - significancia, grados_libertad)

def calcular_pvalor(estadistico, grados_libertad):
    return 1 - chi2.cdf(estadistico, grados_libertad)

def testear(estadistico, valor_critico):    
    return estadistico < valor_critico