async function updateStockTable(reportType) {
    try {
        const response = await fetch(`/get_stock_chart_data/${reportType}/`);
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        let tableData = data.map(row => [
            row.brand || row.category || row.division, 
            new Intl.NumberFormat("en-IN").format(row.qty),
            new Intl.NumberFormat("en-IN").format(row.sales)
        ]);

        let table = $('#stockTable').DataTable();
        table.clear().rows.add(tableData).draw();
    } catch (error) {
        console.error("Error fetching stock data:", error);
    }
}

$(document).ready(function () {
    $('#stockTable').DataTable({
        paging: false,
        searching: false
    });

    $('.report-btn').on('click', function () {
        let reportType = $(this).data('report');
        $('.report-btn').removeClass('active');
        $(this).addClass('active');
        updateStockTable(reportType);
    });

    updateStockTable('brand');
});
