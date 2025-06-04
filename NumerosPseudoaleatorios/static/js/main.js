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
    const btnToggle1 = $('#btnToggle1');
    const btnToggle2 = $('#btnToggle2');
    const formToggle1 = $('#formToggle1');
    const formToggle2 = $('#formToggle2');

    if (btnToggle1.length && btnToggle2.length) {
        function toggleForms(isFormToogle1) {
            if (isFormToogle1) {
                btnToggle1.addClass('active');
                btnToggle2.removeClass('active');
                formToggle1.show();
                formToggle2.hide();
            } else {
                btnToggle1.removeClass('active');
                btnToggle2.addClass('active');
                formToggle1.hide();
                formToggle2.show();
            }
        }

        btnToggle1.on('click', function () { toggleForms(true); });
        btnToggle2.on('click', function () { toggleForms(false); });
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
})