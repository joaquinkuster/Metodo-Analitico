from django import forms
from .models import (
    VonNeumann,
    CongruencialMultiplicativo,
    VALORES_P_VALIDOS,
    SecuenciaBase,
    ChiCuadrado,
    Poker,
    Binomial,
    Exponencial,
    Triangular,
    Simulacion,
    Camion,
)


class VonNeumannForm(forms.ModelForm):
    # Campos ocultos en el formulario pero presentes para validación/errores
    numeros = forms.JSONField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = VonNeumann
        # Excluimos los no editables del Meta para que no Django los quite automáticamente
        exclude = ["numeros"]
        fields = [
            "semilla",
            "cantidad",
            "limite_inferior",
            "limite_superior",
            "numeros",
        ]
        widgets = {
            "semilla": forms.NumberInput(
                attrs={
                    "min": 1000,
                    "value": 3245,
                    "placeholder": "Semilla inicial",
                    "required": True,
                }
            ),
            "cantidad": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 10000,
                    "value": 25,
                    "placeholder": "Cantidad de números",
                    "required": True,
                }
            ),
            "limite_inferior": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 1000000000,
                    "step": 0.01,
                    "value": 1,
                    "placeholder": "Límite inferior",
                    "required": True,
                }
            ),
            "limite_superior": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 1000000000,
                    "step": 0.01,
                    "value": 1000000000,
                    "placeholder": "Límite superior",
                    "required": True,
                }
            ),
        }
        labels = {
            "semilla": "Semilla (4 dígitos)",
            "cantidad": "Cantidad (n)",
            "limite_inferior": "Límite inferior (Li)",
            "limite_superior": "Límite superior (Ls)",
        }


