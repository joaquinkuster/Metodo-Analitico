# funcion para agarrar la lista de numeros generados y transformarlos en un array de 5 digitos cada uno
def unir_numeros_como_string(lista):
    return ''.join(str(num) for num in lista)

# funcion para crear una lista con valores de a 5    
def separar_en_bloques_de_5(s):
    return [s[i:i+5] for i in range(0, len(s), 5)]