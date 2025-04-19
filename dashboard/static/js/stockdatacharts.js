function updateStockChart(reportType) {
    console.log("Fetching stock chart data for:", reportType);

    let chartContainer = document.getElementById(reportType + "StockChartContainer");
    let canvas = document.getElementById(reportType);
    let tableBody = document.querySelector(`#${reportType}StockTable tbody`);

    if (!chartContainer || !canvas || !tableBody) {
        console.error("Chart container or table for", reportType, "not found.");
        return;
    }

    // Hide all charts and show only the selected one
    document.querySelectorAll(".stock-chart-container").forEach(container => container.style.display = "none");
    chartContainer.style.display = "block";

    // Fetch data from Django API
    fetch(`/get_stock_chart_data/${reportType}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not OK");
            }
            return response.json();
        })
        .then(data => {
            if (!data || data.length === 0) {
                console.warn("No data available for the chart");
                return;
            }

            // Clear existing table data
            tableBody.innerHTML = "";

            let labels = [];
            let quantities = [];
            let values = [];

            // Populate table and prepare data for chart
            data.forEach(item => {
                labels.push(item.name);
                quantities.push(item.quantity);
                values.push(item.value);

                let row = `<tr>
                    <td>${item.name}</td>
                    <td>${item.quantity}</td>
                    <td>${item.value}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });

            let chartData = {
                labels: labels,
                datasets: [
                    {
                        label: "Quantity",
                        backgroundColor: "rgba(54, 162, 235, 0.5)",
                        borderColor: "rgba(54, 162, 235, 1)",
                        borderWidth: 1,
                        data: quantities
                    },
                    {
                        label: "Value",
                        backgroundColor: "rgba(255, 99, 132, 0.5)",
                        borderColor: "rgba(255, 99, 132, 1)",
                        borderWidth: 1,
                        data: values
                    }
                ]
            };

            if (window.stockChart) {
                window.stockChart.destroy(); // Destroy previous chart before rendering new one
            }

            let ctx = canvas.getContext("2d");
            window.stockChart = new Chart(ctx, {
                type: "bar",
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error("Error fetching stock chart data:", error);
        });
}
