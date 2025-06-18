from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import (
    TipoGenerador,
    SecuenciaBase,
    TesterBase,
    TipoTester,
    TipoDistribucion,
    DistribucionBase,
    Simulacion,
    Camion,
    SimulacionCamion,
)
from .forms import (
    VonNeumannForm,
    CongruencialMultiplicativoForm,
    ChiCuadradoForm,
    PokerForm,
    BinomialForm,
    ExponencialForm,
    TriangularForm,
    SimulacionForm,
    CamionForm,
)
from django.views.decorators.http import require_POST
from .services.test import poker


# Funciones para gestionar las secuencias
def generar_secuencia(request):
    # Inicializar ambos formularios
    von_neumann_form = VonNeumannForm()
    congruencial_form = CongruencialMultiplicativoForm()
    tipo = (
        request.POST.get("tipo_generador") or request.GET.get("tipo_generador") or "VN"
    )
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
                return redirect("generador:ver", secuencia.id)
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
        return redirect("generador:generar")

    secuencia.delete()
    messages.success(request, "Secuencia eliminada exitosamente.")
    return redirect("generador:generar")


def ver_secuencia(request, id):
    secuencia = SecuenciaBase.objects.get(id=id)

    if secuencia is None:
        messages.error(request, "No se encontró la secuencia para visualizar.")
        return redirect("generador:generar")

    # total_digitos = len(utils.separar_digitos(secuencia.numeros))

    return render(
        request,
        "pages/generador/ver.html",
        {
            "secuencia": secuencia,
        },
    )


# Funciones para gestionar los tests
def generar_test(request):
    # Inicializar ambos formularios
    id_secuencia = request.GET.get("id_secuencia") or None
    chi_cuadrado_form = ChiCuadradoForm(initial={"secuencia": id_secuencia})
    poker_form = PokerForm()
    tipo = request.POST.get("tipo_tester") or request.GET.get("tipo_tester") or "CC"
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
                return redirect("test:ver", test.id)
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
        (
            poker.obtener_probabilidades_teoricas().values()
            if test.tipo == TipoTester.POKER
            else [None] * len(categorias)
        ),  # Para mostrar las probabilidades teóricas del poker
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
    id_secuencia = request.GET.get("id_secuencia") or None
    binomial_form = BinomialForm(initial={"secuencia": id_secuencia})
    exponencial_form = ExponencialForm()
    triangular_form = TriangularForm()
    tipo = (
        request.POST.get("tipo_distribucion")
        or request.GET.get("tipo_distribucion")
        or "BI"
    )
    form = None

    # Procesar POST
    if request.method == "POST":
        if tipo == TipoDistribucion.BINOMIAL:
            binomial_form = BinomialForm(request.POST)
            form = binomial_form
        elif tipo == TipoDistribucion.EXPONENCIAL:
            exponencial_form = ExponencialForm(request.POST)
            form = exponencial_form
        elif tipo == TipoDistribucion.TRIANGULAR:
            triangular_form = TriangularForm(request.POST)
            form = triangular_form

        if form.is_valid():
            try:
                # Guardar la distribución (las validaciones están en el modelo)
                distribucion = form.save(commit=False)
                distribucion.save()
                messages.success(request, "Distribución generada exitosamente!")
                return redirect("distribucion:ver", distribucion.id)
            except ValidationError as e:
                # para cada campo y cada error, lo añadimos al form
                for field, errs in e.message_dict.items():
                    for err in errs:
                        form.add_error(field, err)

    # Obtener todas las distribuciones usando DistribucionBase
    distribuciones = list(DistribucionBase.objects.all())

    return render(
        request,
        "pages/distribucion/index.html",
        {
            "binomial_form": binomial_form,
            "exponencial_form": exponencial_form,
            "triangular_form": triangular_form,
            "tipo_distribucion": tipo,
            "distribuciones": distribuciones,
        },
    )


@require_POST
def eliminar_distribucion(request, id):
    distribucion = DistribucionBase.objects.get(id=id)

    if distribucion is None:
        messages.error(request, "No se encontró la distribución a eliminar.")
        return redirect("distribucion:generar")

    distribucion.delete()
    messages.success(request, "Distribución eliminada exitosamente.")
    return redirect("distribucion:generar")


def ver_distribucion(request, id):
    # Obtenemos la distribución o devolvemos 404
    distribucion = DistribucionBase.objects.get(id=id)

    if distribucion is None:
        messages.error(request, "No se encontró la distribución para visualizar.")
        return redirect("distribucion:generar")

    # Armamos las categorías con sus probabilidades
    if distribucion.tipo != TipoDistribucion.BINOMIAL:
        categorias = distribucion.continua.intervalos
        categorias_sim = distribucion.continua.intervalos_sim
        marcas = distribucion.continua.marcas_de_clase
        marcas_sim = distribucion.continua.marcas_de_clase_sim
        probabilidades, acumuladas = distribucion.continua.agrupar_densidades()
    else:
        categorias = distribucion.variable_aleatoria
        categorias_sim = distribucion.variable_aleatoria_sim
        marcas = marcas_sim = (
            None  # o una lista del mismo largo si lo necesitas para la tabla
        )
        probabilidades = distribucion.probabilidades
        acumuladas = distribucion.acumuladas

    distribucion_probabilidades = zip(
        categorias,
        marcas if marcas else [None] * len(categorias),
        probabilidades,
        acumuladas,
    )

    distribucion_probabilidades_obs = zip(
        categorias_sim,
        marcas_sim if marcas_sim else [None] * len(categorias_sim),
        distribucion.probabilidades_sim,
        distribucion.acumuladas_sim,
    )

    # Renderizamos la plantilla
    return render(
        request,
        "pages/distribucion/ver.html",
        {
            "distribucion": distribucion,
            "distribucion_probabilidades": distribucion_probabilidades,
            "distribucion_probabilidades_obs": distribucion_probabilidades_obs,
        },
    )


