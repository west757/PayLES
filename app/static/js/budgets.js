// confirmation alert to user before changing pages when budgets.html is loaded
function payUnloadPrompt(e) {
    e.preventDefault();
    e.returnValue = "Please confirm to return to the home page. You will lose all existing data on this page and will be unable to return. \n\nTo save a copy of your budget, please use the export function.";
}


function buildEditModal(header, month, field) {
    document.getElementById('modal-dynamic').checked = true;

    const modalContentDynamic = document.getElementById('modal-content-dynamic');
    modalContentDynamic.innerHTML = '';

    const monthLong = getRowValue('pay', 'Month Long', month);
    let modalTitle;
    const modalEditInputs = document.createElement('div');
    modalEditInputs.id = 'modal-edit-inputs';

    if (header === 'Branch' || header === 'Component' || header === 'Grade') {
        modalTitle = `Service Information - ${monthLong}`;
        modalEditInputs.appendChild(addModalDynamicLine('Branch:', createStandardInput('Branch', 'select', getRowValue('pay', 'Branch', month))));
        modalEditInputs.appendChild(addModalDynamicLine('Component:', createStandardInput('Component', 'select', getRowValue('pay', 'Component', month))));
        modalEditInputs.appendChild(addModalDynamicLine('Grade:', createStandardInput('Grade', 'select', getRowValue('pay', 'Grade', month))));

    } else if (header === 'Zip Code' || header === 'OCONUS Locality Code') {
        modalTitle = `Location Stationed - ${monthLong}`;
        modalEditInputs.appendChild(addModalDynamicLine('Zip Code:', createStandardInput('Zip Code', 'string', getRowValue('pay', 'Zip Code', month))));
        modalEditInputs.appendChild(addModalDynamicLine('OCONUS Locality Code:', createStandardInput('OCONUS Locality Code', 'select', getRowValue('pay', 'OCONUS Locality Code', month))));

    } else if (header === 'Federal Filing Status' || header === 'State Filing Status') {
        modalTitle = `Tax Filing Status - ${monthLong}`;
        modalEditInputs.appendChild(addModalDynamicLine('Federal Filing Status:', createStandardInput('Federal Filing Status', 'select', getRowValue('pay', 'Federal Filing Status', month))));
        modalEditInputs.appendChild(addModalDynamicLine('State Filing Status:', createStandardInput('State Filing Status', 'select', getRowValue('pay', 'State Filing Status', month))));

    } else if (header === 'SGLI Coverage') {
        modalTitle = `SGLI Coverage - ${monthLong}`;
        modalEditInputs.appendChild(addModalDynamicLine('SGLI Coverage:', createStandardInput('SGLI Coverage', 'select', getRowValue('pay', 'SGLI Coverage', month))));

    } else {
        modalTitle = `${header} - ${monthLong}`;
        modalEditInputs.appendChild(addModalDynamicLine(header + ':', createStandardInput(header, field, getRowValue('pay', header, month))));
    }

    const modalHeader = document.createElement('h2');
    modalHeader.textContent = modalTitle;
    modalContentDynamic.appendChild(modalHeader);
    modalContentDynamic.appendChild(modalEditInputs);

    const buttonsEdit = document.createElement('div');
    buttonsEdit.className = 'buttons-edit';

    const buttonOnetime = document.createElement('button');
    buttonOnetime.textContent = 'One-Time';
    buttonOnetime.classList.add('button-generic', 'button-positive', 'button-edit');
    buttonOnetime.onclick = function() {
        submitEditModal(header, month, field, repeat=false);
    };
    buttonsEdit.appendChild(buttonOnetime);

    const buttonRepeat = document.createElement('button');
    buttonRepeat.textContent = 'Repeat';
    buttonRepeat.classList.add('button-generic', 'button-positive', 'button-edit');
    buttonRepeat.onclick = function() {
        submitEditModal(header, month, field, repeat=true);
    };
    buttonsEdit.appendChild(buttonRepeat);

    const buttonCancel = document.createElement('button');
    buttonCancel.textContent = 'Cancel';
    buttonCancel.classList.add('button-generic', 'button-negative', 'button-edit');
    buttonCancel.onclick = function() {
        document.getElementById('modal-dynamic').checked = false;
    };
    buttonsEdit.appendChild(buttonCancel);

    modalContentDynamic.appendChild(buttonsEdit);
}


// submit handler for modal edit
function submitEditModal(header, month, field, repeat) {
    const input = document.querySelector('#modal-content-dynamic input, #modal-content-dynamic select');
    const value = input.value;

    if (!validateInput(field, header, value, repeat)) return;

    document.getElementById('modal-dynamic').checked = false;

    htmx.ajax('POST', '/route_update_cell', {
        target: '#budgets',
        swap: 'innerHTML',
        values: {
            header: header,
            month: month,
            value: value,
            repeat: repeat
        }
    });
}