class CongruencialMultiplicativoForm(forms.ModelForm):
    # Campos ocultos en el formulario pero presentes para validación/errores
    multiplicador = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    numeros = forms.JSONField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = CongruencialMultiplicativo
        # Excluimos los no editables del Meta para que no Django los quite automáticamente
        exclude = ["multiplicador", "numeros"]
        fields = [
            "semilla",
            "cantidad",
            "limite_inferior",
            "limite_superior",
            "t",
            "p",
            "modulo",
        ]
        widgets = {
            "semilla": forms.NumberInput(
                attrs={
                    "min": 1,
                    "value": 3247,
                    "placeholder": "Semilla inicial",
                    "required": True,
                }
            ),
            "cantidad": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 10000,
                    "value": 25,
                    "placeholder": "Cantidad de números",
                    "required": True,
                }
            ),
            "limite_inferior": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 1000000000,
                    "step": 0.01,
                    "value": 1,
                    "placeholder": "Límite inferior",
                    "required": True,
                }
            ),
            "limite_superior": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 1000000000,
                    "step": 0.01,
                    "value": 1000000000,
                    "placeholder": "Límite superior",
                    "required": True,
                }
            ),
            "t": forms.NumberInput(
                attrs={
                    "min": 1,
                    "value": 89,
                    "placeholder": "Parámetro t",
                    "required": True,
                }
            ),
            "p": forms.Select(
                choices=[(x, x) for x in VALORES_P_VALIDOS],
                attrs={"placeholder": "Parámetro p"},
            ),
            "modulo": forms.NumberInput(
                attrs={
                    "min": 1,
                    "value": 1619803,
                    "placeholder": "Módulo",
                    "required": True,
                }
            ),
        }
        labels = {
            "semilla": "Semilla",
            "cantidad": "Cantidad (n)",
            "limite_inferior": "Límite inferior (Li)",
            "limite_superior": "Límite superior (Ls)",
            "t": "Parámetro t",
            "p": "Parámetro p",
            "modulo": "Módulo (m)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Usar los valores válidos del modelo para el campo p
        self.fields["p"].widget.choices = [(x, x) for x in VALORES_P_VALIDOS]
        self.fields["p"].initial = 91


class ChiCuadradoForm(forms.ModelForm):
    # Campos ocultos en el formulario pero presentes para validación/errores
    cantidad_intervalos = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    intervalos = forms.JSONField(widget=forms.HiddenInput(), required=False)

    frecuencias_observadas = forms.JSONField(widget=forms.HiddenInput(), required=False)
    frecuencias_esperadas = forms.JSONField(widget=forms.HiddenInput(), required=False)
    estadistico_prueba = forms.FloatField(widget=forms.HiddenInput(), required=False)
    grados_libertad = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    valor_critico = forms.FloatField(widget=forms.HiddenInput(), required=False)
    pvalor = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = ChiCuadrado
        exclude = [
            "cantidad_intervalos",
            "intervalos",
            "frecuencias_observadas",
            "frecuencias_esperadas",
            "estadistico_prueba",
            "grados_libertad",
            "valor_critico",
            "pvalor",
        ]
        fields = ["secuencia", "significancia"]
        widgets = {
            "secuencia": forms.Select(
                attrs={"placeholder": "Seleccione una secuencia", "required": True}
            ),
            "significancia": forms.NumberInput(
                attrs={
                    "min": 0.01,
                    "max": 0.1,
                    "step": 0.01,
                    "value": 0.05,
                    "required": True,
                    "placeholder": "Nivel de significancia",
                }
            ),
        }
        labels = {
            "secuencia": "Secuencia",
            "significancia": "Nivel de significancia (α)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["secuencia"].queryset = SecuenciaBase.objects.all()
        self.fields["secuencia"].empty_label = (
            "Seleccione una secuencia"  # Texto personalizado
        )


class PokerForm(forms.ModelForm):
    # Campos ocultos en el formulario pero presentes para validación/errores
    frecuencias_observadas = forms.JSONField(widget=forms.HiddenInput(), required=False)
    frecuencias_esperadas = forms.JSONField(widget=forms.HiddenInput(), required=False)
    estadistico_prueba = forms.FloatField(widget=forms.HiddenInput(), required=False)
    grados_libertad = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    valor_critico = forms.FloatField(widget=forms.HiddenInput(), required=False)
    pvalor = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Poker
        exclude = [
            "frecuencias_observadas",
            "frecuencias_esperadas",
            "estadistico_prueba",
            "grados_libertad",
            "valor_critico",
            "pvalor",
        ]
        fields = ["secuencia", "significancia"]
        widgets = {
            "secuencia": forms.Select(
                attrs={"placeholder": "Seleccione una secuencia", "required": True}
            ),
            "significancia": forms.NumberInput(
                attrs={
                    "min": 0.01,
                    "max": 0.1,
                    "step": 0.01,
                    "value": 0.05,
                    "required": True,
                    "placeholder": "Nivel de significancia",
                }
            ),
        }
        labels = {
            "secuencia": "Secuencia",
            "significancia": "Nivel de significancia (α)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["secuencia"].queryset = SecuenciaBase.objects.all()
        self.fields["secuencia"].empty_label = (
            "Seleccione una secuencia"  # Texto personalizado
        )


class BinomialForm(forms.ModelForm):
    # Campos ocultos en el formulario pero presentes para validación/errores
    variable_aleatoria = forms.JSONField(widget=forms.HiddenInput(), required=False)
    probabilidades = forms.JSONField(widget=forms.HiddenInput(), required=False)
    acumuladas = forms.JSONField(widget=forms.HiddenInput(), required=False)

    variable_aleatoria_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)
    probabilidades_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)
    acumuladas_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)

    esperanza = forms.FloatField(widget=forms.HiddenInput(), required=False)
    varianza = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Binomial
        exclude = [
            "variable_aleatoria",
            "probabilidades",
            "acumuladas",
            "variable_aleatoria_sim",
            "probabilidades_sim",
            "acumuladas_sim",
            "esperanza",
            "varianza",
        ]
        fields = ["secuencia", "p", "n"]
        widgets = {
            "secuencia": forms.Select(
                attrs={"placeholder": "Seleccione una secuencia", "required": True}
            ),
            "p": forms.NumberInput(
                attrs={
                    "min": 0,
                    "max": 1.0,
                    "step": 0.01,
                    "value": 0.5,
                    "placeholder": "Probabilidad de éxito",
                    "required": True,
                }
            ),
            "n": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 1000,
                    "value": 10,
                    "placeholder": "Cantidad de ensayos",
                    "required": True,
                }
            ),
        }
        labels = {
            "secuencia": "Secuencia",
            "p": "Probabilidad de éxito (p)",
            "n": "Cantidad de ensayos (n)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["secuencia"].queryset = SecuenciaBase.objects.all()
        self.fields["secuencia"].empty_label = (
            "Seleccione una secuencia"  # Texto personalizado
        )


class ExponencialForm(forms.ModelForm):
    # Campos ocultos en el formulario pero presentes para validación/errores
    intervalos = forms.JSONField(widget=forms.HiddenInput(), required=False)
    marcas_de_clase = forms.JSONField(widget=forms.HiddenInput(), required=False)
    variable_aleatoria = forms.JSONField(widget=forms.HiddenInput(), required=False)
    probabilidades = forms.JSONField(widget=forms.HiddenInput(), required=False)
    acumuladas = forms.JSONField(widget=forms.HiddenInput(), required=False)

    intervalos_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)
    marcas_de_clase_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)
    variable_aleatoria_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)
    probabilidades_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)
    acumuladas_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)

    esperanza = forms.FloatField(widget=forms.HiddenInput(), required=False)
    varianza = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Exponencial
        exclude = [
            "intervalos",
            "marcas_de_clase",
            "variable_aleatoria",
            "probabilidades",
            "acumuladas",
            "intervalos_sim",
            "marcas_de_clase_sim",
            "variable_aleatoria_sim",
            "probabilidades_sim",
            "acumuladas_sim",
            "esperanza",
            "varianza",
        ]
        fields = ["secuencia", "tasa"]
        widgets = {
            "secuencia": forms.Select(
                attrs={"placeholder": "Seleccione una secuencia", "required": True}
            ),
            "tasa": forms.NumberInput(
                attrs={
                    "min": 0.01,
                    "step": 0.01,
                    "value": 5,
                    "placeholder": "Tasa",
                    "required": True,
                }
            ),
        }
        labels = {
            "secuencia": "Secuencia",
            "tasa": "Tasa (λ)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["secuencia"].queryset = SecuenciaBase.objects.all()
        self.fields["secuencia"].empty_label = (
            "Seleccione una secuencia"  # Texto personalizado
        )


class TriangularForm(forms.ModelForm):
    # Campos ocultos para cálculos
    intervalos = forms.JSONField(widget=forms.HiddenInput(), required=False)
    marcas_de_clase = forms.JSONField(widget=forms.HiddenInput(), required=False)
    variable_aleatoria = forms.JSONField(widget=forms.HiddenInput(), required=False)
    probabilidades = forms.JSONField(widget=forms.HiddenInput(), required=False)
    acumuladas = forms.JSONField(widget=forms.HiddenInput(), required=False)

    intervalos_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)
    marcas_de_clase_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)
    variable_aleatoria_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)
    probabilidades_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)
    acumuladas_sim = forms.JSONField(widget=forms.HiddenInput(), required=False)

    esperanza = forms.FloatField(widget=forms.HiddenInput(), required=False)
    varianza = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Triangular
        exclude = [
            "intervalos",
            "marcas_de_clase",
            "variable_aleatoria",
            "probabilidades",
            "acumuladas",
            "intervalos_sim",
            "marcas_de_clase_sim",
            "variable_aleatoria_sim",
            "probabilidades_sim",
            "acumuladas_sim",
            "esperanza",
            "varianza",
        ]
        fields = ["secuencia", "a", "b", "c"]
        widgets = {
            "secuencia": forms.Select(
                attrs={"placeholder": "Seleccione una secuencia", "required": True}
            ),
            "a": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 2000,
                    "step": 1,
                    "value": 540,
                    "placeholder": "Peso mínimo",
                    "required": True,
                }
            ),
            "b": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 2000,
                    "step": 1,
                    "value": 860,
                    "placeholder": "Peso máximo",
                    "required": True,
                }
            ),
            "c": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 2000,
                    "step": 1,
                    "value": 700,
                    "placeholder": "Peso moda",
                    "required": True,
                }
            ),
        }
        labels = {
            "secuencia": "Secuencia",
            "a": "Peso mínimo (a)",
            "b": "Peso máximo (b)",
            "c": "Peso moda (c)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["secuencia"].queryset = SecuenciaBase.objects.all()
        self.fields["secuencia"].empty_label = "Seleccione una secuencia"


class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = ["capacidad_vacas", "costo_chofer_km", "consumo_lt_km"]
        widgets = {
            "capacidad_vacas": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 1000,
                    "step": 1,
                    "value": 25,
                    "placeholder": "Capacidad en vacas",
                    "required": True,
                }
            ),
            "costo_chofer_km": forms.NumberInput(
                attrs={
                    "min": 0.1,
                    "max": 10000,
                    "step": 0.1,
                    "value": 0.5,
                    "placeholder": "Costo chofer por km",
                    "required": True,
                }
            ),
            "consumo_lt_km": forms.NumberInput(
                attrs={
                    "min": 0.1,
                    "max": 200,
                    "step": 0.1,
                    "value": 20,
                    "placeholder": "Consumo",
                    "required": True,
                }
            ),
        }
        labels = {
            "capacidad_vacas": "Capacidad (vacas)",
            "costo_chofer_km": "Costo chofer ($/km)",
            "consumo_lt_km": "Consumo combustible (L/100km)",
        }


