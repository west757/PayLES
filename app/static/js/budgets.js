// confirmation alert to user before changing pages when budgets.html is loaded
function payUnloadPrompt(e) {
    e.preventDefault();
    e.returnValue = "Please confirm to return to the home page. You will lose all existing data on this page and will be unable to return. \n\nTo save a copy of your budget, please use the export function.";
}


    // edit service information (branch, component, grade)
    // edit stationed location (zip code, military housing area, mha code, OCONUS locality code, oconus locality, oconus territory)
    // edit home of record
    // edit dependents (dependents)
    // edit tax filing status (federal filing status, state filing status)
    // edit sgli coverage (sgli coverage, sgli rate)
    // edit combat zone
    // edit drills
    // edit tsp rates


function openEditModal(header, month, value, field) {
    const modalEdit = document.getElementById('modal-edit');
    modalEdit.checked = true;

    const modalContentEdit = document.getElementById('modal-content-edit');
    modalContentEdit.innerHTML = '';

    // small helper to build a labeled row: label on left, inputElement on right
    function buildRow(labelText, inputElement) {
        const row = document.createElement('div');
        row.className = 'modal-row';

        const label = document.createElement('div');
        label.className = 'modal-label';
        label.textContent = labelText;

        const inputWrap = document.createElement('div');
        inputWrap.className = 'modal-input';
        inputWrap.appendChild(inputElement);

        row.appendChild(label);
        row.appendChild(inputWrap);
        return row;
    }

    // create a select from options array (options may be array of strings or objects)
    function createSelect(options, current) {
        const sel = document.createElement('select');
        sel.className = 'input-long';
        if (Array.isArray(options)) {
            options.forEach(opt => {
                const optionEl = document.createElement('option');
                if (opt && typeof opt === 'object') {
                    optionEl.value = opt.abbr ?? opt.longname ?? JSON.stringify(opt);
                    optionEl.textContent = opt.longname ?? opt.abbr ?? optionEl.value;
                } else {
                    optionEl.value = opt;
                    optionEl.textContent = opt;
                }
                if (String(optionEl.value) === String(current)) optionEl.selected = true;
                sel.appendChild(optionEl);
            });
        }
        return sel;
    }

    // top-centered month
    const monthLong = getRowValue('pay', 'Month Long', month);
    const monthTop = document.createElement('div');
    monthTop.className = 'modal-month';
    monthTop.textContent = monthLong;
    modalContentEdit.appendChild(monthTop);

    // build title depending on header (exact matches)
    let modalTitleText = `Editing ${header}`;

    // containers for rows
    const rowsContainer = document.createElement('div');
    rowsContainer.id = 'modal-rows-container';

    if (header === 'Branch' || header === 'Component' || header === 'Grade') {
        modalTitleText = 'Edit Service Information';

        const branchOptions = window.CONFIG && window.CONFIG.BRANCHES ? window.CONFIG.BRANCHES : [];
        const branchCurrent = getRowValue('pay', 'Branch', month);
        const branchSelect = createSelect(branchOptions, branchCurrent);
        rowsContainer.appendChild(buildRow('Branch:', branchSelect));

        const componentOptions = window.CONFIG && window.CONFIG.COMPONENTS ? window.CONFIG.COMPONENTS : [];
        const componentCurrent = getRowValue('pay', 'Component', month);
        const componentSelect = createSelect(componentOptions, componentCurrent);
        rowsContainer.appendChild(buildRow('Component:', componentSelect));

        const gradeOptions = window.CONFIG && window.CONFIG.GRADES ? window.CONFIG.GRADES : [];
        const gradeCurrent = getRowValue('pay', 'Grade', month);
        const gradeSelect = createSelect(gradeOptions, gradeCurrent);
        rowsContainer.appendChild(buildRow('Grade:', gradeSelect));

    } else if (header === 'Zip Code' || header === 'OCONUS Locality Code') {
        modalTitleText = 'Edit Location Stationed';

        const zipcodeInput = document.createElement('input');
        zipcodeInput.type = 'text';
        zipcodeInput.value = getRowValue('pay', 'Zip Code', month) || '';
        zipcodeInput.className = 'input-short';
        zipcodeInput.placeholder = 'e.g., 12345';
        rowsContainer.appendChild(buildRow('Zip Code:', zipcodeInput));

        const oconusOptions = (window.CONFIG && window.CONFIG.MHA_ZIP_CODES) ? window.CONFIG.MHA_ZIP_CODES : [];
        const oconusCurrent = getRowValue('pay', 'OCONUS Locality Code', month);
        const oconusSelect = createSelect(oconusOptions, oconusCurrent);
        rowsContainer.appendChild(buildRow('OCONUS Locality Code:', oconusSelect));

    } else if (header === 'Federal Filing Status' || header === 'State Filing Status') {
        modalTitleText = 'Edit Tax Filing Status';

        const federalFilingStatusOptions = window.CONFIG && window.CONFIG.TAX_FILING_STATUSES ? window.CONFIG.TAX_FILING_STATUSES : [];
        const federalFilingStatusCurrent = getRowValue('pay', 'Federal Filing Status', month);
        const federalFilingStatusSelect = createSelect(federalFilingStatusOptions, federalFilingStatusCurrent);
        rowsContainer.appendChild(buildRow('Federal Filing Status:', federalFilingStatusSelect));

        const stateFilingStatusOptions = window.CONFIG && window.CONFIG.HOME_OF_RECORDS ? window.CONFIG.HOME_OF_RECORDS : [];
        const stateFilingStatusCurrent = getRowValue('pay', 'State Filing Status', month);
        const stateFilingStatusSelect = createSelect(stateFilingStatusOptions, stateFilingStatusCurrent);
        rowsContainer.appendChild(buildRow('State Filing Status:', stateFilingStatusSelect));

    } else if (header === 'SGLI Coverage') {
        modalTitleText = 'Edit SGLI Coverage';

        const sgliCoverageOptions = window.CONFIG && window.CONFIG.SGLI_COVERAGE_OPTIONS ? window.CONFIG.SGLI_COVERAGE_OPTIONS : [];
        const sgliCoverageCurrent = getRowValue('pay', 'SGLI Coverage', month);
        const sgliCoverageSelect = createSelect(sgliCoverageOptions, sgliCoverageCurrent);
        rowsContainer.appendChild(buildRow('SGLI Coverage:', sgliCoverageSelect));

    } else {
        modalTitleText = `Editing ${header}`;
        const inputWrapper = createStandardInput(header, field, value);
        const singleRow = document.createElement('div');
        singleRow.style.marginTop = '1rem';
        singleRow.appendChild(inputWrapper);
        rowsContainer.appendChild(singleRow);
    }

    // Title left-aligned
    const modalHeader = document.createElement('h2');
    modalHeader.className = 'modal-title-left';
    modalHeader.textContent = modalTitleText;
    modalContentEdit.appendChild(modalHeader);

    // Append rows container
    modalContentEdit.appendChild(rowsContainer);

    // buttons (preserve existing)
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
        document.getElementById('modal-edit').checked = false;
    };
    buttonsEdit.appendChild(buttonCancel);

    modalContentEdit.appendChild(buttonsEdit);
}


// submit handler for modal edit
function submitEditModal(header, month, field, repeat) {
    const input = document.querySelector('#modal-content-edit input, #modal-content-edit select');
    const value = input.value;

    if (!validateInput(field, header, value, repeat)) return;

    document.getElementById('modal-edit').checked = false;

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
