from django import forms

class GeneradorForm(forms.Form):
    # Parámetros del Generador Congruencial
    semilla = forms.IntegerField(label="Semilla", min_value=0)
    a = forms.IntegerField(label="Multiplicador (a)", min_value=1)
    m = forms.IntegerField(label="Módulo (m)", min_value=1)
    
    # Cantidad de números a generar
    n = forms.IntegerField(label="Cantidad de Números", min_value=10, initial=1000)
