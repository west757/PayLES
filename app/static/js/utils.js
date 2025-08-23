// initialize config variables
function initConfigVars() {
    const configDiv = document.getElementById('config-data');
    if (configDiv) {
        window.DEPENDENTS_MAX = parseInt(configDiv.dataset.dependentsMax);
        window.TRAD_TSP_RATE_MAX = parseInt(configDiv.dataset.tradTspRateMax);
        window.ROTH_TSP_RATE_MAX = parseInt(configDiv.dataset.rothTspRateMax);
        window.HOME_OF_RECORDS = JSON.parse(configDiv.dataset.homeOfRecords);
        window.GRADES = JSON.parse(configDiv.dataset.grades);
        window.SGLI_COVERAGES = JSON.parse(configDiv.dataset.sgliCoverages);
    }
}


// sync settings container height with budget table
function syncSettingsContainerHeight() {
    const budget = document.getElementById('budget');
    const settingsContainer = document.getElementById('settings-container');
    if (budget && settingsContainer) {
        settingsContainer.style.height = budget.offsetHeight + 'px';
    }
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

    let closeButton = document.createElement('span');
    closeButton.textContent = '✖';
    closeButton.className = 'toast-close';
    closeButton.onclick = () => toast.remove();
    toast.appendChild(closeButton);

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, duration);
}


// highlight changes
function highlight_changes() {
    const highlight_color = getComputedStyle(document.documentElement).getPropertyValue('--highlight_yellow_color').trim();
    var checkbox = document.getElementById('highlight-changes-checkbox');
    var checked = checkbox.checked;
    var table = document.getElementById('budget-table');
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
    var rows = document.getElementsByClassName('var-row');
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


// export budget
function exportBudget() {
    var table = document.getElementById('budget-table');
    var filetype = document.getElementById('export-dropdown').value;
    var filename = filetype === 'csv' ? 'payles.csv' : 'payles.xlsx';

    var workbook = XLSX.utils.table_to_book(table, {sheet: "Budget", raw: true});
    if (filetype === 'csv') {
        XLSX.writeFile(workbook, filename, {bookType: 'csv'});
    } else {
        XLSX.writeFile(workbook, filename);
    }
}


function disableInputsExcept(exceptions=[]) {
    document.querySelectorAll('input, button, select, textarea').forEach(el => {
        if (!exceptions.includes(el)) {
            el.disabled = true;
        }
    });
}


function enableAllInputs() {
    document.querySelectorAll('input, button, select, textarea').forEach(el => {
        el.disabled = false;
    });
}


function getBudgetValue(rowHeader, colMonth) {
    if (!window.BUDGET_DATA) return '';
    
    const row = window.BUDGET_DATA.find(r => r.header === rowHeader);

    if (row && row.hasOwnProperty(colMonth)) {
        return row[colMonth];
    }
    return '';
}


function extractMonthHeaders() {
    const differenceRow = window.BUDGET_DATA.find(r => r.header === "Difference");
    return Object.keys(differenceRow).filter(k => k !== "header");
}


function disableTSPRateButtons() {
    const months = extractMonthHeaders();
    months.forEach(month => {
        const tradBase = getBudgetValue('Trad TSP Base Rate', month);
        const rothBase = getBudgetValue('Roth TSP Base Rate', month);

        const tradRows = [
            'Trad TSP Specialty Rate',
            'Trad TSP Incentive Rate',
            'Trad TSP Bonus Rate'
        ];
        const rothRows = [
            'Roth TSP Specialty Rate',
            'Roth TSP Incentive Rate',
            'Roth TSP Bonus Rate'
        ];

        tradRows.forEach(row => {
            const btn = document.querySelector(`.cell-button[data-row="${row}"][data-col="${month}"]`);
            if (btn) btn.disabled = (parseInt(tradBase, 10) === 0);
        });
        rothRows.forEach(row => {
            const btn = document.querySelector(`.cell-button[data-row="${row}"][data-col="${month}"]`);
            if (btn) btn.disabled = (parseInt(rothBase, 10) === 0);
        });
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