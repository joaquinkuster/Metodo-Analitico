from django import forms
from .models import TesterBase, VonNeumann, CongruencialMultiplicativo, VALORES_P_VALIDOS, SecuenciaBase, TipoTester


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

class TestNumerosForm(forms.ModelForm):
    cantidad_digitos = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=3,
        widget=forms.NumberInput(attrs={"placeholder": "Cantidad de dígitos", "id": "cantidad-digitos"}),
        label="Cantidad de dígitos",
    )
    class Meta:
        model = TesterBase
        fields = ["tipo", "secuencia", "significancia"]
        widgets = {
            "tipo": forms.Select(
                choices=[(x, x) for x in TipoTester],
                attrs={"placeholder": "Tipo de test", "id": "tipo-test"},
            ),
            "secuencia": forms.Select(
                choices=[(x.id, str(x)) for x in SecuenciaBase.objects.all()],
                attrs={"placeholder": "Secuencia a testear"},
            ),
            "significancia": forms.NumberInput(
                attrs={
                    "min": 0.01,
                    "max": 0.1,
                    "value": 0.05,
                    "required": True,
                }
            ),
        }
        labels = {
            "tipo": "Tipo de test",
            "secuencia": "Secuencia a testear",
            "significancia": "Nivel de significancia",
            "cantidad_digitos": "Cantidad de dígitos",
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        cantidad_digitos = cleaned_data.get("cantidad_digitos")

        if tipo == TipoTester.CHI_CUADRADO:
            if not cantidad_digitos:
                raise forms.ValidationError("Debe especificar la cantidad de dígitos para el test Chi-Cuadrado.")
        return cleaned_data