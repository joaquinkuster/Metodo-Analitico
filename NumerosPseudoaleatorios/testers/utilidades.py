# funcion para agarrar la lista de numeros generados y transformarlos en un array de 5 digitos cada uno
def unir_numeros_como_string(lista):
    return ''.join(str(num) for num in lista)

# funcion para crear una lista con valores de n digitos 
def separar_en_bloques_de_n_cantidades(s, cantidad_digitos):
    return [s[i:i+cantidad_digitos] for i in range(0, len(s), cantidad_digitos)]
