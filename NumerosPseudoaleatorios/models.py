from math import gcd
from django.db import models
from django.core.exceptions import ValidationError
from .services.generator import von_neumann, congruencial_multiplicativo
from .services.distribution import binomial, exponencial

# Valores válidos para p
VALORES_P_VALIDOS = [3, 11, 13, 19, 21, 27, 29, 37, 53, 59, 61, 67, 69, 77, 83, 91]


class TipoGenerador(models.TextChoices):
    CONGRUENCIAL_MULTIPLICATIVO = "CM", "Congruencial Multiplicativo"
    VON_NEUMANN = "VN", "Von Neumann"


class TipoTester(models.TextChoices):
    CHI_CUADRADO = "CC", "Chi-Cuadrado"
    POKER = "PK", "Poker"


class TipoDistribucion(models.TextChoices):
    BINOMIAL = "BI", "Binomial"
    EXPONENCIAL = "EXP", "Exponencial"


# Validador para la lista de números
def validar_numeros(numeros):
    if not isinstance(numeros, list) or not numeros:
        raise ValidationError("La lista de números no puede estar vacía.")
    for numero in numeros:
        if not isinstance(numero, (int, float)):
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


#  Validar probabilidad de éxito
def validar_probabilidad_exito(p):
    if not (0 < p < 1):
        raise ValidationError("La probabilidad p debe estar entre 0 y 1.")


# Validar cantidad de ensayos
def validar_ensayos(n):
    if n < 1:
        raise ValidationError("El número de ensayos n debe ser al menos 1.")


# Validar lambda
def validar_tasa(tasa):
    if tasa <= 0:
        raise ValidationError("La tasa λ debe ser mayor que 0.")


class SecuenciaBase(models.Model):
    tipo = models.CharField(
        max_length=2,
        choices=TipoGenerador.choices,
    )
    semilla = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField(validators=[validar_cantidad])
    numeros = models.JSONField(validators=[validar_numeros], default=list)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-fecha_creacion"]
    
    def __str__(self):
        return f"{self.numeros}"


class VonNeumann(SecuenciaBase):
    def validar_campos(self):
        errores = {}

        if not (1000 <= self.semilla <= 9999):
            errores["semilla"] = (
                "La semilla para Von Neumann debe tener exactamente 4 dígitos."
            )
        if str(self.semilla)[2:] == "00":
            errores["semilla"] = (
                "Los dos últimos dígitos de la semilla no pueden ser '00'."
            )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.tipo = TipoGenerador.VON_NEUMANN
        self.validar_campos()
        self.generar_numeros()
        super().save(*args, **kwargs)

    def generar_numeros(self):
        self.numeros = von_neumann.generar(self.semilla, self.cantidad)
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
            errores["semilla"] = (
                "La semilla y el módulo deben ser relativamente primos."
            )

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
            raise ValidationError("El multiplicador (a) debe ser un entero positivo (≠ 0).")

        # Validar modulo
        if self.modulo <= 0:
            errores["modulo"] = "El módulo debe ser un entero positivo (≠ 0)."
        if self.modulo <= self.semilla:
            errores["modulo"] = "El módulo debe ser mayor que la semilla."
        if self.modulo <= self.multiplicador:
            errores["modulo"] = (
                f"El módulo debe ser mayor que el multiplicador (a) = {self.multiplicador}."
            )
        if self.modulo == self.multiplicador + 1:
            errores["modulo"] = (
                f"El módulo no puede ser exactamente uno más que el multiplicador (a), es decir: {self.multiplicador + 1}."
            )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.tipo = TipoGenerador.CONGRUENCIAL_MULTIPLICATIVO
        self.validar_campos()
        self.generar_numeros()
        super().save(*args, **kwargs)

    def generar_numeros(self):
        self.numeros = congruencial_multiplicativo.generar(
            self.semilla, self.multiplicador, self.modulo, self.cantidad
        )
        validar_numeros(self.numeros)


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
            errores["estadistico_prueba"] = (
                "El estadístico de prueba no puede ser negativo."
            )

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
    intervalos = models.JSONField(default=list, validators=[validar_intervalos])

    def validar_campos(self):
        errores = {}

        if not (
            len(self.intervalos) == 10
            and all(isinstance(i, float) for i in self.intervalos)
        ):
            errores["intervalos"] = (
                "Debe haber exactamente 10 intervalos de tipo float."
            )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.tipo = TipoTester.CHI_CUADRADO
        self.validar_campos()
        super().save(*args, **kwargs)


