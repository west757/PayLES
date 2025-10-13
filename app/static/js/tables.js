// confirmation alert to user before changing pages when tables.html is loaded
function budgetUnloadPrompt(e) {
    e.preventDefault();
    e.returnValue = "Please confirm to return to the home page. You will lose all existing data on this page and will be unable to return. \n\nTo save a copy of your budget, please use the export function.";
}


// opens modal for editing cell
function openEditModal(header, month, value, field) {
    const modalCheckbox = document.getElementById('modal-edit');
    modalCheckbox.checked = true;

    const editContainer = document.getElementById('modal-content-edit');
    editContainer.innerHTML = '';

    const title = document.createElement('h2');
    title.textContent = `Editing ${header} for ${month}`;
    editContainer.appendChild(title);

    const currentValueDiv = document.createElement('div');
    currentValueDiv.style.marginBottom = '1rem';
    currentValueDiv.innerHTML = `<strong>Current:</strong> ${formatValue(value)}`;
    editContainer.appendChild(currentValueDiv);

    const futureValueDiv = document.createElement('div');
    futureValueDiv.style.marginBottom = '1rem';
    futureValueDiv.innerHTML = `<strong>Future:</strong>`;

    const inputWrapper = createStandardInput(header, field, value);

    futureValueDiv.appendChild(inputWrapper);
    editContainer.appendChild(futureValueDiv);

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'editing-buttons';

    const onetimeButton = document.createElement('button');
    onetimeButton.textContent = 'One-Time Change';
    onetimeButton.classList.add('button-generic', 'button-positive');
    onetimeButton.onclick = function() {
        submitEditModal(header, month, field, false);
    };

    const repeatButton = document.createElement('button');
    repeatButton.textContent = 'Repeat Change';
    repeatButton.classList.add('button-generic', 'button-positive');
    repeatButton.onclick = function() {
        submitEditModal(header, month, field, true);
    };

    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.classList.add('button-generic', 'button-negative');
    cancelButton.onclick = function() {
        document.getElementById('modal-edit').checked = false;
    };

    buttonContainer.appendChild(onetimeButton);
    buttonContainer.appendChild(repeatButton);
    buttonContainer.appendChild(cancelButton);

    editContainer.appendChild(buttonContainer);

    // Store current edit info for validation
    window.currentEditModal = { header, month, field };
}


// Submit handler for modal edit
function submitEditModal(header, month, field, repeat) {
    const input = document.querySelector('#edit-container input, #edit-container select');
    const value = input.value;

    if (!validateInput(field, header, value, repeat)) return;

    document.getElementById('modal-edit').checked = false;

    htmx.ajax('POST', '/route_update_cell', {
        target: '#tables',
        swap: 'innerHTML',
        values: {
            header: header,
            month: month,
            value: value,
            repeat: repeat
        }
    });
}


// highlight changes in table compared to previous month
function highlightChanges(tableName) {
    const highlight_color = getComputedStyle(document.documentElement).getPropertyValue('--highlight_yellow_color').trim();
    let checkbox, table;

    if (tableName === 'budget') {
        checkbox = document.getElementById('checkbox-highlight-budget');
        table = document.getElementById('budget-table');
    } else if (tableName === 'tsp') {
        checkbox = document.getElementById('checkbox-highlight-tsp');
        table = document.getElementById('tsp-table');
    }

    var rows = table.getElementsByTagName('tr');

    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName('td');
        var header = cells[0].textContent.trim();

        //start from month 3 (index 2), skip row header and first month
        for (var j = 2; j < cells.length; j++) {
            var cell = cells[j];
            var prevCell = cells[j - 1];

            if (
                checkbox.checked &&
                cell.textContent.trim() !== prevCell.textContent.trim() &&
                !(header === "Difference" && cell.textContent.trim() === "$0.00")
            ) {
                cell.style.backgroundColor = highlight_color;
            } else {
                cell.style.backgroundColor = '';
            }
        }
    }
}


// toggle display of rows
function toggleRows(rowClass) {
    let checkbox, rows;

    if (rowClass === 'variables') {
        checkbox = document.getElementById('checkbox-variables');
        rows = document.getElementsByClassName('row-variable');
    } else if (rowClass === 'tsp-rates') {
        checkbox = document.getElementById('checkbox-tsp-rates');
        rows = document.getElementsByClassName('row-tsp-rate');
    }

    for (let row of rows) {
        row.style.display = checkbox.checked ? 'table-row' : 'none';
    }
}


