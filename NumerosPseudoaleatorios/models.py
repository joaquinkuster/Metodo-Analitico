from math import gcd
import math
from django.db import models
from django.core.exceptions import ValidationError
from .services.generator import von_neumann, congruencial_multiplicativo
from .services.distribution import binomial, exponencial, triangular, marcas_de_clase
from .services.test import chi_cuadrado, poker
from django.utils.deconstruct import deconstructible
from django.db import transaction

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
    TRIANGULAR = "TR", "Triangular"


# Validadores para la lista de números, aleatoriedad, mínimos y rangos
def validar_numeros(numeros, campo):
    if not isinstance(numeros, list) or not numeros:
        raise ValidationError(
            {
                campo: f"La lista de números, frecuencias o probabilidades no puede estar vacía."
            }
        )
    for numero in numeros:
        if not isinstance(numero, (int, float)):
            raise ValidationError(
                {campo: f"El valor '{numero}' no es un número válido."}
            )


def validar_intervalos(intervalos, campo):
    if not (all(isinstance(li, float) and isinstance(ls, float) for li, ls in intervalos)):
        raise ValidationError({campo: "Los intervalos de tipo flotante."})


def validar_aleatoriedad(id):
    secuencia = SecuenciaBase.objects.get(id=id)

    if not secuencia:
        raise ValidationError("La secuencia seleccionada no existe.")

    if not secuencia.tests.exists():
        raise ValidationError(
            "No se hizo ningún test de aleatoriedad para la secuencia seleccionada."
        )

    if not any(test.aprobado for test in secuencia.tests.all()):
        raise ValidationError(
            "La secuencia seleccionada no es lo suficientemente aleatoria."
        )


@deconstructible
class ValidadorMinimo:
    def __init__(self, minimo, mensaje):
        self.minimo = minimo
        self.mensaje = mensaje

    def __call__(self, valor):
        if valor < self.minimo:
            raise ValidationError(self.mensaje)


@deconstructible
class ValidadorRango:
    def __init__(self, minimo, maximo, mensaje):
        self.minimo = minimo
        self.maximo = maximo
        self.mensaje = mensaje

    def __call__(self, valor):
        if not (self.minimo <= valor <= self.maximo):
            raise ValidationError(self.mensaje)


class SecuenciaBase(models.Model):
    tipo = models.CharField(
        max_length=2,
        choices=TipoGenerador.choices,
    )
    semilla = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField(
        validators=[
            ValidadorRango(
                1, 10000, "La cantidad debe ser mayor a 0 y menor o igual a 1.000."
            )
        ]
    )
    limite_inferior = models.FloatField(
        validators=[
            ValidadorRango(
                1, 1000000000, "El límite inferior debe estar entre 1 y 1 mil millón."
            )
        ]
    )
    limite_superior = models.FloatField(
        validators=[
            ValidadorRango(
                1, 1000000000, "El límite superior debe estar entre 1 y 1 mil millón."
            )
        ]
    )
    numeros = models.JSONField(default=list)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        str = f"[{self.id}] {self.get_tipo_display()} ({len(self.numeros)} números)"
        return str[:150]  # Trunca a 150 caracteres

    def save(self, *args, **kwargs):

        # Si es un nuevo registro
        if self._state.adding:
            self.set_tipo()
            self.validar_campos()
            self.generar_numeros()

        super().save(*args, **kwargs)

    def set_tipo(self):
        raise NotImplementedError("Implementar set_tipo() en la subclase.")

    def validar_campos(self):
        raise NotImplementedError("Implementar validar_campos() en la subclase.")

    def generar_numeros(self):
        raise NotImplementedError("Implementar generar_numeros() en la subclase.")


class VonNeumann(SecuenciaBase):
    def set_tipo(self):
        self.tipo = TipoGenerador.VON_NEUMANN

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

    def generar_numeros(self):
        self.numeros = von_neumann.generar(
            self.semilla,
            self.cantidad,
            self.limite_inferior,
            self.limite_superior,
        )
        validar_numeros(self.numeros, "numeros")


