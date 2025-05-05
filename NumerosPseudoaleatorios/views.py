from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import (
    ChiCuadrado,
    TipoGenerador,
    VonNeumann,
    CongruencialMultiplicativo,
    TesterBase,
    TipoDistribucion,
    DistribucionBase
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
from .testers.poquer import test_poker
from .testers.chiCuadrado import test_chi_cuadrado

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

    # Calcular el número total de dígitos en la secuencia
    total_digitos = 0
    for numero in secuencia.numeros:
        # Contamos los dígitos de cada número (abs para manejar negativos)
        total_digitos += len(str(abs(numero)))
        # Si el número es negativo, contamos un dígito extra para el signo
        if numero < 0:
            total_digitos += 1

    # Procesar el parámetro de agrupación
    numeros_agrupados = None
    agrupar = request.GET.get("agrupar")

    if agrupar:
        try:
            agrupar = int(agrupar)
            if agrupar > 0:
                # Extraer todos los dígitos de los números generados
                todos_digitos = []
                for numero in secuencia.numeros:
                    # Convertir el número a cadena y obtener sus dígitos
                    digitos = [int(d) for d in str(abs(numero))]
                    # Si el número es negativo, añadimos un signo - como un elemento separado
                    if numero < 0:
                        todos_digitos.append("-")
                    todos_digitos.extend(digitos)

                # Agrupar los dígitos según el valor de 'agrupar'
                grupos = []
                for i in range(0, len(todos_digitos), agrupar):
                    grupo = todos_digitos[i : i + agrupar]
                    # Manejar el signo negativo si está presente en un grupo
                    if "-" in grupo:
                        grupo_str = ",".join(
                            [str(d) if d != "-" else "-" for d in grupo]
                        )
                    else:
                        grupo_str = ",".join(map(str, grupo))
                    grupos.append(f"[{grupo_str}]")

                numeros_agrupados = " ".join(grupos)
        except (ValueError, TypeError):
            messages.error(
                request, "El valor de agrupación debe ser un entero positivo."
            )

    return render(
        request,
        "pages/secuencia/ver.html",
        {
            "secuencia": secuencia,
            "numeros_agrupados": numeros_agrupados,
            "total_digitos": total_digitos,  # Pasamos el total de dígitos a la plantilla
        },
    )


# Funciones para gestionar los tests


def generar_test(request):
    # Inicializar el formulario
    test_form = PokerForm(initial={"tipo": "PK"})

    form = None
    tests = []

    # Procesar POST
    if request.method == "POST":
        form = PokerForm(request.POST)
        if form.is_valid():
            try:

                # realizamos el test pasando a la funcion de test de poker la secuencia
                # y la significancia
                # Si no es instancia, lo buscamos manualmente
                secuencia = form.cleaned_data["secuencia"]
                significancia = form.cleaned_data["significancia"]
                tipo = form.cleaned_data["tipo"]
                if tipo == "PK":
                    resultados = test_poker(significancia, secuencia.numeros)
                    test = TesterBase(
                        tipo=tipo,
                        significancia=significancia,
                        estadistico_prueba=resultados["estadistico_prueba"],
                        valor_critico=resultados["valor_critico"],
                        aprobado=resultados["aprobado"],
                        frecuencias_observadas=resultados["frecuencias_observadas"],
                        frecuencias_esperadas=resultados["frecuencias_esperadas"],
                        secuencia=secuencia,
                        pvalor=resultados["pvalor"],
                    )
                elif tipo == "CC":
                    cantidad_digitos = form.cleaned_data["cantidad_digitos"]
                    resultados = test_chi_cuadrado(
                        significancia, secuencia.numeros, cantidad_digitos
                    )
                    test = ChiCuadrado(
                        tipo=tipo,
                        significancia=significancia,
                        estadistico_prueba=resultados["estadistico_prueba"],
                        valor_critico=resultados["valor_critico"],
                        aprobado=resultados["aprobado"],
                        frecuencias_observadas=resultados["frecuencias_observadas"],
                        frecuencias_esperadas=resultados["frecuencias_esperadas"],
                        secuencia=secuencia,
                        pvalor=resultados["pvalor"],
                        cantidad_digitos=cantidad_digitos,
                        intervalos=resultados["intervalos"],
                    )
                else:
                    messages.error(request, "Tipo de prueba no válido.")
                    return HttpResponseNotAllowed(["POST"])

                test.validar_datos()
                print(test.save())
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


def ver_test(request, id, tipo):

    if tipo == "PK":
        test = TesterBase.objects.get(id=id)
    elif tipo == "CC":
        test = ChiCuadrado.objects.get(id=id)
    else:
        if test is None:
            messages.error(request, "No se encontró el test para visualizar.")
        return redirect("test:generar")

    if test.tipo == "PK":
        categorias = [
            "Todos diferentes",
            "Un par",
            "Dos pares",
            "Tercia",
            "Full",
            "Poker",
            "Quintilla",
        ]
        observadas = list(test.frecuencias_observadas.values())
        esperadas = list(test.frecuencias_esperadas.values())
    elif test.tipo == "CC":
        categorias = [
            [round(test.intervalos[i], 2), round(test.intervalos[i + 1], 2)]
            for i in range(len(test.intervalos) - 1)
        ]
        observadas = test.frecuencias_observadas
        esperadas = test.frecuencias_esperadas

    frecuencias = [
        {
            "fo": fo,  # Convertir fo a float
            "fe": float(fe),  # Convertir fe a float
            "diferencia": (float(fo) - float(fe)),
            "cuadrado_diferencia": (float(fo) - float(fe)) ** 2,
            "cuadrado_diferencia_fe": (
                ((float(fo) - float(fe)) ** 2) / float(fe) if float(fe) != 0 else None
            ),  # Guardar la categoría como string
            "cat": cat,
        }
        for cat, fo, fe in zip(categorias, observadas, esperadas)
    ]
    return render(
        request,
        "pages/test/ver.html",
        {"test": test, "frecuencias": frecuencias, "categorias": categorias},
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
    test_form = PokerForm(initial={"tipo": "PK", "secuencia": secuencia.id})

    return render(
        request,
        "pages/test/generar.html",
        {
            "test_form": test_form,
            "tests": TesterBase.objects.all().order_by("-fecha_creacion"),
        },
    )

def generar_distribucion(request):
    # Inicializar ambos formularios
    binomial_form = BinomialForm()
    exponencial_form = ExponencialForm()
    tipo = request.POST.get("tipo_distribucion") or None
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
    return render(request, "pages/distribucion/ver.html", {
        "distribucion": distribucion,
    })