class SimulacionForm(forms.ModelForm):
    # Campos ocultos para resultados
    peso_total = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Simulacion
        exclude = ["peso_total"]
        fields = [
            "distancia",
            "precio_combustible",
            "porcentaje_ganancia",
            "triangular",
            "camiones",
        ]
        widgets = {
            "distancia": forms.NumberInput(
                attrs={
                    "min": 0.1,
                    "max": 100000,
                    "step": 0.1,
                    "value": 1500,
                    "placeholder": "Distancia recorrida",
                    "required": True,
                }
            ),
            "precio_combustible": forms.NumberInput(
                attrs={
                    "min": 0.01,
                    "max": 100000,
                    "step": 0.01,
                    "value": 1,
                    "placeholder": "Precio combustible",
                    "required": True,
                }
            ),
            "porcentaje_ganancia": forms.NumberInput(
                attrs={
                    "min": 0.01,
                    "max": 100,
                    "step": 0.01,
                    "value": 25,
                    "placeholder": "Porcentaje de ganancia",
                    "required": True,
                }
            ),
            "triangular": forms.Select(
                attrs={
                    "placeholder": "Seleccione distribución triangular",
                    "required": True,
                }
            ),
            "camiones": forms.SelectMultiple(
                attrs={"placeholder": "Seleccione camiones", "required": True}
            ),
        }
        labels = {
            "distancia": "Distancia (km)",
            "precio_combustible": "Precio combustible ($/L)",
            "porcentaje_ganancia": "Porcentaje de ganancia (%)",
            "triangular": "Distribución de pesos",
            "camiones": "Camiones disponibles",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["triangular"].queryset = Triangular.objects.all()
        self.fields["triangular"].empty_label = "Seleccione distribución"
        self.fields["camiones"].queryset = Camion.objects.all()
        self.fields["camiones"].empty_label = "Seleccione camiones"
