from collections import Counter
from .. import utils

# Funciones específicas para poker
def preparar_datos_poker(numeros):
    """Prepara los datos para la prueba de poker"""
    numeros = utils.separar_digitos(numeros)
    return utils.agrupar_por_digitos(numeros, 5)

def obtener_probabilidades_teoricas():
    """Devuelve las probabilidades teóricas para cada mano de poker"""
    return {
        "todos_diferentes": 0.3024,
        "un_par": 0.5040,
        "dos_pares": 0.1080,
        "tercia": 0.0720,
        "full": 0.0090,
        "poker": 0.0045,
        "quintilla": 0.0001,
    }

def clasificar_mano_poker(grupo):
    """Clasifica un grupo de 5 dígitos según las reglas de poker"""
    conteo = sorted(Counter(grupo).values(), reverse=True)
    
    if conteo == [5]: return "quintilla"
    elif conteo == [4, 1]: return "poker"
    elif conteo == [3, 2]: return "full"
    elif conteo == [3, 1, 1]: return "tercia"
    elif conteo == [2, 2, 1]: return "dos_pares"
    elif conteo == [2, 1, 1, 1]: return "un_par"
    elif conteo == [1, 1, 1, 1, 1]: return "todos_diferentes"
    return None

def calcular_frecuencias(grupos):
    grupos_poker = preparar_datos_poker(grupos)
    
    categorias = list(obtener_probabilidades_teoricas().keys())
    observadas_dicc = {cat: 0 for cat in categorias}
    
    for grupo in grupos_poker:
        mano = clasificar_mano_poker(list(str(grupo)))
        if mano:
            observadas_dicc[mano] += 1
    
    # Convertir a listas en el orden de las categorías
    observadas = [observadas_dicc[cat] for cat in categorias]       
    
    total = len(grupos_poker)
    esperadas = [total * prob for prob in obtener_probabilidades_teoricas().values()]
     
    return observadas, esperadas