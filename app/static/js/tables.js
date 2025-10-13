// confirmation alert to user before changing pages when tables.html is loaded
function budgetUnloadPrompt(e) {
    e.preventDefault();
    e.returnValue = "Please confirm to return to the home page. You will lose all existing data on this page and will be unable to return. \n\nTo save a copy of your budget, please use the export function.";
}


// opens modal for editing cell
function openEditModal(header, month, value, field) {
    const modalCheckbox = document.getElementById('modal-edit');
    modalCheckbox.checked = true;

    const editContainer = document.getElementById('edit-container');
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
    buttonContainer.className = 'editingButtonContainer';

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

    // remove row buttons from export
    clone.querySelectorAll('.remove-row-button').forEach(btn => btn.remove());

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