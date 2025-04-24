from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import TipoGenerador, VonNeumann, CongruencialMultiplicativo, TesterBase
from .forms import VonNeumannForm, CongruencialMultiplicativoForm, TestNumerosForm
from django.views.decorators.http import require_POST
from .testers.poquer import test_poker
from .testers.chiCuadrado import chi_squared_test
from django.http import JsonResponse, HttpResponseNotAllowed

# Create your views here.


def index(request):
    return render(request, "index.html")

# Funciones para gestionar las secuencias 


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
        messages.error(request, "No se encontró la secuencia para visualizar.")
        return redirect("secuencia:generar")

    return render(
        request,
        "pages/secuencia/ver.html",
        {
            "secuencia": secuencia,
        },
    )


# Funciones para gestionar los tests

def generar_test(request):
    # Inicializar el formulario
    test_form = TestNumerosForm()
    form = None
    tests = []

    # Procesar POST
    if request.method == "POST":
        form = TestNumerosForm(request.POST)
        if form.is_valid():
            try:
                
                # realizamos el test pasando a la funcion de test de poker la secuencia
                # y la significancia
                secuencia = form.cleaned_data["secuencia"]
                significancia = form.cleaned_data["significancia"]
                tipo = form.cleaned_data["tipo"]
                if tipo == "PK":
                    resultados = test_poker(significancia, secuencia.numeros)
                elif tipo == "CC":
                    resultados = chi_squared_test(significancia, secuencia.numeros, num_intervals=10)
                else:
                    messages.error(request, "Tipo de prueba no válido.")
                    return HttpResponseNotAllowed(['POST'])
                
                test = TesterBase(
                    tipo=tipo,
                    significancia=significancia,
                    estadistico_prueba=resultados["estadistico_prueba"],
                    valor_critico=resultados["valor_critico"],
                    aprobado=resultados["aprobado"],
                    frecuencias_observadas=resultados["frecuencias_observadas"],
                    secuencia=secuencia,
                    pvalor=resultados["pvalor"],
                )
                
                test.validar_datos()  # Validar los datos del test antes de guardarlo
                test.save()
                
                messages.success(request, "Test generado exitosamente!")
            except ValidationError as e:
                # para cada campo y cada error, lo añadimos al form
                for field, errs in e.message_dict.items():
                    for err in errs:
                        form.add_error(field, err)
                
    # Obtener todos los tests usando GeneradorBase
    tests = list(TesterBase.objects.all())
    tests.sort(key=lambda x: x.fecha_creacion, reverse=True)

    return render(
        request,
        "pages/test/generar.html",
        {
            "test_form": test_form,
            "tests": tests,	
        },
    )

def eliminar_test(request, id):
    test = None

    test = TesterBase.objects.get(id=id)
    
    if test is None:
        messages.error(request, "No se encontró el test a eliminar.")
        return redirect("test:generar")
    
    test.delete()
    
    messages.success(request, "Test eliminado exitosamente.")
    return redirect("test:generar")

def ver_test(request, id):
    test = TesterBase.objects.get(id=id)

    if test is None:
        messages.error(request, "No se encontró el test para visualizar.")
        return redirect("test:generar")

    return render(
        request,
        "pages/test/ver.html",
        {
            "test": test
        },
    )

def testear_secuencia(request, id, tipo):
    # Obtener la secuencia según el tipo
    if tipo == TipoGenerador.VON_NEUMANN:
        secuencia = VonNeumann.objects.get(id=id)
    elif tipo == TipoGenerador.CONGRUENCIAL_MULTIPLICATIVO:
        secuencia = CongruencialMultiplicativo.objects.get(id=id)
    else:
        messages.error(request, "Tipo de secuencia no válido.")
        return redirect("secuencia:generar")

    # Crear el formulario con la secuencia preseleccionada
    test_form = TestNumerosForm(initial={
        "secuencia": secuencia.id
    })

    return render(
        request,
        "pages/test/generar.html",
        {
            "test_form": test_form,
            "tests": TesterBase.objects.all().order_by("-fecha_creacion"),
        },
    )