class DistribucionBase(models.Model): 
    tipo = models.CharField(
        max_length=3,
        choices=TipoDistribucion.choices,
    )
    valores_x = models.JSONField(default=list, validators=[validar_numeros])
    valores_probabilidad = models.JSONField(
        default=list, validators=[validar_numeros]
    )  # Valores de la función de densidad
    valores_acumulados = models.JSONField(
        default=list, validators=[validar_numeros]
    )  # Valores de la función de distribución acumulada

    valores_x_simulados = models.JSONField(
        default=list, validators=[validar_numeros]
    )  # Valores simulados de X
    
    valores_probabilidad_simulados = models.JSONField(
        default=list, validators=[validar_numeros]
    )  # Valores simulados de la función de densidad

    valores_acumulados_simulados = models.JSONField(
        default=list, validators=[validar_numeros]
    )  # Valores simulados de la función de distribución acumulada

    esperanza = models.FloatField()
    varianza = models.FloatField()
    secuencia = models.ForeignKey(SecuenciaBase, on_delete=models.CASCADE, default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        pares = zip(self.valores_x, self.valores_probabilidad)
        return ", ".join(f"({x}, {y})" for x, y in pares)
    
class Binomial(DistribucionBase):
    p = models.FloatField(
        validators=[validar_probabilidad_exito]
    )  # Probabilidad de éxito
    n = models.PositiveIntegerField(validators=[validar_ensayos])  # Cantidad de ensayos

    def calcular_probabilidades(self):
        self.valores_x, self.valores_probabilidad, self.valores_acumulados = (
            binomial.calcular_probabilidades(self.p, self.n)
        )
        validar_numeros(self.valores_x)
        validar_numeros(self.valores_probabilidad)
        validar_numeros(self.valores_acumulados)
    
    def calcular_esperenza(self):
        self.esperanza = binomial.calcular_esperanza(self.p, self.n)
        if self.esperanza <= 0:
            raise ValidationError("La esperanza E(x) debe ser un número positivo (≠ 0).")
        
    def calcular_varianza(self):
        self.varianza = binomial.calcular_varianza(self.p, self.n)
        if self.varianza <= 0:
            raise ValidationError("La varianza V(x) debe ser un número positivo (≠ 0).")        
        
    def simular_binomial(self, numeros_aleatorios):
        self.valores_x_simulados, self.valores_acumulados_simulados, self.valores_probabilidad_simulados = binomial.simular_binomial(numeros_aleatorios, self.n, self.p)
        validar_numeros(self.valores_x_simulados)
        validar_numeros(self.valores_acumulados_simulados)
        validar_numeros(self.valores_probabilidad_simulados)

    def save(self, *args, **kwargs):
        self.tipo = TipoDistribucion.BINOMIAL
        self.calcular_probabilidades()
        self.simular_binomial(self.secuencia.numeros)
        self.calcular_esperenza()
        self.calcular_varianza()
        super().save(*args, **kwargs)

class Exponencial(DistribucionBase):
    tasa = models.FloatField(validators=[validar_tasa])  # Corresponde a λ
    
    def calcular_probabilidades(self):
        self.valores_x, self.valores_probabilidad, self.valores_acumulados = (
            exponencial.calcular_probabilidades(self.tasa)
        )
        validar_numeros(self.valores_x)
        validar_numeros(self.valores_probabilidad)
        validar_numeros(self.valores_acumulados)
    
    def calcular_exponencial_desde_datos(self, numeros_aleatorios):
        self.valores_x_simulados, self.valores_probabilidad_simulados, self.valores_acumulados_simulados = (
            exponencial.calcular_exponencial_desde_datos(numeros_aleatorios, self.tasa)
        )
        validar_numeros(self.valores_x_simulados)
        validar_numeros(self.valores_probabilidad_simulados)
        validar_numeros(self.valores_acumulados_simulados)

    def calcular_esperenza(self):
        self.esperanza = exponencial.calcular_esperanza(self.tasa)
        if self.esperanza <= 0:
            raise ValidationError("La esperanza E(x) debe ser un número positivo (≠ 0).")
        
    def calcular_varianza(self):
        self.varianza = exponencial.calcular_varianza(self.tasa)
        if self.varianza <= 0:
            raise ValidationError("La varianza V(x) debe ser un número positivo (≠ 0).")        
        
    def save(self, *args, **kwargs):
        self.tipo = TipoDistribucion.EXPONENCIAL
        self.calcular_probabilidades()
        self.calcular_exponencial_desde_datos(self.secuencia.numeros)
        self.calcular_esperenza()
        self.calcular_varianza()
        super().save(*args, **kwargs)