class CongruencialMultiplicativo(SecuenciaBase):
    t = models.PositiveIntegerField()
    p = models.PositiveIntegerField()
    modulo = models.PositiveIntegerField()
    multiplicador = models.BigIntegerField(editable=False)

    def set_tipo(self):
        self.tipo = TipoGenerador.CONGRUENCIAL_MULTIPLICATIVO

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
            errores["multiplicador"] = (
                "El multiplicador (a) debe ser un entero positivo (≠ 0)."
            )
        if gcd(self.multiplicador, self.modulo) != 1:
            errores["multiplicador"] = (
                "El multiplicador y el módulo deben ser relativamente primos. Por favor, cambie el módulo o los parámetros específicos."
            )

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

    def generar_numeros(self):
        self.numeros = congruencial_multiplicativo.generar(
            self.semilla,
            self.multiplicador,
            self.modulo,
            self.cantidad,
            self.limite_inferior,
            self.limite_superior,
        )
        validar_numeros(self.numeros, "numeros")


class TesterBase(models.Model):
    tipo = models.CharField(
        max_length=2,
        choices=TipoTester.choices,
    )
    significancia = models.FloatField(
        validators=[
            ValidadorRango(
                0.00001, 0.99999, "La significancia debe ser un número entre 0 y 1."
            )
        ]
    )
    frecuencias_observadas = models.JSONField(default=list)
    frecuencias_esperadas = models.JSONField(default=list)
    diferencia = models.JSONField(default=list)
    diferencia_cuadrado = models.JSONField(default=list)
    diferencia_cuadrado_fe = models.JSONField(default=list)
    estadistico_prueba = models.FloatField(editable=False)
    grados_libertad = models.PositiveIntegerField(editable=False)
    valor_critico = models.FloatField(editable=False)
    secuencia = models.ForeignKey(
        SecuenciaBase, related_name="tests", on_delete=models.CASCADE
    )
    aprobado = models.BooleanField(editable=False)
    pvalor = models.FloatField(editable=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.estadistico_prueba} < {self.valor_critico}"

    def save(self, *args, **kwargs):

        # Si es un nuevo registro
        if self._state.adding:
            self.set_tipo()
            self.validar_campos()
            self.testear_aleatoriedad()

        super().save(*args, **kwargs)

    def validar_campos(self):
        errores = {}

        if self.tipo == TipoTester.CHI_CUADRADO:

            self.cantidad_intervalos = marcas_de_clase.calcular_cantidad_intervalos(
                self.secuencia.cantidad
            )
            if self.cantidad_intervalos <= 0:
                raise ValidationError(
                    {
                        "cantidad_intervalos": "La cantidad de intervalos debe ser mayor a 0."
                    }
                )

            self.intervalos = marcas_de_clase.calcular_intervalos(
                self.secuencia.numeros, self.cantidad_intervalos
            )

            validar_intervalos(self.intervalos, "intervalos")

        self.frecuencias_observadas, self.frecuencias_esperadas = (
            self.calcular_frecuencias()
        )
        validar_numeros(self.frecuencias_observadas, "frecuencias_observadas")
        validar_numeros(self.frecuencias_esperadas, "frecuencias_esperadas")

        (
            self.diferencia,
            self.diferencia_cuadrado,
            self.diferencia_cuadrado_fe,
            self.estadistico_prueba,
        ) = chi_cuadrado.calcular_estadistico(
            self.frecuencias_observadas, self.frecuencias_esperadas
        )
        if self.estadistico_prueba < 0:
            raise ValidationError(
                {
                    "estadistico_prueba": "El estadístico de prueba no puede ser negativo."
                }
            )

        self.grados_libertad = chi_cuadrado.calcular_grados_libertad(
            len(self.frecuencias_esperadas)
        )
        if self.grados_libertad <= 0:
            raise ValidationError(
                {"grados_libertad": "Los grados de libertad deben ser mayor a 0."}
            )

        self.valor_critico = chi_cuadrado.calcular_valor_critico(
            self.grados_libertad, self.significancia
        )
        if self.valor_critico <= 0:
            raise ValidationError(
                {"valor_critico": "El valor crítico debe ser mayor a 0."}
            )

        self.pvalor = chi_cuadrado.calcular_pvalor(
            self.estadistico_prueba, self.grados_libertad
        )
        if not (0 <= self.pvalor <= 1):
            errores["pvalor"] = "El p-valor debe estar entre 0 y 1."

        if errores:
            raise ValidationError(errores)

    def testear_aleatoriedad(self):
        self.aprobado = chi_cuadrado.testear(
            self.estadistico_prueba, self.valor_critico
        )

    def set_tipo(self):
        raise NotImplementedError("Implementar set_tipo() en la subclase.")

    def calcular_frecuencias(self):
        raise NotImplementedError("Implementar calcular_frecuencias() en la subclase.")