// export table to xlsx or csv using SheetJS
function exportTable(tableName) {
    let filename;

    if (tableName === 'budget') {
        var table = document.getElementById('budget-table');
        var filetype = document.getElementById('dropdown-export-budget').value;
        filename = 'PayLES_Budget';
    } else if (tableName === 'tsp') {
        var table = document.getElementById('tsp-table');
        var filetype = document.getElementById('dropdown-export-tsp').value;
        filename = 'PayLES_TSP';
    }

    var fullFilename = filetype === 'xlsx' ? filename + '.xlsx' : filename + '.csv';

    var clone = table.cloneNode(true);

    // exclude remove row buttons from export
    clone.querySelectorAll('.button-remove-row').forEach(btn => btn.remove());

    var workbook = XLSX.utils.table_to_book(clone, {sheet: filename, raw: true});
    if (filetype === 'xlsx') {
        XLSX.writeFile(workbook, fullFilename);
    } else {
        XLSX.writeFile(workbook, fullFilename, {bookType: 'csv'});
    }
}


function disableTSPRateButtons() {
    const months = window.CONFIG.months;
    months.forEach(month => {
        const tradBase = getRowValue('tsp', 'Trad TSP Base Rate', month);
        const rothBase = getRowValue('tsp', 'Roth TSP Base Rate', month);

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


function disableDrillsButtons() {
    const months = window.CONFIG.months;
    months.forEach(month => {
        const component = getRowValue('budget', 'Component', month);
        const btn = document.querySelector(`.cell-button[data-row="Drills"][data-month="${month}"]`);
        if (btn) {
            btn.disabled = !(component === 'NG' || component === 'RES');
        }
    });
}







// editing states
let isEditing = false;
let currentEdit = null;


function validateInput(field, header, value, repeat = false) {
    if (value === '' || value === null || value === undefined) {
        showToast('A value must be entered.');
        return false;
    }

    if (field === 'int') {
        let num = parseInt(value, 10);
        if (isNaN(num)) {
            showToast('Value must be a number.');
            return false;
        }
        if (header.toLowerCase().includes('tsp rate') && (num < 0 || num > 100)) {
            showToast('TSP rate must be between 0 and 100.');
            return false;
        }
        if (value.length > 3) {
            showToast('Value must be at most 3 digits.');
            return false;
        }
    }

    if (field === 'float') {
        if (!/^\d{0,4}(\.\d{0,2})?$/.test(value)) {
            showToast('Value must be a decimal with up to 4 digits before and 2 after the decimal.');
            return false;
        }
        if (value.length > 7) {
            showToast('Value must be at most 7 characters.');
            return false;
        }
    }
    
    if (header === 'Zip Code') {
        if (!/^\d{5}$/.test(value)) {
            showToast('Zip code must be exactly 5 digits.');
            return false;
        }
    }


    // TSP base rate validation
    if (header === 'Trad TSP Base Rate') {
        if (value > window.CONFIG.TRAD_TSP_RATE_MAX) {
            showToast(`Trad TSP Base Rate cannot be more than ${window.CONFIG.TRAD_TSP_RATE_MAX}.`);
            return false;
        }

        const month = currentEdit.month;
        const rows = [
            'Trad TSP Specialty Rate',
            'Trad TSP Incentive Rate',
            'Trad TSP Bonus Rate'
        ];

        for (let r of rows) {
            const v = getRowValue('budget', r, month);
            if (parseInt(v, 10) > 0 && value === 0) {
                showToast('Cannot set Trad TSP Base Rate to 0 while a specialty/incentive/bonus rate is greater than 0%.');
                return false;
            }
        }
    }

    if (header === 'Roth TSP Base Rate') {
        if (value > window.CONFIG.ROTH_TSP_RATE_MAX) {
            showToast(`Roth TSP Base Rate cannot be more than ${window.CONFIG.ROTH_TSP_RATE_MAX}.`);
            return false;
        }

        const month = currentEdit.month;
        const rows = [
            'Roth TSP Specialty Rate',
            'Roth TSP Incentive Rate',
            'Roth TSP Bonus Rate'
        ];

        for (let r of rows) {
            const v = getRowValue('budget', r, month);
            if (parseInt(v, 10) > 0 && value === 0) {
                showToast('Cannot set Roth TSP Base Rate to 0 while a specialty/incentive/bonus rate is greater than 0%.');
                return false;
            }
        }

    }

    if (
        header.includes('Specialty Rate') ||
        header.includes('Incentive Rate') ||
        header.includes('Bonus Rate')
    ) {
        if (value > 100) {
            showToast('Specialty/Incentive/Bonus Rate cannot be more than 100%.');
            return false;
        }
        if (header.startsWith('Trad') && getRowValue('tsp', 'Trad TSP Base Rate', currentEdit.month) === 0) {
            showToast('Cannot set Trad TSP Specialty/Incentive/Bonus Rate if base rate is 0%.');
            return false;
        }
        if (header.startsWith('Roth') && getRowValue('tsp', 'Roth TSP Base Rate', currentEdit.month) === 0) {
            showToast('Cannot set Roth TSP Specialty/Incentive/Bonus Rate if base rate is 0%.');
            return false;
        }
    }

    
    if (repeat && (header.includes('Specialty Rate') || header.includes('Incentive Rate') || header.includes('Bonus Rate'))) {
        const months = window.CONFIG.months;
        const startIdx = months.indexOf(currentEdit.month);
        const baseRow = header.startsWith('Trad') ? 'Trad TSP Base Rate' : 'Roth TSP Base Rate';
        console.log('Repeat validation:', months.slice(startIdx), baseRow);
        for (let i = startIdx; i < months.length; i++) { // Only future months
            const baseRate = getRowValue('tsp', baseRow, months[i]);
            if (parseInt(baseRate, 10) === 0) {
                showToast(`Cannot repeat specialty/incentive/bonus rate into months where base rate is 0% (${months[i]}).`);
                return false;
            }
        }
    }

    if (header.includes('TSP Base Rate') || header.includes('Specialty Rate') || header.includes('Incentive Rate') || header.includes('Bonus Rate')) {
        const month = currentEdit.month;
        let tradValue = 0, rothValue = 0;

        if (header.startsWith('Trad')) {
            tradValue = parseInt(value, 10);
            if (header.includes('Base Rate')) rothValue = parseInt(getRowValue('tsp', 'Roth TSP Base Rate', month), 10);
            if (header.includes('Specialty Rate')) rothValue = parseInt(getRowValue('tsp', 'Roth TSP Specialty Rate', month), 10);
            if (header.includes('Incentive Rate')) rothValue = parseInt(getRowValue('tsp', 'Roth TSP Incentive Rate', month), 10);
            if (header.includes('Bonus Rate')) rothValue = parseInt(getRowValue('tsp', 'Roth TSP Bonus Rate', month), 10);
        } else if (header.startsWith('Roth')) {
            rothValue = parseInt(value, 10);
            if (header.includes('Base Rate')) tradValue = parseInt(getRowValue('tsp', 'Trad TSP Base Rate', month), 10);
            if (header.includes('Specialty Rate')) tradValue = parseInt(getRowValue('tsp', 'Trad TSP Specialty Rate', month), 10);
            if (header.includes('Incentive Rate')) tradValue = parseInt(getRowValue('tsp', 'Trad TSP Incentive Rate', month), 10);
            if (header.includes('Bonus Rate')) tradValue = parseInt(getRowValue('tsp', 'Trad TSP Bonus Rate', month), 10);
        }

        if ((tradValue + rothValue) > 100) {
            showToast('Combined Traditional and Roth TSP rates for this type cannot exceed 100%.');
            return false;
        }
    }

    return true;
}



function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    const badge = document.getElementById('badge-recommendations');

    if (recommendations.length > 0) {
        container.innerHTML = recommendations.map(r => `<div class="modal-list-text">${r}</div>`).join('');
        badge.textContent = recommendations.length;
        badge.style.display = 'inline-block';
    } else {
        container.innerHTML = '<div class="modal-list-text">No current recommendations for your budget.</div>';
        badge.style.display = 'none';
    }
}


function getDiscrepancyMessage(header) {
    const messages = {
        'SGLI Rate': "There is a discrepancy with the SGLI Rate. This sometimes happens when the SGLI rate dataset has not been recently updated.",
        'BAH': "There is a discrepancy with the BAH. This may be due to recent changes in locality rates.",
        'Federal Taxes': "There is a discrepancy with Federal Taxes. This may be due to differences in withholding or filing status.",
    };
    return messages[header] || null;
}

function displayDiscrepanciesModal(discrepancies) {
    const tableContainer = document.getElementById('discrepancies-table-container');
    const messageContainer = document.getElementById('discrepancies-message-container');
    const badge = document.getElementById('badge-discrepancies');

    if (!discrepancies || discrepancies.length === 0) {
        tableContainer.innerHTML = '<div class="modal-list-text">PayLES has analyzed your budget and found no discrepancies.</div>';
        messageContainer.innerHTML = '';
        badge.style.display = 'none';
        return;
    }

    let tableHTML = `<table class="modal-table">
        <tr>
            <td>Header</td>
            <td>Value from LES</td>
            <td>Calculated Value</td>
        </tr>`;
    let messages = [];

    discrepancies.forEach(row => {
        tableHTML += `<tr>
            <td>${row.header}</td>
            <td>${formatValue(row.les_value)}</td>
            <td>${formatValue(row.calc_value)}</td>
        </tr>`;
        const msg = getDiscrepancyMessage(row.header);
        if (msg) messages.push(`<div class="modal-list-text">${msg}</div>`);
    });

    tableHTML += `</table>
        <div class="modal-list-text">PayLES found these discrepancies.</div>`;

    badge.textContent = discrepancies.length;
    badge.style.display = 'inline-block';

    tableContainer.innerHTML = tableHTML;
    messageContainer.innerHTML = messages.join('');
}
