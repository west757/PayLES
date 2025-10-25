// confirmation alert to user before changing pages when budgets.html is loaded
function budgetUnloadPrompt(e) {
    e.preventDefault();
    e.returnValue = "Please confirm to return to the home page. You will lose all existing data on this page and will be unable to return. \n\nTo save a copy of your budget, please use the export function.";
}


function buildEditModal(header, month, field) {
    openDynamicModal('short');

    const content = document.getElementById('modal-content-dynamic');
    content.innerHTML = '';

    const monthLong = getRowValue('pay', 'Month Long', month);
    const monthTitle = document.createElement('h2');
    monthTitle.textContent = monthLong;
    monthTitle.style.textAlign = 'center';
    content.appendChild(monthTitle);

    const row = getRowValue('pay', header);
    let type = null;
    if (row) {
        type = row.type ? row.type : null;
    }

    let headerTitleName = header;
    // if row is ent/ded/alt, use tooltip for title
    if (type === 'ent' || type === 'ded' || type === 'alt') {
        const headersList = window.CONFIG.headers || [];
        const meta = headersList.find(h => h.header === header);
        if (meta && meta.tooltip && meta.tooltip !== 'none') {
            headerTitleName = meta.tooltip;
        }
    }

    const headerTitle = document.createElement('h2');
    headerTitle.textContent = headerTitleName;
    headerTitle.style.textAlign = 'center';
    content.appendChild(headerTitle);

    let cancelOnly = false;
    const body = document.createElement('div');
    body.className = 'modal-dynamic-body';

    if (header === 'Drills') {
        const component = getRowValue('pay', 'Component', month);
        if (component !== 'NG' && component !== 'RES') {
            cancelOnly = true;
            body.textContent = 'You are currently not in the National Guard or Reserves component for this month. In order to set the number of drills, you must be in that component.';
        }
    }

    const rateSIBHeaders = [
        'Trad TSP Specialty Rate', 'Trad TSP Incentive Rate', 'Trad TSP Bonus Rate',
        'Roth TSP Specialty Rate', 'Roth TSP Incentive Rate', 'Roth TSP Bonus Rate'
    ];
    if (rateSIBHeaders.includes(header)) {
        let baseHeader = header.startsWith('Trad') ? 'Trad TSP Base Rate' : 'Roth TSP Base Rate';
        const baseRate = parseFloat(getRowValue('tsp', baseHeader, month));
        if (baseRate === 0) {
            cancelOnly = true;
            body.textContent = 'You cannot set a specialty/incentive/bonus rate when ' + baseHeader + ' is 0.';
        }
    }

    if (!cancelOnly) {
        body.appendChild(createStandardInput(header, field, getRowValue('pay', header, month)));
    }

    content.appendChild(body);

    const buttons = document.createElement('div');
    buttons.className = 'modal-dynamic-buttons';

    if (!cancelOnly) {
        const buttonOnetime = document.createElement('button');
        buttonOnetime.textContent = 'One-Time';
        buttonOnetime.classList.add('button-generic', 'button-positive');
        buttonOnetime.onclick = function() {
            submitEditModal(header, month, field, false);
        };
        buttons.appendChild(buttonOnetime);

        const buttonRepeat = document.createElement('button');
        buttonRepeat.textContent = 'Repeat';
        buttonRepeat.classList.add('button-generic', 'button-positive');
        buttonRepeat.onclick = function() {
            submitEditModal(header, month, field, true);
        };
        buttons.appendChild(buttonRepeat);
    }

    const buttonCancel = document.createElement('button');
    buttonCancel.textContent = 'Cancel';
    buttonCancel.classList.add('button-generic', 'button-negative');
    buttonCancel.onclick = function() {
        document.getElementById('modal-dynamic').checked = false;
    };
    buttons.appendChild(buttonCancel);

    content.appendChild(buttons);
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


function boldEditableCells(active) {
    const editableCells = document.querySelectorAll(
        '#budget-pay-table .button-modal-dynamic, #budget-tsp-table .button-modal-dynamic'
    );
    
    editableCells.forEach(cell => {
        if (active) {
            cell.style.fontWeight = 'bold';
        } else {
            cell.style.fontWeight = '';
        }
    });
}


function buildAccountModal(header) {
    openDynamicModal('short');

    if (header === 'Direct Deposit Account') {
        budget = document.getElementById('budget-pay');
        initial = getRowValue('pay', 'Direct Deposit Account', window.CONFIG.months[0]);
    } else if (header === 'TSP Account') {
        budget = document.getElementById('budget-tsp');
        initial = getRowValue('tsp', 'TSP Account', window.CONFIG.months[0]);
    }

    const content = document.getElementById('modal-content-dynamic');
    content.innerHTML = '';

    const title = document.createElement('h2');
    title.textContent = "Edit " + header;
    content.appendChild(title);

    const body = document.createElement('div');
    body.className = 'modal-dynamic-body';

    const inputLabel = document.createElement('p');
    inputLabel.textContent = 'Initial Value:';
    body.appendChild(inputLabel);
    body.appendChild(createStandardInput('Initial Value', 'float', initial));

    content.appendChild(body);

    const buttons = document.createElement('div');
    buttons.className = 'modal-dynamic-buttons';

    const buttonUpdate = document.createElement('button');
    buttonUpdate.textContent = 'Update';
    buttonUpdate.classList.add('button-generic', 'button-positive');
    buttonUpdate.onclick = function () {
        submitAccountModal(header);
    };
    buttons.appendChild(buttonUpdate);

    const buttonCancel = document.createElement('button');
    buttonCancel.textContent = 'Cancel';
    buttonCancel.classList.add('button-generic', 'button-negative');
    buttonCancel.onclick = function () {
        document.getElementById('modal-dynamic').checked = false;
    };
    buttons.appendChild(buttonCancel);

    content.appendChild(buttons);
}


function submitAccountModal(header) {
    const input = document.querySelector('#modal-content-dynamic input');
    const initial = input.value;

    if (!validateInput('float', 'Initial Value', initial)) return;

    document.getElementById('modal-dynamic').checked = false;

    htmx.ajax('POST', '/route_update_account', {
        target: '#budgets',
        swap: 'innerHTML',
        values: {
            header: header,
            initial: initial,
        }
    });
}


// export budget to xlsx or csv using SheetJS
function exportBudget(budgetName) {
    let filename;

    if (budgetName === 'pay') {
        var budget = document.getElementById('budget-pay-table');
        var filetype = document.getElementById('dropdown-export-pay').value;
        filename = 'PayLES_Budget';
    } else if (budgetName === 'tsp') {
        var budget = document.getElementById('budget-tsp-table');
        var filetype = document.getElementById('dropdown-export-tsp').value;
        filename = 'PayLES_TSP_Budget';
    }

    var fullFilename = filetype === 'xlsx' ? filename + '.xlsx' : filename + '.csv';

    var clone = budget.cloneNode(true);

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
            const btn = document.querySelector(`.cell-button[data-header="${row}"][data-month="${month}"]`);
            if (btn) btn.disabled = (parseInt(tradBase, 10) === 0);
        });
        rothRows.forEach(row => {
            const btn = document.querySelector(`.cell-button[data-header="${row}"][data-month="${month}"]`);
            if (btn) btn.disabled = (parseInt(rothBase, 10) === 0);
        });
    });
}