class ChiCuadrado(TesterBase):
    intervalos = models.JSONField(default=list)
    cantidad_intervalos = models.PositiveIntegerField(editable=False)

    def set_tipo(self):
        self.tipo = TipoTester.CHI_CUADRADO

    def calcular_frecuencias(self):
        return chi_cuadrado.calcular_frecuencias(
            self.secuencia.numeros, self.intervalos
        )


class Poker(TesterBase):
    def set_tipo(self):
        self.tipo = TipoTester.POKER

    def calcular_frecuencias(self):
        return poker.calcular_frecuencias(self.secuencia.numeros)


class DistribucionBase(models.Model):
    tipo = models.CharField(
        max_length=3,
        choices=TipoDistribucion.choices,
    )
    variable_aleatoria = models.JSONField(default=list)
    probabilidades = models.JSONField(default=list)  # Valores de la función de densidad
    acumuladas = models.JSONField(
        default=list
    )  # Valores de la función de distribución acumulada

    variable_aleatoria_sim = models.JSONField(default=list)  # Valores simulados de X
    probabilidades_sim = models.JSONField(
        default=list
    )  # Valores simulados de la función de densidad
    acumuladas_sim = models.JSONField(
        default=list
    )  # Valores simulados de la función de distribución acumulada

    esperanza = models.FloatField(editable=False)
    varianza = models.FloatField(editable=False)
    secuencia = models.ForeignKey(
        SecuenciaBase,
        related_name="distribuciones",
        on_delete=models.CASCADE,
        validators=[validar_aleatoriedad],
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"[{self.id}] {self.get_tipo_display()} ({self.secuencia.cantidad} muestras)"

    def save(self, *args, **kwargs):

        # Si es un nuevo registro
        if self._state.adding:
            self.set_tipo()
            self.validar_parametros()
            self.distribucion_teorica()
            self.distribucion_simulada()
            self.calcular_estadisticos()

        super().save(*args, **kwargs)

    def set_tipo(self):
        raise NotImplementedError("Implementar set_tipo() en la subclase.")

    def validar_parametros(self):
        raise NotImplementedError("Implementar validar_parametros() en la subclase.")

    def distribucion_teorica(self):
        raise NotImplementedError("Implementar distribucion_teorica() en la subclase.")

    def distribucion_simulada(self):
        raise NotImplementedError("Implementar distribucion_simulada() en la subclase.")

    def calcular_teorica(self):
        raise NotImplementedError("Implementar calcular_teorica() en la subclase.")

    def calcular_simulada(self):
        raise NotImplementedError("Implementar calcular_simulada() en la subclase.")

    def calcular_estadisticos(self):
        errores = {}

        self.esperanza = self.calcular_esperanza()
        if self.esperanza <= 0:
            errores["esperanza"] = (
                "La esperanza E(x) debe ser un número positivo (≠ 0)."
            )

        self.varianza = self.calcular_varianza()
        if self.varianza <= 0:
            errores["varianza"] = "La varianza V(x) debe ser un número positivo (≠ 0)."

        if errores:
            raise ValidationError(errores)

    def calcular_esperanza(self):
        raise NotImplementedError("Implementar calcular_esperanza() en la subclase.")

    def calcular_varianza(self):
        raise NotImplementedError("Implementar calcular_varianza() en la subclase.")


class Discreta(DistribucionBase):

    def distribucion_teorica(self):

        self.variable_aleatoria, self.probabilidades, self.acumuladas = (
            self.calcular_teorica()
        )

        validar_numeros(self.variable_aleatoria, "variable_aleatoria")
        validar_numeros(self.probabilidades, "probabilidades")
        validar_numeros(self.acumuladas, "acumuladas")

    def distribucion_simulada(self):

        (
            self.variable_aleatoria_sim,
            self.probabilidades_sim,
            self.acumuladas_sim,
        ) = self.calcular_simulada()

        validar_numeros(self.variable_aleatoria_sim, "variable_aleatoria_sim")
        validar_numeros(self.probabilidades_sim, "probabilidades_sim")
        validar_numeros(self.acumuladas_sim, "acumuladas_sim")

    def set_tipo(self):
        raise NotImplementedError("Implementar set_tipo() en la subclase.")

    def validar_parametros(self):
        raise NotImplementedError("Implementar validar_parametros() en la subclase.")

    def calcular_teorica(self):
        raise NotImplementedError("Implementar calcular_teorica() en la subclase.")

    def calcular_simulada(self):
        raise NotImplementedError("Implementar calcular_simulada() en la subclase.")

    def calcular_esperanza(self):
        raise NotImplementedError("Implementar calcular_esperanza() en la subclase.")

    def calcular_varianza(self):
        raise NotImplementedError("Implementar calcular_varianza() en la subclase.")


class Continua(DistribucionBase):
    # Calculados internamente
    intervalos = models.JSONField(default=list)
    marcas_de_clase = models.JSONField(default=list)

    intervalos_sim = models.JSONField(default=list)
    marcas_de_clase_sim = models.JSONField(default=list)

    def agrupar_densidades(self):
        probabilidades = [0] * len(self.intervalos)
        acumuladas = [0] * len(self.intervalos)
        for i, x in enumerate(self.variable_aleatoria):
            for j, (li, ls) in enumerate(self.intervalos):
                if li <= x < ls:
                    probabilidades[j] += self.probabilidades[i]
                    acumuladas[j] = self.acumuladas[i]
                    break
        return probabilidades, acumuladas

    def distribucion_teorica(self):

        (
            self.intervalos,
            self.marcas_de_clase,
            self.variable_aleatoria,
            self.probabilidades,
            self.acumuladas,
        ) = self.calcular_teorica()

        validar_intervalos(self.intervalos, "intervalos")
        validar_numeros(self.marcas_de_clase, "marcas_de_clase")
        validar_numeros(self.variable_aleatoria, "variable_aleatoria")
        validar_numeros(self.probabilidades, "probabilidades")
        validar_numeros(self.acumuladas, "acumuladas")

    def distribucion_simulada(self):

        (
            self.intervalos_sim,
            self.marcas_de_clase_sim,
            self.variable_aleatoria_sim,
            self.probabilidades_sim,
            self.acumuladas_sim,
        ) = self.calcular_simulada()

        validar_intervalos(self.intervalos_sim, "intervalos_sim")
        validar_numeros(self.marcas_de_clase_sim, "marcas_de_clase_sim")
        validar_numeros(self.variable_aleatoria_sim, "variable_aleatoria_sim")
        validar_numeros(self.probabilidades_sim, "probabilidades_sim")
        validar_numeros(self.acumuladas_sim, "acumuladas_sim")

    def set_tipo(self):
        raise NotImplementedError("Implementar set_tipo() en la subclase.")

    def validar_parametros(self):
        raise NotImplementedError("Implementar validar_parametros() en la subclase.")

    def calcular_teorica(self):
        raise NotImplementedError("Implementar calcular_teorica() en la subclase.")

    def calcular_simulada(self):
        raise NotImplementedError("Implementar calcular_simulada() en la subclase.")

    def calcular_esperanza(self):
        raise NotImplementedError("Implementar calcular_esperanza() en la subclase.")

    def calcular_varianza(self):
        raise NotImplementedError("Implementar calcular_varianza() en la subclase.")


class Binomial(Discreta):
    p = models.FloatField(
        validators=[
            ValidadorRango(
                0.00001, 0.99999, "La probabilidad p debe estar entre 0 y 1."
            )
        ]
    )
    n = models.PositiveIntegerField(
        validators=[ValidadorMinimo(1, "El número de ensayos n debe ser al menos 1.")]
    )

    def set_tipo(self):
        self.tipo = TipoDistribucion.BINOMIAL

    def validar_parametros(self):
        return

    def calcular_teorica(self):
        return binomial.teorica(self.p, self.n)

    def calcular_simulada(self):
        return binomial.simular(self.p, self.n, self.secuencia.numeros)

    def calcular_esperanza(self):
        return binomial.calcular_esperanza(self.p, self.n)

    def calcular_varianza(self):
        return binomial.calcular_varianza(self.p, self.n)


class Exponencial(Continua):
    tasa = models.FloatField(
        validators=[ValidadorMinimo(0.00001, "La tasa λ debe ser mayor que 0.")]
    )

    def set_tipo(self):
        self.tipo = TipoDistribucion.EXPONENCIAL

    def validar_parametros(self):
        return

    def calcular_teorica(self):
        return exponencial.teorica(self.tasa)

    def calcular_simulada(self):
        return exponencial.simular(
            self.tasa, self.secuencia.numeros, max(self.variable_aleatoria)
        )

    def calcular_esperanza(self):
        return exponencial.calcular_esperanza(self.tasa)

    def calcular_varianza(self):
        return exponencial.calcular_varianza(self.tasa)


class Triangular(Continua):
    a = models.FloatField(
        validators=[
            ValidadorRango(1, 2000, "El peso mínimo debe estar entre 1 y 2000 kg.")
        ]
    )
    b = models.FloatField(
        validators=[
            ValidadorRango(1, 2000, "El peso máximo debe estar entre 1 y 2000 kg.")
        ]
    )
    c = models.FloatField(
        validators=[
            ValidadorRango(1, 2000, "El peso moda debe estar entre 1 y 2000 kg.")
        ]
    )

    def set_tipo(self):
        self.tipo = TipoDistribucion.TRIANGULAR

    def validar_parametros(self):
        if self.a >= self.b:
            raise ValidationError(
                {"a": "El peso mínimo 'a' debe ser menor que el peso máximo 'b'"}
            )
        if not (self.a <= self.c <= self.b):
            raise ValidationError({"c": "El peso moda 'c' debe estar entre 'a' y 'b'"})

    def calcular_teorica(self):
        return triangular.teorica(self.a, self.b, self.c)

    def calcular_simulada(self):
        return triangular.simular(
            self.a, self.b, self.c, self.secuencia.numeros, max(self.variable_aleatoria)
        )

    def calcular_esperanza(self):
        return triangular.calcular_esperanza(self.a, self.b, self.c)

    def calcular_varianza(self):
        return triangular.calcular_varianza(self.a, self.b, self.c)


class Camion(models.Model):
    capacidad_vacas = models.PositiveIntegerField(
        validators=[
            ValidadorRango(
                1, 1000, "La capacidad del camión debe ser entre 1 y 1000 vacas."
            )
        ]
    )
    costo_chofer_km = models.FloatField(
        validators=[
            ValidadorRango(
                0.1,
                10000,
                "El costo del chofer por km debe estar entre $0.1 y $10.000.",
            )
        ]
    )
    consumo_lt_km = models.FloatField(
        validators=[
            ValidadorRango(
                0.1,
                200,
                "El consumo de combustible debe estar entre 0.1 y 200 L/100km.",
            )
        ]
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Camión {self.id} - Capacidad: {self.capacidad_vacas}"

    def save(self, *args, **kwargs):

        # Si es un nuevo registro
        if self._state.adding:
            self.consumo_lt_km = self.consumo_lt_km / 100

        super().save(*args, **kwargs)


class Simulacion(models.Model):
    # Parámetros de entrada
    distancia = models.FloatField(
        validators=[
            ValidadorRango(0.1, 100000, "La distancia debe ser entre 0.1 y 100.000 km.")
        ]
    )
    precio_combustible = models.FloatField(
        validators=[
            ValidadorRango(
                0.01,
                100000,
                "El precio del combustible debe ser entre $0.01 y $100.000.",
            )
        ]
    )
    porcentaje_ganancia = models.FloatField(
        validators=[
            ValidadorRango(
                0.01,
                100.0,
                "El porcentaje de ganancia debe estar entre 0.01% y 100%.",
            )
        ],
    )
    triangular = models.ForeignKey(Triangular, on_delete=models.CASCADE)
    # Relación ManyToMany con Camion
    camiones = models.ManyToManyField(
        Camion, through="SimulacionCamion", related_name="simulaciones_camiones"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Calculados al momento de la simulación
    # costo_total_traslado = models.FloatField(editable=False)
    peso_total = models.FloatField(editable=False)
    camion_ideal = models.ForeignKey(
        Camion, on_delete=models.CASCADE, related_name="simulaciones", null=True
    )

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Simulación {self.id}"

    def save(self, *args, **kwargs):

        # Si es un nuevo registro
        if self._state.adding:

            # Calculemos el peso total de vacas
            self.peso_total = 0
            for peso in self.triangular.variable_aleatoria_sim:
                self.peso_total += peso

            self.porcentaje_ganancia /= 100

        super().save(*args, **kwargs)

    def determinar_camion_ideal(self):

        with transaction.atomic():
            mejor_camion = None
            menor_costo = float("inf")

            # Procesar cada camión y encontrar el ideal
            for camion in self.camiones.all():

                # Obtener la relación SimulacionCamion
                relacion = SimulacionCamion.objects.get(simulacion=self, camion=camion)

                # Buscar el camión con menor costo total
                if relacion.costo_traslado < menor_costo:
                    menor_costo = relacion.costo_traslado
                    mejor_camion = camion

            # Asignar el camión ideal
            self.camion_ideal = mejor_camion
            self.save(update_fields=["camion_ideal"])


class SimulacionCamion(models.Model):
    simulacion = models.ForeignKey(Simulacion, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)

    # Resultados de costos por camión
    cantidad_viajes = models.IntegerField(editable=False, default=0)
    costo_combustible = models.FloatField(editable=False, default=0)
    costo_choferes = models.FloatField(editable=False, default=0)
    costo_traslado = models.FloatField(editable=False, default=0)
    precio_por_kg = models.FloatField(editable=False, default=0)

    def save(self, *args, **kwargs):

        # Si es un nuevo registro
        if self._state.adding:

            # Número de viajes necesarios
            self.cantidad_viajes = math.ceil(
                self.simulacion.triangular.secuencia.cantidad
                / self.camion.capacidad_vacas
            )

            # Cálculo de combustible total (lt) y su costo
            litros_totales = (
                self.cantidad_viajes
                * self.camion.consumo_lt_km
                * self.simulacion.distancia
            )
            self.costo_combustible = litros_totales * self.simulacion.precio_combustible

            # Costo choferes
            self.costo_choferes = (
                self.cantidad_viajes
                * self.camion.costo_chofer_km
                * self.simulacion.distancia
            )

            # Costo total
            self.costo_traslado = self.costo_combustible + self.costo_choferes

            # Estimar peso total ganado
            self.precio_por_kg = (
                self.costo_traslado
                + (self.costo_traslado * self.simulacion.porcentaje_ganancia)
            ) / self.simulacion.peso_total

        super().save(*args, **kwargs)
