from math import gcd
from django.db import models
from django.core.exceptions import ValidationError

# Valores válidos para p
VALORES_P_VALIDOS = [3, 11, 13, 19, 21, 27, 29, 37, 53, 59, 61, 67, 69, 77, 83, 91]

class TipoGenerador(models.TextChoices):
    CONGRUENCIAL_MULTIPLICATIVO = 'CM', 'Congruencial Multiplicativo'
    VON_NEUMANN = 'VN', 'Von Neumann'

# Validador para la lista de números
def validarNumeros(numeros):
    if not isinstance(numeros, list) or not numeros:
        raise ValidationError("La lista de números no puede estar vacía.")

# Validador para la cantidad
def validarCantidad(cantidad):
     if not (1 <= cantidad <= 100): 
            raise ValidationError("La cantidad debe ser mayor a 0 y menor o igual a 100.")

class SecuenciaPseudoaleatoria(models.Model):
    id = models.AutoField(primary_key=True)
    semilla = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField(validators=[validarCantidad])
    generador = models.CharField(
        max_length=2,
        choices=TipoGenerador.choices,
        default=TipoGenerador.CONGRUENCIAL_MULTIPLICATIVO,
    )
    
    # Campos para Método Congruencial Multiplicativo (opcionales para Von Neumann)
    t = models.PositiveIntegerField(null=True, blank=True)
    p = models.PositiveIntegerField(null=True, blank=True)
    modulo = models.PositiveIntegerField(null=True, blank=True)
    multiplicador = models.BigIntegerField(editable=False, null=True, blank=True)
    
    numeros = models.JSONField(validators=[validarNumeros])
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def validar_campos(self):
        # Validaciones para Von Neumann
        if self.generador == TipoGenerador.VON_NEUMANN:
            # No requieren t, p, modulo
            if not (1000 <= self.semilla <= 9999):
                raise ValidationError({
                    "semilla": "La semilla para Von Neumann debe tener exactamente 4 dígitos."
                })

        # Validaciones para Congruencial Multiplicativo
        elif self.generador == TipoGenerador.CONGRUENCIAL_MULTIPLICATIVO:
            # Campos requeridos
            if self.t is None or self.p is None or self.modulo is None:
                raise ValidationError({
                    "t": "El valor de t es obligatorio para el Congruencial Multiplicativo.",
                    "p": "El valor de p es obligatorio para el Congruencial Multiplicativo.",
                    "modulo": "El módulo es obligatorio para el Congruencial Multiplicativo."
                })

            # Semilla positiva
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
                    "modulo": "El módulo debe ser mayor que el multiplicador (a)."
                })

    def save(self, *args, **kwargs):
        # Ejecutar validaciones y calcular multiplicador
        self.validar_campos()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.generador.value} - Semilla: {self.semilla} - Cantidad: {self.cantidad}"