// highlight changes in budget compared to previous month
function highlightChanges(budgetName) {
    const highlight_color = getComputedStyle(document.documentElement).getPropertyValue('--highlight_yellow_color').trim();
    let checkbox, budget;

    if (budgetName === 'pay') {
        checkbox = document.getElementById('checkbox-highlight-pay');
        budget = document.getElementById('budget-pay');
    } else if (budgetName === 'tsp') {
        checkbox = document.getElementById('checkbox-highlight-tsp');
        budget = document.getElementById('budget-tsp');
    }

    var rows = budget.getElementsByTagName('tr');

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





let accountDepositInitial = 0.0;
let accountDepositInterest = 0;
let accountTSPInitial = 0.0;
let accountTSPInterest = 0;

function buildAccountModal(accountName) {
    document.getElementById('modal-dynamic').checked = true;

    if (accountName === 'Direct Deposit Account') {
        budget = document.getElementById('budget-pay');
        initial = accountDepositInitial;
        interest = accountDepositInterest;
    } else if (accountName === 'TSP Account') {
        budget = document.getElementById('budget-tsp');
        initial = accountTSPInitial;
        interest = accountTSPInterest;
    }

    modalTitle = "Edit " + accountName;

    const modalContentDynamic = document.getElementById('modal-content-dynamic');
    modalContentDynamic.innerHTML = '';

    const modalContentDynamicLine = document.createElement('div');
    modalContentDynamicLine.id = 'modal-content-dynamic-line';

    modalContentDynamicLine.appendChild(addModalDynamicLine('Initial Value:', createStandardInput('Initial Value', 'float', initial)));
    modalContentDynamicLine.appendChild(addModalDynamicLine('Interest Rate:', createStandardInput('Interest Rate', 'int', interest)));

    const modalHeader = document.createElement('h2');
    modalHeader.textContent = modalTitle;
    modalContentDynamic.appendChild(modalHeader);
    modalContentDynamic.appendChild(modalEditInputs);

    const buttonsEdit = document.createElement('div');
    buttonsEdit.className = 'buttons-edit';

    const buttonUpdate = document.createElement('button');
    buttonUpdate.textContent = 'Update';
    buttonUpdate.classList.add('button-generic', 'button-positive', 'button-edit');
    buttonUpdate.onclick = function () {
        submitAccountModal(budgetName, initial, interest);
    };
    buttonsEdit.appendChild(buttonUpdate);

    const buttonCancel = document.createElement('button');
    buttonCancel.textContent = 'Cancel';
    buttonCancel.classList.add('button-generic', 'button-negative', 'button-edit');
    buttonCancel.onclick = function () {
        document.getElementById('modal-dynamic').checked = false;
    };
    buttonsEdit.appendChild(buttonCancel);

    modalContentDynamic.appendChild(buttonsEdit);
}



function submitAccountModal(budgetName, initial, interest) {
    if (!validateInput('float', 'Account Initial Value', initial)) return;
    if (!validateInput('int', 'Account Interest Rate', interest)) return;

    document.getElementById('modal-dynamic').checked = false;

    htmx.ajax('POST', '/route_update_account', {
        target: '#budgets',
        swap: 'innerHTML',
        values: {
            budgetName: budgetName,
            initial: initial,
            interest: interest
        }
    });
}




// export budget to xlsx or csv using SheetJS
function exportBudget(budgetName) {
    let filename;

    if (budgetName === 'pay') {
        var budget = document.getElementById('pay-budget');
        var filetype = document.getElementById('dropdown-export-pay').value;
        filename = 'PayLES_PAY_BUDGET';
    } else if (budgetName === 'tsp') {
        var budget = document.getElementById('tsp-budget');
        var filetype = document.getElementById('dropdown-export-tsp').value;
        filename = 'PayLES_TSP_BUDGET';
    }

    var fullFilename = filetype === 'xlsx' ? filename + '.xlsx' : filename + '.csv';

    var clone = budget.cloneNode(true);

    // exclude remove row buttons from export
    clone.querySelectorAll('.button-remove-row').forEach(btn => btn.remove());

    var workbook = XLSX.utils.budget_to_book(clone, {sheet: filename, raw: true});
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
        const component = getRowValue('pay', 'Component', month);
        const btn = document.querySelector(`.cell-button[data-row="Drills"][data-month="${month}"]`);
        if (btn) {
            btn.disabled = !(component === 'NG' || component === 'RES');
        }
    });
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
