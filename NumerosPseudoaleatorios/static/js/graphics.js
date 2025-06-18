$(document).ready(function () {
    // Gráfico ChI-Cuadrado para los tests de aleatoriedad
    const chiCuadradoChart = $("#chiCuadradoChart");

    if (chiCuadradoChart.length) {
        // Datos necesarios
        const estadistico_prueba = parseFloat($("#estadistico_prueba").val());
        const valor_critico = parseFloat($("#valor_critico").val());
        const grados_libertad = parseInt($("#grados_libertad").val());
        const aprobado = $("#aprobado").val().toLowerCase() === "true";

        // Generar puntos para la curva
        const xValues = [];
        const yValues = [];
        const maxX = Math.max(valor_critico, estadistico_prueba) * 1.5;

        for (let x = 0; x <= maxX; x += maxX / 200) {
            xValues.push(x);
            yValues.push(jStat.chisquare.pdf(x, grados_libertad));
        }

        // Configuración del gráfico
        const ctx = chiCuadradoChart[0].getContext('2d');
        const myChart = new Chart(ctx, {
            type: 'scatter', // Cambiamos a tipo scatter para mejor control
            data: {
                datasets: [
                    // Curva principal (como línea)
                    {
                        label: `Distribución χ² (gl=${grados_libertad})`,
                        data: xValues.map((x, i) => ({ x, y: yValues[i] })),
                        borderColor: '#4e73df',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1,
                        showLine: true,
                        pointRadius: 0
                    },
                    // Área de rechazo
                    {
                        label: 'Zona de rechazo',
                        data: xValues.map((x, i) => x >= valor_critico ? { x, y: yValues[i] } : null),
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 0.2)',
                        borderWidth: 0,
                        fill: true,
                        showLine: true,
                        pointRadius: 0
                    },
                    // Valor crítico
                    {
                        label: `Valor crítico (${valor_critico.toFixed(2)})`,
                        data: [{
                            x: valor_critico,
                            y: jStat.chisquare.pdf(valor_critico, grados_libertad)
                        }],
                        backgroundColor: 'red',
                        borderColor: 'red',
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        showLine: false
                    },
                    // Estadístico de prueba
                    {
                        label: `Estadístico prueba (${estadistico_prueba.toFixed(2)})`,
                        data: [{
                            x: estadistico_prueba,
                            y: jStat.chisquare.pdf(estadistico_prueba, grados_libertad)
                        }],
                        backgroundColor: aprobado ? '#1cc88a' : '#f6c23e',
                        borderColor: aprobado ? '#1cc88a' : '#f6c23e',
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        showLine: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            boxWidth: 12,
                            padding: 10,
                            font: {
                                size: window.innerWidth < 768 ? 10 : 12
                            }
                        }
                    },
                    tooltip: {
                        bodyFont: {
                            size: window.innerWidth < 768 ? 10 : 12
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Valor χ²',
                            font: {
                                size: window.innerWidth < 768 ? 10 : 12
                            }
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45,
                            font: {
                                size: window.innerWidth < 768 ? 8 : 10
                            }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Densidad',
                            font: {
                                size: window.innerWidth < 768 ? 10 : 12
                            }
                        },
                        ticks: {
                            font: {
                                size: window.innerWidth < 768 ? 8 : 10
                            }
                        }
                    }
                }
            }
        });

        // Redimensionar el gráfico
        window.addEventListener('resize', function () {
            myChart.resize();
        });
    }

    // Gráfico PDF y CDF para las distribuciones teóricas y simuladas
    const pdfChart = $("#pdfChart");
    const cdfChart = $("#cdfChart");

    if (pdfChart.length || cdfChart.length) {
        // Datos necesarios
        const xsTeo = JSON.parse($("#xsTeo").val() || 'null');
        const pdfTeo = JSON.parse($("#pdfTeo").val() || 'null');
        const cdfTeo = JSON.parse($("#cdfTeo").val() || 'null');
        const xsSim = JSON.parse($("#xsSim").val() || 'null');
        const pdfSim = JSON.parse($("#pdfSim").val() || 'null');
        const cdfSim = JSON.parse($("#cdfSim").val() || 'null');


        const tipo = $("#tipoDistribucion").val();  // "BI" para discreta, otro para continua

        // Configuración común
        const esDiscreta = tipo === "BI";

        function crearChartPDF() {
            const ctx = pdfChart[0].getContext('2d');

            const chartConfig = {
                type: esDiscreta ? 'bar' : 'scatter',
                data: {
                    labels: esDiscreta ? xsTeo : undefined, // etiquetas solo si es discreta
                    datasets: []
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: esDiscreta
                            ? {
                                type: 'linear',
                                title: { display: true, text: 'x' },
                                ticks: {
                                    stepSize: 1,
                                    callback: (val) => Number.isInteger(val) ? val : ''
                                }
                            }
                            : {
                                type: 'linear',
                                title: { display: true, text: 'x' }
                            },
                        y: {
                            title: {
                                display: true,
                                text: esDiscreta ? 'P(X=x)' : 'f(x)'
                            }
                        }
                    },
                    plugins: {
                        legend: { position: 'top' },
                        tooltip: { mode: 'index', intersect: false },
                        title: {
                            display: true,
                            text: 'Distribución de Probabilidad (PDF)'
                        }
                    }
                }
            };

            // Dataset Teórica
            const teoricaDataset = esDiscreta
                ? {
                    type: 'bar',
                    label: 'Teórica',
                    data: pdfTeo,
                    backgroundColor: 'rgba(0,123,255,0.6)',
                    borderColor: 'rgba(0,123,255,1)',
                    borderWidth: 1,
                    barPercentage: 1.0,
                    categoryPercentage: 1.0
                }
                : {
                    type: 'line',
                    label: 'Teórica',
                    data: xsTeo.map((x, i) => ({ x, y: pdfTeo[i] })),
                    borderColor: 'rgba(0,123,255,1)',
                    backgroundColor: 'rgba(0,123,255,0.1)',
                    borderWidth: 2,
                    fill: true,
                    showLine: true,
                    pointRadius: 0,
                    tension: 0.4
                };

            // Dataset Simulada
            const simuladaDataset = esDiscreta
                ? {
                    type: 'bar',
                    label: 'Simulada',
                    data: pdfSim,
                    backgroundColor: 'rgba(220,53,69,0.6)',
                    borderColor: 'rgba(220,53,69,1)',
                    borderWidth: 1,
                    barPercentage: 1.0,
                    categoryPercentage: 1.0
                }
                : {
                    type: 'scatter',
                    label: 'Simulada',
                    data: xsSim.map((x, i) => ({ x, y: pdfSim[i] })),
                    backgroundColor: 'rgba(220,53,69,0.6)',
                    borderColor: 'rgba(220,53,69,1)',
                    borderWidth: 1,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    showLine: false
                };

            // Cargar datasets
            chartConfig.data.datasets.push(teoricaDataset, simuladaDataset);

            return new Chart(ctx, chartConfig);
        }


        function crearChartCDF() {
            const ctx = cdfChart[0].getContext('2d');

            return new Chart(ctx, {
                type: 'scatter', // Cambiado a scatter para mejor visualización
                data: {
                    datasets: [
                        {
                            label: 'Teórica',
                            data: xsTeo.map((x, i) => ({ x: x, y: cdfTeo[i] })),
                            borderColor: 'rgba(0,123,255,1)',
                            backgroundColor: 'rgba(0,123,255,0.1)',
                            borderWidth: 2,
                            fill: false,
                            showLine: true, // Línea continua para la teórica
                            pointRadius: 0, // Sin puntos para la teórica
                            tension: 0.4
                        },
                        {
                            label: 'Simulada',
                            data: xsSim.map((x, i) => ({ x: x, y: cdfSim[i] })),
                            borderColor: 'rgba(220,53,69,1)',
                            backgroundColor: 'rgba(220,53,69,0.6)',
                            borderWidth: 1,
                            pointRadius: 5, // Puntos más grandes para simulada
                            pointHoverRadius: 7,
                            showLine: false, // Solo puntos, sin línea
                            pointStyle: 'circle'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'linear',
                            title: { display: true, text: 'x' },
                            min: Math.min(...xsTeo, ...xsSim),
                            max: Math.max(...xsTeo, ...xsSim)
                        },
                        y: {
                            title: { display: true, text: 'F(x)' },
                            min: 0,
                            max: 1,
                            ticks: {
                                stepSize: 0.1
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    return `${context.dataset.label}: (${context.parsed.x.toFixed(5)}, ${context.parsed.y.toFixed(5)})`;
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'Distribución Acumulada (CDF)'
                        }
                    }
                }
            });
        }

        let chartPdf = pdfChart.length ? crearChartPDF() : null;
        let chartCdf = cdfChart.length ? crearChartCDF() : null;

        // Ahora tanto al inicializar como al redimensionar
        window.addEventListener('resize', () => {
            chartPdf?.resize();
            chartCdf?.resize();
        });
    }
})