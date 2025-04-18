from django import forms
from .models import VonNeumann, CongruencialMultiplicativo, VALORES_P_VALIDOS

class VonNeumannForm(forms.ModelForm):
    class Meta:
        model = VonNeumann
        fields = ['semilla', 'cantidad']
        widgets = {
            'semilla': forms.NumberInput(attrs={
                'min': 1000,
                'max': 9999,
                'required': True
            }),
            'cantidad': forms.NumberInput(attrs={
                'min': 1,
                'max': 100,
                'required': True
            })
        }
        labels = {
            'semilla': 'Semilla inicial (4 dígitos)',
            'cantidad': 'Cantidad de números (n)'
        }

class CongruencialMultiplicativoForm(forms.ModelForm):
    class Meta:
        model = CongruencialMultiplicativo
        fields = ['semilla', 'cantidad', 't', 'p', 'modulo']
        widgets = {
            'semilla': forms.NumberInput(attrs={
                'min': 1,
                'required': True
            }),
            'cantidad': forms.NumberInput(attrs={
                'min': 1,
                'max': 100,
                'required': True
            }),
            't': forms.NumberInput(attrs={
                'min': 1,
                'required': True
            }),
            'p': forms.Select(choices=[(x, x) for x in VALORES_P_VALIDOS]),
            'modulo': forms.NumberInput(attrs={
                'min': 1,
                'required': True
            })
        }
        labels = {
            'semilla': 'Semilla inicial',
            'cantidad': 'Cantidad de números (n)',
            't': 'Parámetro t',
            'p': 'Parámetro p',
            'modulo': 'Módulo (m)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Usar los valores válidos del modelo para el campo p
        self.fields['p'].widget.choices = [(x, x) for x in VALORES_P_VALIDOS]