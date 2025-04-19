let charts = {}; // Store chart instances

async function updateChart(reportType, chartType = "bar") {
    try {
        const chartContainer = document.getElementById(`${reportType}ChartContainer`);
        if (!chartContainer) {
            console.warn(`Chart container for ${reportType} not found. Skipping update.`);
            return;
        }

        const response = await fetch(`/get_chart_data/${reportType}/`);
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        let labels, values, labelText;
        switch (reportType) {
            case "dashboard":
                labels = data.map(row => row.category);
                values = data.map(row => row.value);
                labelText = "Dashboard Summary";
                break;
            case "overall":
                labels = data.map(row => row.month);
                values = data.map(row => row.total_sales);
                labelText = "Overall Month Wise Sales";
                break;
            case "top-sales":
                labels = data.map(row => row.product_name);
                values = data.map(row => row.quantity);
                labelText = "Top Selling Products";
                break;
            case "top-customer":
                labels = data.map(row => row.cus_name);
                values = data.map(row => row.total_spent);
                labelText = "Top Customers";
                break;
            case "big-deals":
                labels = data.map(row => `${row.invno}`);
                values = data.map(row => row.inv_amt);
                labelText = "Big Deals";
                break;
            /*case "brand":
                labels = data.map(row => row.brand);
                values = data.map(row => row.sales);
                labelText = "brand";
                break;
            case "category":
                labels = data.map(row => row.category);
                values = data.map(row => row.quantity);
                labelText = "category";
                break;
            case "division":
                labels = data.map(row => row.division);
                values = data.map(row => row.total_spent);
                labelText = "division";
                break;
                */
            default:
                console.error("Unknown report type:", reportType);
                return;
        }

        console.log(`Switching to: ${reportType} (Type: ${chartType})`);

        // Hide all charts before showing the active one
        document.querySelectorAll(".chart-container").forEach(chart => {
            chart.style.display = "none";
        });

        // Destroy the existing chart before creating a new one
        if (charts[reportType]) {
            charts[reportType].destroy();
            console.warn(`Destroyed previous ${reportType} chart`);
        }

        // Show the active chart container
        chartContainer.style.display = "block";

        // Initialize the new chart
        initializeChart(reportType, `${reportType}`, chartType, labels, values, labelText);

    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

function initializeChart(section, canvasId, chartType, labels, values, labelText) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element with ID ${canvasId} not found.`);
        return;
    }

    const ctx = canvas.getContext("2d");

    const isCurrency = ["Overall Sales", "Big Deals", "Top Customers"].includes(labelText);

    charts[section] = new Chart(ctx, {
        type: chartType,  
        data: {
            labels: labels,
            datasets: [{
                label: labelText,
                data: values,
                backgroundColor: ["#4CAF50", "#FF5733", "#3498DB", "#F1C40F", "#9B59B6"]
            }]
        },
        options: { 
            responsive: true,
            plugins: {
                tooltip: { 
                    enabled: true,
                    callbacks: {
                        label: function(tooltipItem) {
                            let value = tooltipItem.raw;
                            return isCurrency 
                                ? `₹ ${new Intl.NumberFormat("en-IN").format(value)}` // Currency format
                                : new Intl.NumberFormat("en-IN").format(value); // Quantity format
                        }
                    }
                },
                legend: { display: true },
                datalabels: { 
                    anchor: 'end',
                    align: 'top',
                    formatter: (value) => {
                        return isCurrency 
                            ? `₹ ${new Intl.NumberFormat("en-IN").format(value)}`  // Format as Indian currency
                            : new Intl.NumberFormat("en-IN").format(value); // Format as quantity
                    },
                    color: '#000',
                    font: { weight: 'bold', size: 11 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return isCurrency 
                                ? `₹ ${new Intl.NumberFormat("en-IN").format(value)}` // Axis labels as currency
                                : new Intl.NumberFormat("en-IN").format(value); // Axis labels as quantity
                        }
                    }
                }
            }
        },
        plugins: [ChartDataLabels]
    });
}

// ✅ Add event listener for buttons only if elements exist
document.addEventListener("DOMContentLoaded", function () {
    const reportButtons = document.querySelectorAll(".report-btn");
    if (reportButtons.length > 0) {
        reportButtons.forEach(button => {
            button.addEventListener("click", function () {
                const reportType = this.getAttribute("data-report");
                const chartType = this.getAttribute("data-chart-type");

                document.querySelectorAll(".report-btn").forEach(btn => btn.classList.remove("active"));
                this.classList.add("active");

                updateChart(reportType, chartType);
            });
        });

        // ✅ Load default chart only if the element exists
        if (document.getElementById("overallChartContainer")) {
            updateChart("overall", "bar");
        }
    }
});

// ✅ Export Chart Handling
document.addEventListener("DOMContentLoaded", function () {
    const exportButtons = document.querySelectorAll(".export-btn");
    if (exportButtons.length > 0) {
        exportButtons.forEach(button => {
            button.addEventListener("click", function () {
                const format = this.getAttribute("data-format");
                exportChart(format);
            });
        });
    }
});

function exportChart(format) {
    const activeChartContainer = document.querySelector(".chart-container:not([style*='display: none'])");
    if (!activeChartContainer) {
        console.error("No active chart found.");
        return;
    }

    const canvas = activeChartContainer.querySelector("canvas");
    if (!canvas) {
        console.error("No canvas found in active chart container.");
        return;
    }

    const chartDataURL = canvas.toDataURL(`image/${format}`, 1.0);

    if (format === "pdf") {
        // Export as PDF using jsPDF
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF("landscape");
        pdf.addImage(chartDataURL, "JPEG", 15, 40, 250, 100);
        pdf.save("chart.pdf");
    } else {
        // Export as PNG or JPG
        const link = document.createElement("a");
        link.href = chartDataURL;
        link.download = `chart.${format}`;
        link.click();
    }
}
