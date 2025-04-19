function initializeFlexmonster(
    containerId,
    dataSource = [],
    flex_key,
    reportFilter = [],
    measures = [],
    tablerows = [],
    additionalOptions = {} // Optional parameter for additional configurations
) {
    const pivot = new Flexmonster({
        container: `#${containerId}`,
        componentFolder: "flexmonster/",
        licenseKey: flex_key,
        toolbar: true,
        customizeToolbar: function(toolbar) {
            // Get the default toolbar items
            toolbar.items = toolbar.items.filter(function(item) {
                return item.id !== "fm-save" &&   // Hide Save option
                       item.id !== "fm-open" &&   // Hide Open option
                       item.id !== "fm-connect";  // Hide Connect option
            });
        },
        report: {
            dataSource: {
                type: "json",
                data: dataSource
            },
            slice: {
                rows: tablerows,
                columns: [{ uniqueName: "[Measures]" }],
                measures: measures,
                reportFilters: reportFilter
            },
            options: {
                grid: {
                    type: "classic",
                    showHeaders: true,
                    classicView: true,
                    showRowHierarchies: true,
                    showColumnGrandTotals: false,
                    showRowGrandTotals: false,
                    showFilter: true,
                    showSubtotal: false
                },
                showTotals: "off",  // Disables all subtotals
            }
        },
        ready: function() {
            // Apply row height and font size through CSS
            var style = document.createElement("style");
            style.innerHTML = `
                #fm-pivot-view .fm-grid-layout .fm-body .fm-row {
                    height: auto !important; /* Let Flexmonster manage row height */
                }
                #fm-pivot-view .fm-grid-layout .fm-cell {
                    font-size: 15px;  /* Bigger font */
                    padding: 1px;  /* Better spacing inside cells */
                    text-align: left; /* Align text centrally */
                }
                #fm-pivot-view .fm-grid-layout .fm-header {
                    background-color: #f1f1f1; /* Light background for headers */
                    font-weight: bold;
                    color: #024e96;
                    text-transform: uppercase;
                }
            `;
            document.head.appendChild(style);
        
            // Apply number formatting
            pivot.customizeCell(function(cell, data) {
        
                if (data.type === "value" && !isNaN(data.value)) {
                    cell.text = new Intl.NumberFormat("en-IN", { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                    }).format(data.value);
                }
            });
        }
        
        
    });

    // Automatically expand all rows and apply styling
    pivot.on("reportcomplete", function () {
        pivot.expandAllData();
        if (document.getElementById(containerId)) {
            document.getElementById(containerId).style.backgroundColor = "#1c1c1c";
        }
    });

    // Handle other events (optional)
    pivot.on("dataerror", function (err) {
        console.error("Flexmonster Data Error:", err);
    });

    return pivot; // Return the pivot instance for further use
}

function initializeFlatFlexmonster(containerId, data, flex_key) {
    const pivot = new Flexmonster({
        container: `#${containerId}`,
        componentFolder: "flexmonster/",
        licenseKey: flex_key,
        toolbar: true,
        report: {
            dataSource: {
                type: "json",
                data: data // Using the 'data' parameter passed to the function
            },
            slice: {
                rows: [],   // Customize these as needed
                columns: [], // Customize these as needed
                measures: [] // Customize these as needed
            },
            options: {
                grid: {
                    type: "flat"
                }
            }
        }
    });

    // Handle other events (optional)
    pivot.on("dataerror", function (err) {
        console.error("Flexmonster Data Error:", err);
    });

    return pivot; // Return the pivot instance for further use
}
