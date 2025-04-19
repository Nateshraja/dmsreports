

// Global session parameters object
let sessionParams = {};

// Fetch card data dynamically and update the target elements
function fetchCardData(endpoint, targetValueId, targetQtyId) {
    if (!sessionParams.param1 || !sessionParams.param2) {
        return;
    }

    const dynamicEndpoint = `${endpoint}?code=${sessionParams.param1}&type_param=${sessionParams.param2}`;

    fetch(dynamicEndpoint)
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`Failed to fetch data from ${dynamicEndpoint}. Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const targetValueElement = document.getElementById(targetValueId);
            const targetQtyElement = document.getElementById(targetQtyId);

            if (!targetValueElement || !targetQtyElement) {
                console.error(`One or both target elements not found in the DOM.`);
                return;
            }

            if (Array.isArray(data) && data.length > 0) {
                const saleValue = parseFloat(data[0].sale_value);
                const saleQty = parseFloat(data[0].sale_qty);

                targetValueElement.textContent = !isNaN(saleValue)
                    ? `Value: ${formatIndianCurrency(saleValue || 0)}`
                    : 'N/A';

                targetQtyElement.textContent = !isNaN(saleQty)
                    ? `Pcs: ${formatIndianQuantity(saleQty)}`
                    : 'N/A';
            } else {
                console.warn('No data found or invalid response format:', data);
                targetValueElement.textContent = 'N/A';
                targetQtyElement.textContent = 'N/A';
            }
        })
        .catch(error => console.error(`Error fetching data:`, error));
}

// Fetch card data dynamically and update the target element
function fetchOrderSummaryData(endpoint, targetId) {
    if (!sessionParams.param1 || !sessionParams.param2) {
        return;
    }

    const dynamicEndpoint = `${endpoint}?code=${sessionParams.param1}&type_param=${sessionParams.param2}`;

    fetch(dynamicEndpoint)
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`Failed to fetch data from ${dynamicEndpoint}. Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const targetElement = document.getElementById(targetId);
            if (!targetElement) {
                console.error(`Element with id "${targetId}" not found in the DOM.`);
                return;
            }

            // Assume the API returns an array of results; extract and format `sale_value`
            if (Array.isArray(data) && data.length > 0) {
                const saleValue = parseFloat(data[0].sale_value); // Convert to a number
                if (!isNaN(saleValue)) {
                    targetElement.textContent = saleValue;
                } else {
                    console.error('Invalid sale_value format. Expected a number:', saleValue);
                    targetElement.textContent = 'N/A';
                }
            } else {
                console.warn('No data found or invalid response format:', data);
                targetElement.textContent = 'N/A';
            }
        })
        .catch(error => console.error(`Error fetching data for ${targetId}:`, error));
}

