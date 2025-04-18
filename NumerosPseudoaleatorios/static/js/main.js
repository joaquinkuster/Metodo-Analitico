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
    const btnVonNeumann = $('#btn-vonneumann');
    const btnCongruencial = $('#btn-congruencial');
    const formVonNeumann = $('#form-vonneumann');
    const formCongruencial = $('#form-congruencial');

    if (btnVonNeumann.length && btnCongruencial.length) {
        function toggleForms(vonNeumann) {
            if (vonNeumann) {
                btnVonNeumann.addClass('active');
                btnCongruencial.removeClass('active');
                formVonNeumann.show();
                formCongruencial.hide();
            } else {
                btnVonNeumann.removeClass('active');
                btnCongruencial.addClass('active');
                formVonNeumann.hide();
                formCongruencial.show();
            }
        }

        btnVonNeumann.on('click', function () { toggleForms(true); });
        btnCongruencial.on('click', function () { toggleForms(false); });
    }
})