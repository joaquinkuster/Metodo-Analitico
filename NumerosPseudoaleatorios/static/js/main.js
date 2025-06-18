$(document).ready(function () {
    // Configuración de la acción de eliminar con confirmación
    const btnEliminar = $(".btnEliminar");
    if (btnEliminar.length) {
        btnEliminar.each(function () {
            const btn = $(this);
            const form = btn.closest("form"); // Busca el formulario más cercano

            btn.on("click", function (e) {
                e.preventDefault();
                Swal.fire({
                    title: "¿Estás seguro?",
                    text: "Esta acción no se puede deshacer.",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#3085d6",
                    cancelButtonColor: "#d33",
                    confirmButtonText: "Sí, eliminar",
                    cancelButtonText: "Cancelar"
                }).then((result) => {
                    if (result.isConfirmed) {
                        form.submit(); // Envía el formulario si el usuario confirma
                    }
                });
            });
        });
    }

    // Toggle entre formularios
    const buttons = $('[data-toggle-target]');
    const forms = $('[data-toggle-form]');

    if (buttons.length && forms.length) {
        buttons.on('click', function () {
            const formId = $(this).data('toggle-target');

            // Activar solo el botón correspondiente
            buttons.removeClass('active');
            $(this).addClass('active');

            // Mostrar solo el formulario correspondiente
            forms.hide();
            $(`#${formId}`).show();
        });
    }

    // Función para separar dígitos individualmente
    function separarDigitos(numeros) {
        const digitos = [];
        for (let i = 0; i < numeros.length; i++) {
            const strNum = String(numeros[i]);
            for (let j = 0; j < strNum.length; j++) {
                // Convierte cada carácter a entero
                digitos.push(parseInt(strNum[j], 10));
            }
        }
        return digitos;
    }

    // Función de agrupación en base a una cantidad n
    function agruparNumeros(n, numeros) {
        if (n < 1) return numeros.join(', ');

        const grupos = [];
        for (let i = 0; i < numeros.length; i += n) {
            grupos.push(numeros.slice(i, i + n).join(''));
        }
        return grupos.join(', ');
    }

    const inputAgruparDigitos = $('#inputAgruparDigitos');
    const numerosGenerados = $('#numerosGenerados');

    if (inputAgruparDigitos.length &&
        numerosGenerados.length
    ) {
        function procesarAgrupacion() {
            // Validación nativa HTML5
            if (!inputAgruparDigitos[0].checkValidity()) {
                inputAgruparDigitos[0].reportValidity(); // Muestra mensaje nativo del navegador
                return;
            }

            const n = parseInt(inputAgruparDigitos.val()) || 1;
            // Obtenemos los números directamente del elemento <code>
            let numeros = numerosGenerados.data("numeros");
            numeros = separarDigitos(numeros); // Primero, separamos todos los dígitos
            numerosGenerados.text(agruparNumeros(n, numeros));
        }

        procesarAgrupacion(); // Procesar la agrupación al inicio

        inputAgruparDigitos.on('input change', function (e) {
            e.preventDefault();
            procesarAgrupacion();
        });
    }

    // Parsear los datos de secuencias (compartidos)
    const $selectSecuencia = $('[name="secuencia"]'); // Nota el $ para indicar que es un objeto jQuery

    if ($selectSecuencia.length > 0) {

        const rawData = $('#data-secuencias').val();
        const secuenciasData = {};
        rawData.split(';').forEach(item => {
            const [id, numeros] = item.split('=');
            if (id && numeros) {
                secuenciasData[id] = numeros;
            }
        });

        $selectSecuencia.each(function (index, select) {
            $(select).change(function () {
                const idSecuencia = $(this).val();
                const $form = $(this).closest('form');

                const $containerNumeros = $form.find("#numeros-secuencia");
                const $contenidoNumeros = $form.find("#numeros-contenido");

                if (idSecuencia && secuenciasData[idSecuencia]) {
                    $contenidoNumeros.text(secuenciasData[idSecuencia]);
                    $containerNumeros.show();
                } else {
                    $containerNumeros.hide();
                }
            }).trigger('change'); // Mostrar inmediatamente si hay valor
        });
    }

    // Parsear los datos de las distribuciones (compartidos)
    const $selectTriangular = $('[name="triangular"]'); // Nota el $ para indicar que es un objeto jQuery

    if ($selectTriangular.length > 0) {

        const rawData = $('#data-pesos').val();
        const pesosData = {};
        rawData.split(';').forEach(item => {
            const [id, pesos] = item.split('=');
            if (id && pesos) {
                pesosData[id] = pesos;
            }
        });

        $selectTriangular.each(function (index, select) {
            $(select).change(function () {
                const idTriangular = $(this).val();
                const $form = $(this).closest('form');

                const $contenedorPesos = $form.find("#pesos-contenedor");
                const $contenidoPesos = $form.find("#pesos-contenido");

                if (idTriangular && pesosData[idTriangular]) {
                    $contenidoPesos.text(pesosData[idTriangular]);
                    $contenedorPesos.show();
                } else {
                    $contenedorPesos.hide();
                }
            }).trigger('change'); // Mostrar inmediatamente si hay valor
        });
    }

    const selectMultipleCamiones = $('.select-multiple');
    if (selectMultipleCamiones.length) {
        selectMultipleCamiones.select2({
            placeholder: "Seleccione uno o más camiones",
            allowClear: true
        });
    }
})