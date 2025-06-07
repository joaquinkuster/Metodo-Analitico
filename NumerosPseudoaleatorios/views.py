from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import (
    ChiCuadrado,
    TipoGenerador,
    VonNeumann,
    CongruencialMultiplicativo,
    SecuenciaBase,
    TesterBase,
    TipoTester,
    TipoDistribucion,
    DistribucionBase,
)
from .forms import (
    VonNeumannForm,
    CongruencialMultiplicativoForm,
    ChiCuadradoForm,
    PokerForm,
    BinomialForm,
    ExponencialForm,
)
from django.views.decorators.http import require_POST
from .services.test import poker
from .services import utils


def index(request):
    return render(request, "index.html")


# Funciones para gestionar las secuencias
def generar_secuencia(request):
    # Inicializar ambos formularios
    von_neumann_form = VonNeumannForm()
    congruencial_form = CongruencialMultiplicativoForm()
    tipo = request.POST.get("tipo_generador") or "VN"
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
    secuencias = list(SecuenciaBase.objects.all())

    return render(
        request,
        "pages/generador/index.html",
        {
            "von_neumann_form": von_neumann_form,
            "congruencial_form": congruencial_form,
            "tipo_generador": tipo,
            "secuencias": secuencias,
        },
    )

@require_POST
def eliminar_secuencia(request, id):
    secuencia = SecuenciaBase.objects.get(id=id)

    if secuencia is None:
        messages.error(request, "No se encontró la secuencia a eliminar.")
        return redirect("generador:index")

    secuencia.delete()
    messages.success(request, "Secuencia eliminada exitosamente.")
    return redirect("generador:index")


def ver_secuencia(request, id):
    secuencia = SecuenciaBase.objects.get(id=id)

    if secuencia is None:
        messages.error(request, "No se encontró la secuencia para visualizar.")
        return redirect("generador:index")
    
    total_digitos = len(utils.separar_digitos(secuencia.numeros))

    return render(
        request,
        "pages/generador/ver.html",
        {
            "total_digitos": total_digitos,
            "secuencia": secuencia,
        },
    )
    
@require_POST
def modificar_secuencia(request, id):
    secuencia = SecuenciaBase.objects.get(id=id)
        
    if secuencia is None:
        messages.error(request, "No se encontró la secuencia a modificar.")
        return redirect("generador:index")
    
    cantidad_digitos = request.POST.get('cantidad_digitos')
        
    try:
        secuencia.cantidad_digitos = int(cantidad_digitos)
        secuencia.save()
        messages.success(request, "Cantidad de dígitos actualizada exitosamente.")
        
    except Exception as e:
        messages.error(request, f"Error al modificar la secuencia: {str(e)}")
    
    return redirect("generador:ver", id)


# Funciones para gestionar los tests
def generar_test(request):
    # Inicializar ambos formularios
    id_secuencia = request.GET.get("id_secuencia") or None
    chi_cuadrado_form = ChiCuadradoForm(initial={"secuencia": id_secuencia})
    poker_form = PokerForm()
    tipo = request.POST.get("tipo_tester") or "CC"
    form = None

    # Procesar POST
    if request.method == "POST":
        if tipo == TipoTester.CHI_CUADRADO:
            chi_cuadrado_form = ChiCuadradoForm(request.POST)
            form = chi_cuadrado_form
        elif tipo == TipoTester.POKER:
            poker_form = PokerForm(request.POST)
            form = poker_form

        if form.is_valid():
            try:
                # Guardar el test (las validaciones están en el modelo)
                test = form.save(commit=False)
                test.save()
                messages.success(request, "Test de aleatoriedad generado exitosamente!")
            except ValidationError as e:
                # para cada campo y cada error, lo añadimos al form
                for field, errs in e.message_dict.items():
                    for err in errs:
                        form.add_error(field, err)

    # Obtener todos los tests usando TesterBase
    tests = list(TesterBase.objects.all())

    return render(
        request,
        "pages/test/index.html",
        {
            "chi_cuadrado_form": chi_cuadrado_form,
            "poker_form": poker_form,
            "tipo_tester": tipo,
            "tests": tests,
        },
    )

