from math import gcd
from django.db import models
from django.core.exceptions import ValidationError
from .generadores import generadores

# Valores válidos para p
VALORES_P_VALIDOS = [3, 11, 13, 19, 21, 27, 29, 37, 53, 59, 61, 67, 69, 77, 83, 91]

class TipoGenerador(models.TextChoices):
    CONGRUENCIAL_MULTIPLICATIVO = 'CM', 'Congruencial Multiplicativo'
    VON_NEUMANN = 'VN', 'Von Neumann'

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

class SecuenciaBase(models.Model):
    id = models.IntegerField(primary_key=True)
    tipo = models.CharField(
        max_length=2,
        choices=TipoGenerador.choices,
    )
    semilla = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField(validators=[validar_cantidad])
    numeros = models.JSONField(validators=[validar_numeros], default=list)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        
    def __str__(self):
        return f"{self.numeros}"

class VonNeumann(SecuenciaBase):
    def validar_campos(self):
        if not (1000 <= self.semilla <= 9999):
                raise ValidationError({
                    "semilla": "La semilla para Von Neumann debe tener exactamente 4 dígitos."
                })
        if str(self.semilla)[2:] == '00':
            raise ValidationError({
                "semilla": "Los dos últimos dígitos de la semilla no pueden ser '00'."
            })
                 
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
        if self.semilla <= 0:
                raise ValidationError({
                    "semilla": "La semilla debe ser un entero positivo (≠ 0)."
                })
        if self.semilla % 2 == 0:
            raise ValidationError({
                "semilla": "La semilla debe ser impar."
            })
        if self.semilla % 5 == 0:
            raise ValidationError({
                "semilla": "La semilla no debe ser divisible por 5."
            })
        if gcd(self.semilla, self.modulo) != 1:
                raise ValidationError({
                    "semilla": "La semilla y el módulo deben ser relativamente primos."
                })
        # Validar p
        if self.p <= 0:
            raise ValidationError({
                "p": "El valor de p debe ser un entero positivo (≠ 0)."
            })
        if self.p not in VALORES_P_VALIDOS:
            raise ValidationError({
                "p": f"El valor de p debe ser uno de: {VALORES_P_VALIDOS}"
            })
        # Validar t
        if self.t <= 0:
            raise ValidationError({
                "t": "El valor de t debe ser un entero positivo (≠ 0)."
            })
        # Calcular multiplicador (a)
        self.multiplicador = 200 * self.t * self.p
        if self.multiplicador <= 0:
            raise ValidationError({
                "multiplicador": "El multiplicador (a) debe ser un entero positivo (≠ 0)."
            })
        # Validar modulo
        if self.modulo <= 0:
            raise ValidationError({
                "modulo": "El módulo debe ser un entero positivo (≠ 0)."
            })
        if self.modulo <= self.semilla:
            raise ValidationError({
                "modulo": "El módulo debe ser mayor que la semilla."
            })
        if self.modulo <= self.multiplicador:
            raise ValidationError({
                "modulo": f"El módulo debe ser mayor que el multiplicador (a) = {self.multiplicador}."
            })     
        if self.modulo == self.multiplicador + 1:
            raise ValidationError({
                "modulo": f"El módulo no puede ser exactamente uno más que el multiplicador (a), es decir: {self.multiplicador + 1}."
            })

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

    
