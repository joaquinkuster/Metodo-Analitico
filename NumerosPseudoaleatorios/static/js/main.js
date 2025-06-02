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

    // Función de agrupación 
    function agruparNumeros(n, numeros) {
        if (n < 1) return numeros.join(', ');

        const grupos = [];
        for (let i = 0; i < numeros.length; i += n) {
            grupos.push(numeros.slice(i, i + n).join(''));
        }
        return grupos.join(', ');
    }

    const formAgruparDigitos = $('#formAgruparDigitos');
    const inputAgruparDigitos = $('#inputAgruparDigitos');
    const numerosGenerados = $('#numerosGenerados');

    if (formAgruparDigitos.length &&
        inputAgruparDigitos.length &&
        numerosGenerados.length
    ) {
        formAgruparDigitos.on('submit', function (e) {
            e.preventDefault();
            const n = parseInt(inputAgruparDigitos.val()) || 1;
            // Obtenemos los números directamente del elemento <code>
            const numeros = numerosGenerados.data("numeros");
            numerosGenerados.text(agruparNumeros(n, numeros));
        });
    }
})