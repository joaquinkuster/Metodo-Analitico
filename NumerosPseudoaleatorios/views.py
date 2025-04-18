from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import TipoGenerador, VonNeumann, CongruencialMultiplicativo
from .forms import VonNeumannForm, CongruencialMultiplicativoForm
from django.views.decorators.http import require_POST

# Create your views here.


def index(request):
    return render(request, "index.html")


def generar_secuencia(request):
    # Inicializar ambos formularios
    von_neumann_form = VonNeumannForm()
    congruencial_form = CongruencialMultiplicativoForm()
    tipo = request.POST.get("tipo_generador") or None
    form = None

    # Procesar POST
    if request.method == "POST":
        if tipo == TipoGenerador.VON_NEUMANN:
            von_neumann_form = VonNeumannForm(request.POST)
            form = von_neumann_form
        elif tipo == TipoGenerador.CONGRUENCIAL_MULTIPLICATIVO:
            congruencial_form = CongruencialMultiplicativoForm(request.POST)
            form = congruencial_form

        if form.is_valid():
            try:
                # Guardar la secuencia (las validaciones están en el modelo)
                secuencia = form.save(commit=False)
                secuencia.save()
                messages.success(request, "Secuencia generada exitosamente!")
            except ValidationError as e:
                # para cada campo y cada error, lo añadimos al form
                for field, errs in e.message_dict.items():
                    for err in errs:
                        form.add_error(field, err)

    # Obtener todas las secuencias usando GeneradorBase
    secuencias = list(VonNeumann.objects.all()) + list(
        CongruencialMultiplicativo.objects.all()
    )
    secuencias.sort(key=lambda x: x.fecha_creacion, reverse=True)

    return render(
        request,
        "pages/secuencia/generar.html",
        {
            "von_neumann_form": von_neumann_form,
            "congruencial_form": congruencial_form,
            "tipo_generador": tipo,
            "secuencias": secuencias,
        },
    )


@require_POST
def eliminar_secuencia(request, id, tipo):
    secuencia = None

    if tipo == TipoGenerador.VON_NEUMANN:
        secuencia = VonNeumann.objects.get(id=id)
    elif tipo == TipoGenerador.CONGRUENCIAL_MULTIPLICATIVO:
        secuencia = CongruencialMultiplicativo.objects.get(id=id)

    if secuencia is None:
        messages.error(request, "No se encontró la secuencia a eliminar.")
        return redirect("secuencia:generar")

    secuencia.delete()
    messages.success(request, "Secuencia eliminada exitosamente.")
    return redirect("secuencia:generar")


def ver_secuencia(request, id, tipo):
    secuencia = None

    if tipo == TipoGenerador.VON_NEUMANN:
        secuencia = VonNeumann.objects.get(id=id)
    elif tipo == TipoGenerador.CONGRUENCIAL_MULTIPLICATIVO:
        secuencia = CongruencialMultiplicativo.objects.get(id=id)

    if secuencia is None:
        messages.error(request, "No se encontró la secuencia a eliminar.")
        return redirect("secuencia:generar")

    return render(
        request,
        "pages/secuencia/ver.html",
        {
            "secuencia": secuencia,
        },
    )
