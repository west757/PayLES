// confirmation alert to user before changing off budget page
function budgetUnloadPrompt(e) {
    e.preventDefault();
    e.returnValue = "Please confirm to return to the home page. You will lose all existing data on this page and will be unable to return. \n\nTo save a copy of your budget, please use the export function.";
}


// show toast messages for 6 seconds and 0.5 second fade transition
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


function showTooltip(evt, text) {
    const tooltip = document.getElementById('tooltip');
    if (!tooltip) return;
    tooltip.innerText = text;
    tooltip.style.left = (evt.pageX + 16) + 'px';
    tooltip.style.top = (evt.pageY - 16) + 'px';
    tooltip.style.display = 'block';
}


function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    if (!tooltip) return;
    tooltip.style.display = 'none';
}


function disableInputs(exceptions=[]) {
    // disable all inputs except those in exceptions array
    document.querySelectorAll('input, button, select, textarea').forEach(el => {
        if (!exceptions.includes(el)) {
            el.disabled = true;
        }
    });
}


function enableInputs() {
    document.querySelectorAll('input, button, select, textarea').forEach(el => {
        el.disabled = false;
    });
}


function highlightChanges() {
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
        
        //start from month 3 (index 2), skip row header and first month
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


function showAllVariables() {
    var checkbox = document.getElementById('show-all-variables-checkbox');
    var checked = checkbox.checked;
    var rows = document.getElementsByClassName('var-row');
    
    for (var row of rows) {
        if (checked) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    }
}


function showTSPOptions() {
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


function showYTDRows() {
    var checkbox = document.getElementById('show-ytd-rows-checkbox');
    var checked = checkbox.checked;
    var rows = document.getElementsByClassName('ytd-row');

    for (var row of rows) {
        if (checked) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    }
}


function exportBudget() {
    var table = document.getElementById('budget-table');
    var filetype = document.getElementById('export-dropdown').value;
    var filename = filetype === 'csv' ? 'PayLES_Budget.csv' : 'PayLES_Budget.xlsx';

    var clone = table.cloneNode(true);

    // remove row buttons from export
    clone.querySelectorAll('.remove-row-button').forEach(btn => btn.remove());

    var workbook = XLSX.utils.table_to_book(clone, {sheet: "Budget", raw: true});
    if (filetype === 'csv') {
        XLSX.writeFile(workbook, filename, {bookType: 'csv'});
    } else {
        XLSX.writeFile(workbook, filename);
    }
}


function getBudgetValue(rowHeader, month) {
    const row = window.CONFIG.budget.find(r => r.header === rowHeader);

    if (row && row.hasOwnProperty(month)) {
        return row[month];
    }
    return '';
}


function disableTSPRateButtons() {
    const months = window.CONFIG.months;
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
            const btn = document.querySelector(`.cell-button[data-row="${row}"][data-month="${month}"]`);
            if (btn) btn.disabled = (parseInt(tradBase, 10) === 0);
        });
        rothRows.forEach(row => {
            const btn = document.querySelector(`.cell-button[data-row="${row}"][data-month="${month}"]`);
            if (btn) btn.disabled = (parseInt(rothBase, 10) === 0);
        });
    });
}


function setInputRestriction(fieldType, maxLength = null) {
    // input restrictions for money inputs
    if (fieldType === 'money') {
        return function(e) {
            let val = e.target.value.replace(/[^0-9.]/g, '');
            let parts = val.split('.');
            if (parts.length > 2) {
                val = parts[0] + '.' + parts.slice(1).join('');
            }
            if (parts[0].length > 4) {
                parts[0] = parts[0].slice(0, 4);
            }
            if (parts.length > 1 && parts[1].length > 2) {
                parts[1] = parts[1].slice(0, 2);
            }
            val = parts.length > 1 ? parts[0] + '.' + parts[1] : parts[0];
            if (val.startsWith('00')) {
                val = val.replace(/^0+/, '0');
            } else if (val.startsWith('0') && val.length > 1 && val[1] !== '.') {
                val = val.replace(/^0+/, '');
            }
            if (val.length > 7) {
                val = val.slice(0, 7);
            }
            e.target.value = val;
        };
    }

    // input restrictions for only number inputs
    if (fieldType === 'number') {
        return function(e) {
            let val = e.target.value.replace(/\D/g, '');
            if (maxLength && val.length > maxLength) {
                val = val.slice(0, maxLength);
            }
            e.target.value = val;
        };
    }

    // input restrictions for text inputs
    if (fieldType === 'text') {
        return function(e) {
            let val = e.target.value.replace(/[^A-Za-z0-9_\- ]/g, '');
            if (maxLength && val.length > maxLength) {
                val = val.slice(0, maxLength);
            }
            e.target.value = val;
        };
    }

    return function(e) {};
}