def distribuir_secuencia(request, id):
    # Versión mejorada con manejo de errores
    secuencia = get_object_or_404(SecuenciaBase, id=id)
    return redirect(f'{reverse("distribucion:generar")}?id_secuencia={secuencia.id}')


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


# Funciones para gestionar los camiones
def guardar_camion(request):

    camion_form = CamionForm()

    if request.method == "POST":
        camion_form = CamionForm(request.POST)
        if camion_form.is_valid():
            try:
                # Guardar el camión (las validaciones están en el modelo)
                camion = camion_form.save(commit=False)
                camion.save()
                messages.success(request, "Camión agregado exitosamente!")
            except ValidationError as e:
                # para cada campo y cada error, lo añadimos al form
                # para cada campo y cada error, lo añadimos al form
                for field, errs in e.message_dict.items():
                    for err in errs:
                        camion_form.add_error(field, err)

    # Obtenemos los camiones
    camiones = list(Camion.objects.all())

    return render(
        request,
        "pages/simulacion/camion.html",
        {
            "camion_form": camion_form,
            "camiones": camiones,
        },
    )


@require_POST
def eliminar_camion(request, id):
    camion = Camion.objects.get(id=id)

    if camion is None:
        messages.error(request, "No se encontró el camión a eliminar.")
        return redirect("camion:guardar")

    camion.delete()
    messages.success(request, "Camión eliminado exitosamente.")
    return redirect("camion:guardar")


# Funciones para gestionar las simulaciones
def generar_simulacion(request):

    id_distribucion = request.GET.get("id_distribucion") or None
    simulacion_form = SimulacionForm(initial={"triangular": id_distribucion})

    # Procesar POST
    if request.method == "POST":

        simulacion_form = SimulacionForm(request.POST)

        if simulacion_form.is_valid():

            try:
                # Guardar la simulación (las validaciones están en el modelo)
                simulacion = simulacion_form.save(commit=False)
                simulacion.save()

                # Crear las relaciones intermedias
                for camion in simulacion_form.cleaned_data["camiones"]:
                    SimulacionCamion.objects.create(
                        simulacion=simulacion, camion=camion
                    )

                # Procesar camiones y determinar el ideal
                simulacion.determinar_camion_ideal()

                messages.success(request, "Simulación generada exitosamente!")
                return redirect("simulacion:ver", simulacion.id)
            except ValidationError as e:
                # para cada campo y cada error, lo añadimos al form
                for field, errs in e.message_dict.items():
                    for err in errs:
                        simulacion_form.add_error(field, err)

    # Obtener todas las simulaciones
    simulaciones = list(Simulacion.objects.all())

    return render(
        request,
        "pages/simulacion/index.html",
        {
            "simulacion_form": simulacion_form,
            "simulaciones": simulaciones,
        },
    )


@require_POST
def eliminar_simulacion(request, id):
    simulacion = Simulacion.objects.get(id=id)

    if simulacion is None:
        messages.error(request, "No se encontró la simulación a eliminar.")
        return redirect("simulacion:generar")

    simulacion.delete()
    messages.success(request, "Simulación eliminada exitosamente.")
    return redirect("simulacion:generar")


def ver_simulacion(request, id):
    simulacion = Simulacion.objects.get(id=id)

    if simulacion is None:
        messages.error(request, "No se encontró la simulación para visualizar.")
        return redirect("simulacion:generar")

    # Relaciones entre simulación y camiones
    relaciones = simulacion.simulacioncamion_set.all()

    # Armamos las categorías con sus probabilidades
    probabilidades, acumuladas = simulacion.triangular.agrupar_densidades()

    distribucion_probabilidades = zip(
        simulacion.triangular.intervalos,
        simulacion.triangular.continua.marcas_de_clase,
        probabilidades,
        acumuladas,
    )

    distribucion_probabilidades_obs = zip(
        simulacion.triangular.continua.intervalos_sim,
        simulacion.triangular.continua.marcas_de_clase_sim,
        simulacion.triangular.continua.probabilidades_sim,
        simulacion.triangular.continua.acumuladas_sim,
    )

    return render(
        request,
        "pages/simulacion/ver.html",
        {
            "simulacion": simulacion,
            "relaciones": relaciones,
            "distribucion_probabilidades": distribucion_probabilidades,
            "distribucion_probabilidades_obs": distribucion_probabilidades_obs,
        },
    )


def simular_distribucion(request, id):
    # Versión mejorada con manejo de errores
    distribucion = get_object_or_404(DistribucionBase, id=id)
    return redirect(
        f'{reverse("simulacion:generar")}?id_distribucion={distribucion.id}'
    )
