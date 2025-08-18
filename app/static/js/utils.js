// initialize config variables
function initConfigVars() {
    const configDiv = document.getElementById('config-data');
    if (configDiv) {
        window.DEFAULT_MONTHS_DISPLAY = parseInt(configDiv.dataset.defaultMonthsDisplay);
        window.MAX_CUSTOM_ROWS = parseInt(configDiv.dataset.maxCustomRows);
        window.RESERVED_HEADERS = JSON.parse(configDiv.dataset.reservedHeaders);
        window.TRAD_TSP_RATE_MAX = parseInt(configDiv.dataset.tradTspRateMax);
        window.ROTH_TSP_RATE_MAX = parseInt(configDiv.dataset.rothTspRateMax);
    }
}


// enable all inputs
function enableAllInputs() {
    document.querySelectorAll('button, input, select, textarea').forEach(function(el) {
        el.disabled = false;
    });
}


// disable all inputs
function disableAllInputs() {
    document.querySelectorAll('button, input, select, textarea').forEach(function(el) {
        el.disabled = true;
    });
}


// show tooltip
function showTooltip(evt, text) {
    const tooltip = document.getElementById('tooltip');
    tooltip.innerText = text;
    tooltip.style.left = (evt.pageX + 10) + 'px';
    tooltip.style.top = (evt.pageY + 10) + 'px';
    tooltip.style.display = 'block';
}


// hide tooltip
function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    tooltip.style.display = 'none';
}


// show toast messages
function showToast(message, duration = 6500) {
    const MAX_TOASTS = 3;
    const container = document.getElementById('toast-container');

    while (container.children.length >= MAX_TOASTS) {
        container.removeChild(container.firstChild);
    }

    let toast = document.createElement('div');
    toast.className = 'toast shadow';
    toast.textContent = message;

    let closeBtn = document.createElement('span');
    closeBtn.textContent = '✖';
    closeBtn.className = 'toast-close';
    closeBtn.onclick = () => toast.remove();
    toast.appendChild(closeBtn);

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, duration);
}


// stripe table rows
function stripeTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    let rowIndex = 0;
    table.querySelectorAll('tbody').forEach(function(tbody) {
        tbody.querySelectorAll('tr').forEach(function(tr) {
            if (rowIndex % 2 === 1) {
                tr.classList.add('even-row');
            } else {
                tr.classList.remove('even-row');
            }
            rowIndex++;
        });
    });
}


// highlight changes
function highlight_changes() {
    const highlight_color = getComputedStyle(document.documentElement).getPropertyValue('--highlight_yellow_color').trim();
    var checkbox = document.getElementById('highlight-changes-checkbox');
    var checked = checkbox.checked;
    var table = document.getElementById('paydf-table');
    var rows = table.getElementsByTagName('tr');

    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName('td');

        //skip spacer rows
        if (cells.length < 2) continue;

        // get row header (first cell)
        var rowHeader = cells[0].textContent.trim();
        
        //start from col 3 (index 2), skip row header and first month
        for (var j = 2; j < cells.length; j++) {
            var cell = cells[j];
            var prevCell = cells[j - 1];

            if (
                checked &&
                cell.textContent.trim() !== prevCell.textContent.trim() &&
                !(rowHeader === "Difference" && cell.textContent.trim() === "$0.00")
            ) {
                cell.style.backgroundColor = highlight_color;
            } else {
                cell.style.backgroundColor = '';
            }
        }
    }
}


// show all variables
function show_all_variables() {
    var checkbox = document.getElementById('show-all-variables-checkbox');
    var checked = checkbox.checked;
    var rows = document.getElementsByClassName('variable-row');
    for (var i = 0; i < rows.length; i++) {
        rows[i].style.display = checked ? 'table-row' : 'none';
    }
}


// show tsp options
function show_tsp_options() {
    var checkbox = document.getElementById('show-tsp-options-checkbox');
    var checked = checkbox.checked;
    var rows = document.getElementsByClassName('tsp-row');

    for (var row of rows) {
        if (checked) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    }
}


// export paydf
function exportPaydf() {
    var table = document.getElementById('paydf-table');
    var filetype = document.getElementById('export-dropdown').value;
    var filename = filetype === 'csv' ? 'payles.csv' : 'payles.xlsx';

    var workbook = XLSX.utils.table_to_book(table, {sheet: "PayDF", raw: true});
    if (filetype === 'csv') {
        XLSX.writeFile(workbook, filename, {bookType: 'csv'});
    } else {
        XLSX.writeFile(workbook, filename);
    }
}


// input validation for TSP rates
function updateTspRateFields() {
    const tradBaseRate = document.getElementById('trad_tsp_base_rate_f');
    const tradSpecialtyRate = document.getElementById('trad_tsp_specialty_rate_f');
    const tradIncentiveRate = document.getElementById('trad_tsp_incentive_rate_f');
    const tradBonusRate = document.getElementById('trad_tsp_bonus_rate_f');
    const rothBaseRate = document.getElementById('roth_tsp_base_rate_f');
    const rothSpecialtyRate = document.getElementById('roth_tsp_specialty_rate_f');
    const rothIncentiveRate = document.getElementById('roth_tsp_incentive_rate_f');
    const rothBonusRate = document.getElementById('roth_tsp_bonus_rate_f');

    let tradRateDisable = false;
    let rothRateDisable = false;
    const tradRateValue = tradBaseRate.value;
    const rothBaseValue = rothBaseRate.value;

    if (tradRateValue === "" || parseInt(tradRateValue, 10) === 0) {
        tradRateDisable = true;
    }

    if (rothBaseValue === "" || parseInt(rothBaseValue, 10) === 0) {
        rothRateDisable = true;
    }

    tradSpecialtyRate.disabled = tradRateDisable;
    tradIncentiveRate.disabled = tradRateDisable;
    tradBonusRate.disabled = tradRateDisable;
    rothSpecialtyRate.disabled = rothRateDisable;
    rothIncentiveRate.disabled = rothRateDisable;
    rothBonusRate.disabled = rothRateDisable;
}




// =========================
// update buttons
// =========================

function updateButtonStates() {
    const buttonIds = [
        'update-les-button',
        'add-entitlement-button',
        'add-deduction-button',
        'export-button'
    ];

    const disable = editingIndex !== null;
    buttonIds.forEach(function(id) {
        const btn = document.getElementById(id);
        if (btn) {
            btn.disabled = disable;
        }
    });
}



// =========================
// drag and drop file upload
// =========================

(function() {
    var dropContainer = document.getElementById("home-drop");
    var fileInput = document.getElementById("home-input");
    var form = dropContainer.closest("form");

    if (!dropContainer || !fileInput || !form) return;

    // prevent default drag behaviors
    ["dragenter", "dragover", "dragleave", "drop"].forEach(function(eventName) {
        dropContainer.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    dropContainer.addEventListener("dragenter", function() {
        dropContainer.classList.add("drag-active");
    });

    dropContainer.addEventListener("dragleave", function(e) {
        if (e.target === dropContainer) {
            dropContainer.classList.remove("drag-active");
        }
    });

    dropContainer.addEventListener("drop", function(e) {
        dropContainer.classList.remove("drag-active");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
        }
    });
})();