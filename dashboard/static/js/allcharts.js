async function dashboardfetchSalesData() {
    try {
        chartshowLoading(); // Show chart spinner before starting fetch

        const response = await fetch("/monthly_sales_data/");  // Update with your Django URL
        const data = await response.json();

        // Get the length of the months array (or adjust if needed for another relevant data field)
        const monthCount = data.months.length;

        // Adjust the height of the chart container based on the number of months
        const chartContainer = document.querySelector('.chart-container-summary');
        const dynamicHeight = monthCount * 40 + 100;  // Example: 40px per month + some extra padding
        chartContainer.style.height = `${dynamicHeight}px`;

        // Initialize the chart
        const ctx = document.getElementById('salesChart').getContext('2d');
        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.months,
                datasets: [{
                    label: 'Sales Amount',
                    data: data.totals,
                    backgroundColor: '#714B67',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { 
                        display: false,
                        labels: {
                            font: {
                                size: 12 // Increase legend font size
                            }
                        }
                    },
                    tooltip: { 
                        enabled: true,
                        bodyFont: {
                            size: 12 // Increase tooltip font size
                        }
                    },
                    datalabels: {  
                        anchor: 'end',  
                        align: 'top',    
                        offset: 5, 
                        formatter: (value) => value.toLocaleString(), 
                        color: '#714B67',
                        font: {
                            size: 16 // Increase data labels font size
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            font: {
                                size: 14 // Increase x-axis labels font size
                            }
                        }
                    },
                    y: { 
                        beginAtZero: true,
                        ticks: {
                            font: {
                                size: 12 // Increase y-axis labels font size
                            }
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 20  
                    }
                }
            },
            plugins: [ChartDataLabels] 
        });

    } catch (error) {
        console.error("Error fetching sales data:", error);
    } finally {
        charthideLoading(); // Hide the loading spinner after the fetch completes
    }
}

/*
async function fetchTableChartData() {
    try {
        tableShowLoading(); // Show table spinner before starting fetch
        
        const response = await fetch("/monthly_sales_table_chart/");  // Update with your Django URL
        const data = await response.json();

        const tableBody = document.getElementById("tableBody");
        tableBody.innerHTML = ""; // Clear previous data

        data.group1.forEach((group, index) => {
            const row = `
                <tr>
                    <td>${group}</td>
                    <td>${data.inv_qty[index]}</td>
                    <td>${data.schemeqty[index]}</td>
                    <td>${data.final_qty[index]}</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });

        // Adjust the height of the chart container dynamically based on the number of rows
        const chartContainer = document.querySelector('.chart-container-summary');
        const rowCount = data.group1.length;  // Get the number of rows in the table

        // Calculate the height (for example, 40px per row)
        const dynamicHeight = rowCount * 40;  // Adjust multiplier based on your content size
        chartContainer.style.height = `${dynamicHeight}px`;

    } catch (error) {
        console.error("Error fetching table data:", error);
    } finally {
        tableHideLoading(); // Hide the table spinner after the fetch completes
    }
}
*/
// Spinner control for chart
const chartshowLoading = () => {
    const spinners = document.querySelectorAll('.chart-loading-spinner');
    spinners.forEach(spinner => {
        spinner.style.display = 'block';  // Show chart spinner
    });
};

const charthideLoading = () => {
    const spinners = document.querySelectorAll('.chart-loading-spinner');
    spinners.forEach(spinner => {
        spinner.style.display = 'none';  // Hide chart spinner
    });
};

// Spinner control for table
const tableShowLoading = () => {
    const spinners = document.querySelectorAll('.table-loading-spinner');
    spinners.forEach(spinner => {
        spinner.style.display = 'block';  // Show table spinner
    });
};

const tableHideLoading = () => {
    const spinners = document.querySelectorAll('.table-loading-spinner');
    spinners.forEach(spinner => {
        spinner.style.display = 'none';  // Hide table spinner
    });
};
