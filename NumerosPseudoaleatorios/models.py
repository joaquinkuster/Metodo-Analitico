from math import gcd
from django.db import models
from django.core.exceptions import ValidationError
from .generadores import generadores

# Valores válidos para p
VALORES_P_VALIDOS = [3, 11, 13, 19, 21, 27, 29, 37, 53, 59, 61, 67, 69, 77, 83, 91]

class TipoGenerador(models.TextChoices):
    CONGRUENCIAL_MULTIPLICATIVO = 'CM', 'Congruencial Multiplicativo'
    VON_NEUMANN = 'VN', 'Von Neumann'
    
class TipoTester(models.TextChoices):
    CHI_CUADRADO = 'CC', 'Chi-Cuadrado'
    POKER = 'PK', 'Poker'

# Validador para la lista de números
def validar_numeros(numeros):
    if not isinstance(numeros, list) or not numeros:
        raise ValidationError("La lista de números no puede estar vacía.")
    for numero in numeros:
        if not isinstance(numero, (int)):
            raise ValidationError(f"El valor '{numero}' no es un número válido.")

# Validador para la cantidad
def validar_cantidad(cantidad):
     if not (1 <= cantidad <= 100): 
            raise ValidationError("La cantidad debe ser mayor a 0 y menor o igual a 100.")

# Validar significancia
def validar_significancia(significancia):
    if not (0 < significancia < 1):
        raise ValidationError("La significancia debe ser un número entre 0 y 1.")

# Validadores para ChiCuadrado
def validar_cantidad_digitos(valor):
    if valor not in [1, 2, 3]:
        raise ValidationError("La cantidad de dígitos debe ser 1, 2 o 3.")

def validar_intervalos(intervalos):
    if len(intervalos) != 10:
        raise ValidationError("Debe haber exactamente 10 intervalos.")
    if not all(isinstance(i, float) for i in intervalos):
        raise ValidationError("Todos los intervalos deben ser de tipo float.")


class SecuenciaBase(models.Model):
    tipo = models.CharField(
        max_length=2,
        choices=TipoGenerador.choices,
    )
    semilla = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField(validators=[validar_cantidad])
    numeros = models.JSONField(validators=[validar_numeros], default=list)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.numeros}"
    
class TesterBase(models.Model):
    tipo = models.CharField(
        max_length=2,
        choices=TipoTester.choices,
    )
    significancia = models.FloatField(validators=[validar_significancia])
    estadistico_prueba = models.FloatField()
    valor_critico = models.FloatField()
    aprobado = models.BooleanField()
    frecuencias_observadas = models.JSONField(validators=[validar_numeros], default=list)
    frecuencias_esperadas = models.JSONField(validators=[validar_numeros], default=list)
    secuencia = models.ForeignKey(SecuenciaBase, on_delete=models.CASCADE)
    pvalor = models.FloatField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def validar_campos(self):
        errores = {}

        if self.estadistico_prueba < 0:
            errores["estadistico_prueba"] = "El estadístico de prueba no puede ser negativo."

        if self.valor_critico <= 0:
            errores["valor_critico"] = "El valor crítico debe ser mayor a 0."

        if not (0 <= self.pvalor <= 1):
            errores["pvalor"] = "El p-valor debe estar entre 0 y 1."

        if errores:
            raise ValidationError(errores)
        
    def __str__(self):
        return f"{self.estadistico_prueba} <= {self.valor_critico}"

class ChiCuadrado(TesterBase):
    cantidad_digitos = models.PositiveIntegerField(default=1, validators=[validar_cantidad_digitos])
    intervalos = models.JSONField(
        default=list,   
        validators=[validar_intervalos]
    )

    def validar_campos(self):
        errores = {}
        
        if self.cantidad_digitos not in [1, 2, 3]:
            errores["cantidad_digitos"] = "La cantidad de dígitos debe ser 1, 2 o 3."
        
        if not (len(self.intervalos) == 10 and all(isinstance(i, float) for i in self.intervalos)):
            errores["intervalos"] = "Debe haber exactamente 10 intervalos de tipo float."
        
        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.tipo = TipoTester.CHI_CUADRADO
        self.validar_campos()
        super().save(*args, **kwargs)

class VonNeumann(SecuenciaBase):
    def validar_campos(self):
        errores = {}
        
        if not (1000 <= self.semilla <= 9999):
            errores["semilla"] = "La semilla para Von Neumann debe tener exactamente 4 dígitos."
        if str(self.semilla)[2:] == '00':
            errores["semilla"] = "Los dos últimos dígitos de la semilla no pueden ser '00'."
        
        if errores:
            raise ValidationError(errores)
                         
    def save(self, *args, **kwargs):
        self.tipo = TipoGenerador.VON_NEUMANN
        self.validar_campos()
        self.generar_numeros()
        super().save(*args, **kwargs)

    def generar_numeros(self):
        self.numeros = generadores.von_neumann(self.semilla, self.cantidad)
        validar_numeros(self.numeros)

class CongruencialMultiplicativo(SecuenciaBase):
    t = models.PositiveIntegerField()
    p = models.PositiveIntegerField()
    modulo = models.PositiveIntegerField()
    multiplicador = models.BigIntegerField(editable=False)

    def validar_campos(self):
        errores = {}
        
        if self.semilla <= 0:
            errores["semilla"] = "La semilla debe ser un entero positivo (≠ 0)."
        if self.semilla % 2 == 0:
            errores["semilla"] = "La semilla debe ser impar."
        if self.semilla % 5 == 0:
            errores["semilla"] = "La semilla no debe ser divisible por 5."
        if gcd(self.semilla, self.modulo) != 1:
            errores["semilla"] = "La semilla y el módulo deben ser relativamente primos."
                
        # Validar p
        if self.p <= 0:
            errores["p"] = "El valor de p debe ser un entero positivo (≠ 0)."
        if self.p not in VALORES_P_VALIDOS:
            errores["p"] = f"El valor de p debe ser uno de: {VALORES_P_VALIDOS}"
    
        # Validar t
        if self.t <= 0:
            errores["t"] = "El valor de t debe ser un entero positivo (≠ 0)."
        
        # Calcular multiplicador (a)
        self.multiplicador = 200 * self.t * self.p
        if self.multiplicador <= 0:
            errores["multiplicador"] = "El multiplicador (a) debe ser un entero positivo (≠ 0)."
        
        # Validar modulo
        if self.modulo <= 0:
            errores["modulo"] = "El módulo debe ser un entero positivo (≠ 0)."
        if self.modulo <= self.semilla:
            errores["modulo"] = "El módulo debe ser mayor que la semilla."
        if self.modulo <= self.multiplicador:
            errores["modulo"] = f"El módulo debe ser mayor que el multiplicador (a) = {self.multiplicador}."
        if self.modulo == self.multiplicador + 1:
            errores["modulo"] = f"El módulo no puede ser exactamente uno más que el multiplicador (a), es decir: {self.multiplicador + 1}."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.tipo = TipoGenerador.CONGRUENCIAL_MULTIPLICATIVO
        self.validar_campos()
        self.generar_numeros()
        super().save(*args, **kwargs)

    def generar_numeros(self):
        self.numeros = generadores.congruencial_multiplicativo(
            self.semilla,
            self.multiplicador,
            self.modulo,
            self.cantidad
        )
        validar_numeros(self.numeros)    