@require_POST
def eliminar_test(request, id):
    test = TesterBase.objects.get(id=id)

    if test is None:
        messages.error(request, "No se encontró el test a eliminar.")
        return redirect("test:generar")

    test.delete()
    messages.success(request, "Test de aleatoriedad eliminado exitosamente.")
    return redirect("test:generar")


def ver_test(request, id):
    test = TesterBase.objects.get(id=id)

    if test is None:
        messages.error(request, "No se encontró el test para visualizar.")
        return redirect("test:generar")
    
    categorias = None
    if test.tipo == TipoTester.CHI_CUADRADO:
        categorias = test.chicuadrado.intervalos
    else:
        categorias = list(poker.obtener_probabilidades_teoricas().keys())    
        
    # Preparar datos para la tabla de frecuencias
    categorias_con_frecuencias = zip(
        categorias,
        test.frecuencias_observadas,
        test.frecuencias_esperadas, 
        test.diferencia,
        test.diferencia_cuadrado,
        test.diferencia_cuadrado_fe,
    )
    
    return render(
        request,
        "pages/test/ver.html",
        {
            "test": test,
            "categorias_con_frecuencias": categorias_con_frecuencias,
        },
    )


def testear_secuencia(request, id):
    # Versión mejorada con manejo de errores
    secuencia = get_object_or_404(SecuenciaBase, id=id)
    return redirect(f'{reverse("test:generar")}?id_secuencia={secuencia.id}')

# Funciones para gestionar las distribuciones
def generar_distribucion(request):
    # Inicializar ambos formularios
    binomial_form = BinomialForm()
    exponencial_form = ExponencialForm()
    tipo = request.POST.get("tipo_distribucion") or "BI"
    form = None

    # Procesar POST
    if request.method == "POST":
        if tipo == TipoDistribucion.BINOMIAL:
            binomial_form = BinomialForm(request.POST)
            form = binomial_form
        elif tipo == TipoDistribucion.EXPONENCIAL:
            exponencial_form = ExponencialForm(request.POST)
            form = exponencial_form

        if form.is_valid():
            try:
                # Guardar la distribución (las validaciones están en el modelo)
                distribucion = form.save(commit=False)
                distribucion.save()
                messages.success(request, "Distribución generada exitosamente!")
            except ValidationError as e:
                # para cada campo y cada error, lo añadimos al form
                for field, errs in e.message_dict.items():
                    for err in errs:
                        form.add_error(field, err)

    # Obtener todas las distribuciones usando DistribucionBase
    distribuciones = list(DistribucionBase.objects.all())

    return render(
        request,
        "pages/distribucion/generar.html",
        {
            "binomial_form": binomial_form,
            "exponencial_form": exponencial_form,
            "tipo_distribucion": tipo,
            "distribuciones": distribuciones,
        },
    )


def ver_distribucion(request, id):
    # Obtenemos la distribución o devolvemos 404
    distribucion = DistribucionBase.objects.get(id=id)

    if distribucion is None:
        messages.error(request, "No se encontró la distribución para visualizar.")
        return redirect("distribucion:generar")

    # Renderizamos la plantilla de detalle
    return render(
        request,
        "pages/distribucion/ver.html",
        {
            "distribucion": distribucion,
        },
    )


def menu_ejemplos(request):
    # Renderizamos la plantilla de detalle
    return render(request, "pages/distribucion/ejemplos/menu.html")


def ejemplos_distribucion(request, distribucion):
    binomial_form = BinomialForm()
    exponencial_form = ExponencialForm()

    if distribucion is None:
        messages.error(request, "No se encontró la distribución para visualizar.")
        return redirect("distribucion:generar")
    if distribucion == "binomial":
        return render(
            request,
            "pages/distribucion/ejemplos/binomial.html",
            {"binomial_form": binomial_form},
        )
    elif distribucion == "exponencial":
        return render(
            request,
            "pages/distribucion/ejemplos/exponencial.html",
            {"exponencial_form": exponencial_form},
        )