function fetchStockData(endpoint) {
    if (!sessionParams.param1 || !sessionParams.param2) {
        return;
    }

    const dynamicEndpoint = `${endpoint}?code=${sessionParams.param1}&type_param=${sessionParams.param2}`;

    fetch(dynamicEndpoint)
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`Failed to fetch data from ${dynamicEndpoint}. Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (Array.isArray(data) && data.length > 0) {
                const stockInfo = data[0];
                    let stk_qty = stockInfo.pcs_qty || 0;
                    console.log(stk_qty);

                    //document.getElementById("box-qty").textContent = `Box    : ${stockInfo.box_qty || 0}`;
                    //document.getElementById("pcs-qty").textContent = `Pcs    : ${new Intl.NumberFormat("en-IN").format(stockInfo.pcs_qty || 0)}`;
                    document.getElementById("pcs-qty").textContent = `Pcs    : ${new Intl.NumberFormat("en-IN").format(stk_qty)}`;
                    document.getElementById("stock-value").textContent = `Value: ${formatIndianCurrency(stockInfo.stkvalue || 0)}`;
            } else {
                console.warn('No stock data found or invalid response format:', data);
                //document.getElementById("box-qty").textContent = "Box  : N/A";
                document.getElementById("pcs-qty").textContent = "Pcs  : N/A";
                document.getElementById("stock-value").textContent = "Value: N/A";
            }
        })
        .catch(error => console.error(`Error fetching stock data:`, error));
}


function getUrlParameter(name) {
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(window.location.search);
    return results ? decodeURIComponent(results[1].replace(/\+/g, ' ')) : '';
}

// Helper function to get CSRF token from cookies
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}

// Utility function to format numbers in Indian currency
function formatIndianCurrency(amount) {
    if (typeof amount !== 'number' || isNaN(amount)) {
        return 'N/A';
    }

    return amount.toLocaleString('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}
function formatIndianQuantity(amount) {
    if (typeof amount !== 'number' || isNaN(amount)) {
        return 'N/A';
    }

    return amount.toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }); // Formats number with Indian grouping (e.g., 1,00,000)
}

function fetchsaleorderSummary() {
    fetch("/saleorder_summary/") // Update with your actual API URL
        .then(response => response.json())
        .then(data => {
            if (data.saleorder_summary.length > 0) {
                const invoiceData = data.saleorder_summary[0]; // Assuming one row of data
                console.log(invoiceData)
                // Updating the respective fields
                document.getElementById("saleordercount").innerText = invoiceData.today_order_count || 0;
                document.getElementById("saleorderQty").innerText = new Intl.NumberFormat("en-IN").format(invoiceData.todayqty || 0);
                document.getElementById("so_amount").innerText = `₹ ${new Intl.NumberFormat("en-IN").format(invoiceData.todaysales || 0)}`;
            }
        })
        .catch(error => console.error("Error fetching invoice summary:", error));
}
function fetchInvoiceSummary() {
    fetch("/invoice_summary/") // Update with your actual API URL
        .then(response => response.json())
        .then(data => {
            if (data.invoice_summary.length > 0) {
                const invoiceData = data.invoice_summary[0]; // Assuming one row of data
                console.log(invoiceData)
                // Updating the respective fields
                document.getElementById("invoicecount").innerText = invoiceData.today_order_count || 0;
                document.getElementById("invoiceQty").innerText = new Intl.NumberFormat("en-IN").format(invoiceData.todayqty || 0);;
                document.getElementById("salesAmount").innerText = `₹ ${new Intl.NumberFormat("en-IN").format(invoiceData.todaysales || 0)}`;
            }
        })
        .catch(error => console.error("Error fetching invoice summary:", error));
}
// Initialize dashboard by fetching data for all cards
function initializeDashboard(params) {
    sessionParams = params;
    if (window.location.pathname === '/dmsdashboard/') {
    //console.log(sessionParams)
    // Example: Fetch data for specific cards
    fetchCardData('/sale_summary_card/', 'sales-invoice','sales-qty');
    fetchCardData('/purchase_summary_card/', 'purchases-invoice','purchases-qty');
    fetchStockData('/stock_summary_card/');
    fetchsaleorderSummary();
    fetchInvoiceSummary();
    //dashboardfetchSalesData();
    //fetchTableChartData();
    setTimeout(() => {
        let saleOrderElem = document.getElementById("saleordercount");
        let invoiceElem = document.getElementById("invoicecount");
        let pendingOrderElem = document.getElementById("pendingorder");
    
        if (saleOrderElem && invoiceElem && pendingOrderElem) {
            let saleOrderCount = Number(saleOrderElem.innerText) || 0;
            let invoiceCount = Number(invoiceElem.innerText) || 0;
            pendingOrderElem.innerText = saleOrderCount - invoiceCount;
        } else {
            pendingOrderElem.innerText = 0;
        }
    }, 300);  // Adjust delay if needed
    
    }
}

// Set session parameters and initialize dashboard
function setSessionParameters(param1, param2) {
    return fetch('/set_session/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ param1, param2 }),
    })
    .then(response => {
        if (response.ok) {
            setTimeout(() => {
                window.location.href = '/dmsdashboard/';
            }, 2000);
        } else {
            alert('Failed to log in. Please try again.');
        }
    })
    .catch(error => console.error('Error setting session parameters:', error));
}


 // Highlight the active link in the sidebar
 function setActiveSidebarLink() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar a').forEach(link => {
        link.classList.toggle('active', link.getAttribute('href') === currentPath);
    });
}


const showLoading = () => {
    document.getElementById("loading-spinner").style.display = "block";
    document.getElementById("pivot-container").style.display = "none"; // Hide Flexmonster during loading
};

const hideLoading = () => {
    document.getElementById("loading-spinner").style.display = "none";
    document.getElementById("pivot-container").style.display = "block"; // Show Flexmonster after loading
};

if (window.location.pathname === '/sales_data/') {

}
/*setTimeout(() => {
    let a = 50;
    document.getElementById("totalSales").innerText = "₹5,23,450"+a;
    document.getElementById("inventoryQty").innerText = "1,200";
    document.getElementById("finalQty").innerText = "1,500";

    document.querySelector(".chart-loading-spinner").style.display = "none";
    //document.querySelector(".table-loading-spinner").style.display = "none";
}, 2000); // Simulated delay
*/



function waitForJQuery(callback) {
    if (typeof jQuery !== 'undefined') {
        callback();
    } else {
        console.warn("Waiting for jQuery...");
        setTimeout(() => waitForJQuery(callback), 100);
    }
}

waitForJQuery(() => {
    $(document).ready(function () {
        console.log("✅ jQuery Loaded Successfully");

        if (typeof $.fn.select2 === 'undefined') {
            console.error("❌ Select2 is NOT loaded!");
        } else {
            console.log("✅ Select2 Loaded Successfully");

            // Initialize Select2
            $('.select2').select2({
                width: '100%',
                placeholder: "Search...",
                allowClear: true
            });
        }
    });
});


// Handle button clicks to switch charts
document.querySelectorAll(".report-btn").forEach(button => {
    button.addEventListener("click", function () {
        document.querySelectorAll(".report-btn").forEach(btn => btn.classList.remove("active"));
        this.classList.add("active");

        const reportType = this.getAttribute("data-report");
        updateChart(reportType);
        updateStockChart(reportType);
    });
});

/*$(document).ready(function () {
    $(".stock-report-btn").on("click", function () {
        $(".stock-report-btn").removeClass("active");
        $(this).addClass("active");

        let reportType = $(this).data("report") + "ChartContainer"; // Append 'ChartContainer' to match ID
        $(".stock-chart-container").removeClass("active").hide();
        $("#" + reportType).addClass("active").show();
    });
});



document.getElementById("signout-link").addEventListener("click", function (event) {
    event.preventDefault(); // Prevent default link behavior

    // Send a request to clear session in Django
    fetch('/logout/', { method: 'POST', credentials: 'same-origin' })
        .then(response => {
            if (response.ok) {
                // Redirect to the testdashboard page
                window.location.href = "/testdashboard/";
            } else {
                alert("Failed to sign out.");
            }
        })
        .catch(error => console.error("Error during sign out:", error));
});
*/