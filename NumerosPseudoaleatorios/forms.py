from django import forms
from .models import VonNeumann, CongruencialMultiplicativo, VALORES_P_VALIDOS, SecuenciaBase, TipoTester


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

class TestNumerosForm(forms.Form):
    tipo_test = forms.ChoiceField(
        choices=TipoTester.choices,
        widget=forms.RadioSelect,
        label="Tipo de prueba",
        required=True
    )
    
    secuencia = forms.ModelChoiceField(
        queryset=SecuenciaBase.objects.all(),
        label="Secuencia",
        required=True,
        help_text="Seleccione una secuencia existente de la base de datos"
    )
    
    significancia = forms.DecimalField(
        max_digits=5,
        decimal_places=4,
        min_value=0.001,
        max_value=0.1,
        initial=0.05,
        label="Nivel de significancia",
        required=True,
        help_text="Ingrese un nivel de significancia entre 0.001 y 0.1"
    )