function disableDrillsButtons() {
    const months = window.CONFIG.months;
    months.forEach(month => {
        const component = getRowValue('pay', 'Component', month);
        const btn = document.querySelector(`.cell-button[data-header="Drills"][data-month="${month}"]`);
        if (btn) {
            btn.disabled = !(component === 'NG' || component === 'RES');
        }
    });
}


function displayRecommendations(budgetName, recommendations) {
    openDynamicModal('wide');

    if (budgetName === 'pay') {
        displayBadge('recommendations-pay', []);
    } else if (budgetName === 'tsp') {
        displayBadge('recommendations-tsp', []);
    }

    const content = document.getElementById('modal-content-dynamic');
    content.innerHTML = '';

    const titleText = budgetName === 'pay' ? 'Budget Recommendations' : 'TSP Recommendations';
    const title = document.createElement('h2');
    title.textContent = titleText;
    content.appendChild(title);

    const recommendationsList = document.createElement('div');
    if (recommendations.length > 0) {
        recommendations.forEach(r => {
            recommendationsList.className = 'modal-list-text';
            recommendationsList.textContent = r;
        });
    } else {
        recommendationsList.className = 'modal-list-text';
        recommendationsList.textContent = 'No current recommendations.';
        
    }
    content.appendChild(recommendationsList);
}


function getDiscrepancyMessage(header) {
    const messages = {
        'SGLI Rate': "There is a discrepancy with the SGLI Rate. This sometimes happens when the SGLI rate dataset has not been recently updated.",
        'BAH': "There is a discrepancy with the BAH. This may be due to recent changes in locality rates.",
        'Federal Taxes': "There is a discrepancy with Federal Taxes. This may be due to differences in withholding or filing status.",
    };
    return messages[header] || null;
}

function displayDiscrepancies(discrepancies) {
    openDynamicModal('wide');

    displayBadge('discrepancies', []);

    const content = document.getElementById('modal-content-dynamic');
    content.innerHTML = '';

    const titleText = 'Pay Discrepancies';
    const title = document.createElement('h2');
    title.textContent = titleText;
    content.appendChild(title);

    const description = document.createElement('p');
    description.innerHTML = 'PayLES performs analysis to find any discrepancies between the uploaded LES and calculated values for the first month. Factors that may cause a discrepancy are an LES older than one month, pay errors, outdated data sets used by PayLES, and certain specific individual circumstances.';
    content.appendChild(description);

    const tableContainer = document.createElement('div');
    tableContainer.id = 'discrepancies-table-container';
    content.appendChild(tableContainer);
    const messageContainer = document.createElement('div');
    messageContainer.id = 'discrepancies-message-container';
    content.appendChild(messageContainer);

    if (!discrepancies || discrepancies.length === 0) {
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

    tableContainer.innerHTML = tableHTML;
    messageContainer.innerHTML = messages.join('');
}
