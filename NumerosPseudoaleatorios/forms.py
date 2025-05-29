from django import forms
from .models import (
    TesterBase,
    VonNeumann,
    CongruencialMultiplicativo,
    VALORES_P_VALIDOS,
    SecuenciaBase,
    ChiCuadrado,
    Binomial,
    Exponencial,
)

class VonNeumannForm(forms.ModelForm):
    class Meta:
        model = VonNeumann
        fields = ["semilla", "cantidad"]
        widgets = {
            "semilla": forms.NumberInput(
                attrs={
                    "min": 1000,
                    "max": 9999,
                    "placeholder": "Semilla inicial",
                    "required": True,
                }
            ),
            "cantidad": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 100,
                    "placeholder": "Cantidad de números",
                    "required": True,
                }
            ),
        }
        labels = {
            "semilla": "Semilla (4 dígitos)",
            "cantidad": "Cantidad (n)",
        }


class CongruencialMultiplicativoForm(forms.ModelForm):
    class Meta:
        model = CongruencialMultiplicativo
        fields = ["semilla", "cantidad", "t", "p", "modulo"]
        widgets = {
            "semilla": forms.NumberInput(
                attrs={"min": 1, "placeholder": "Semilla inicial", "required": True}
            ),
            "cantidad": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 100,
                    "placeholder": "Cantidad de números",
                    "required": True,
                }
            ),
            "t": forms.NumberInput(
                attrs={"min": 1, "placeholder": "Parámetro t", "required": True}
            ),
            "p": forms.Select(
                choices=[(x, x) for x in VALORES_P_VALIDOS],
                attrs={"placeholder": "Parámetro p"},
            ),
            "modulo": forms.NumberInput(
                attrs={"min": 1, "placeholder": "Módulo", "required": True}
            ),
        }
        labels = {
            "semilla": "Semilla inicial",
            "cantidad": "Cantidad (n)",
            "t": "Parámetro t",
            "p": "Parámetro p",
            "modulo": "Módulo (m)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Usar los valores válidos del modelo para el campo p
        self.fields["p"].widget.choices = [(x, x) for x in VALORES_P_VALIDOS]


class ChiCuadradoForm(forms.ModelForm):
    class Meta:
        model = ChiCuadrado
        fields = ["secuencia", "significancia", "cantidad_digitos"]
        widgets = {
            "secuencia": forms.Select(
                attrs={"placeholder": "Seleccioná secuencia", "required": True}
            ),
            "significancia": forms.NumberInput(
                attrs={
                    "min": 0.01,
                    "max": 0.1,
                    "step": 0.01,
                    "value": 0.05,
                    "required": True,
                    "placeholder": "Nivel de significancia"
                }
            ),
            "cantidad_digitos": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 3,
                    "step": 1,
                    "required": True,
                    "placeholder": "Cantidad de dígitos a agrupar"
                }
            ),
        }
        labels = {
            "secuencia": "Secuencia",
            "significancia": "Nivel de significancia (α)",
            "cantidad_digitos": "Cantidad de dígitos a agrupar (n)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["secuencia"].queryset = SecuenciaBase.objects.all()


class PokerForm(forms.ModelForm):
    class Meta:
        model = TesterBase  # Asigna diseño de formulario a TesterBase para Poker
        fields = ["secuencia", "significancia"]
        widgets = {
            "secuencia": forms.Select(
                attrs={"placeholder": "Seleccioná secuencia", "required": True}
            ),
            "significancia": forms.NumberInput(
                attrs={
                    "min": 0.01,
                    "max": 0.1,
                    "step": 0.01,
                    "value": 0.05,
                    "required": True,
                    "placeholder": "Nivel de significancia"
                }
            ),
        }
        labels = {
            "secuencia": "Secuencia",
            "significancia": "Nivel de significancia (α)",
        }

class BinomialForm(forms.ModelForm):
    class Meta:
        model = Binomial
        fields = ["secuencia", "p", "n"]
        widgets = {
            "secuencia": forms.Select(
                attrs={"placeholder": "Seleccioná secuencia", "required": True}
            ),
            "p": forms.NumberInput(
                attrs={
                    "min": 0,
                    "max": 1.0,
                    "step": 0.01,
                    "placeholder": "Probabilidad de éxito",
                    "required": True,
                }
            ),
            "n": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 1000,
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
        
class ExponencialForm(forms.ModelForm):
    class Meta:
        model = Exponencial
        fields = ["secuencia", "tasa"]
        widgets = {
            "secuencia": forms.Select(
                attrs={"placeholder": "Seleccioná secuencia", "required": True}
            ),
            "tasa": forms.NumberInput(
                attrs={
                    "min": 0.01,
                    "step": 0.01,
                    "placeholder": "Tasa",
                    "required": True,
                }
            ),
        }
        labels = {
            "secuencia": "Secuencia",
            "tasa": "Tasa (λ)",
        }