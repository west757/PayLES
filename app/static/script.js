//constants and global variables
const DEFAULT_MONTHS_DISPLAY = 6;
const MAX_CUSTOM_ROWS = 9;
let editingIndex = null;
let customRows = [];
let customRowButtons = [];


// =========================
// drag and drop file upload
// =========================

(function() {
    var dropContainer = document.getElementById("home-drop");
    var fileInput = document.getElementById("home-input");
    var form = dropContainer.closest("form");

    if (!dropContainer || !fileInput || !form) return;

    //prevent default drag behaviors
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


// =========================
// update paydf and GUI
// =========================

function updatePaydf() {
    const optionsForm = document.getElementById('options-form');
    const settingsForm = document.getElementById('settings-form');
    const formData = new FormData(optionsForm);
    const monthsDropdown = settingsForm.querySelector('[name="months_display"]');
    formData.append('months_display', monthsDropdown.value);
    formData.append('custom_rows', JSON.stringify(customRows));

    fetch('/update_paydf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(html => {
        document.getElementById('paydf').innerHTML = html;
        editingIndex = null;
        highlight_changes();
        show_all_variables();
        show_all_options();
        updateButtonStates();
        renderCustomRowButtonTable();
        updateMonthDropdowns();
    });
}

function updateMonthDropdowns() {
    //get colHeaders from the data attribute
    const colHeaders = JSON.parse(document.getElementById('button-paydf-tables').dataset.colHeaders);
    //remove the first two column headers (row header and first month)
    const monthOptions = colHeaders.slice(2);

    document.querySelectorAll('select.month-dropdown').forEach(function(select) {
        const currentValue = select.value;
        select.innerHTML = '';
        monthOptions.forEach(function(month) {
            const option = document.createElement('option');
            option.value = month;
            option.textContent = month;
            if (month === currentValue) option.selected = true;
            select.appendChild(option);
        });
    });
}

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

function show_all_variables() {
    var checkbox = document.getElementById('show-all-variables-checkbox');
    var checked = checkbox.checked;
    var rows = document.getElementsByClassName('variable-row');
    for (var i = 0; i < rows.length; i++) {
        rows[i].style.display = checked ? 'table-row' : 'none';
    }
}

function show_all_options() {
    var checkbox = document.getElementById('show-all-options-checkbox');
    var checked = checkbox.checked;
    var rows = document.getElementsByClassName('options-standard-row');

    for (var row of rows) {
        if (checked) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    }
}


// =========================
// custom rows and buttons
// =========================

function renderCustomRowButtonTable() {
    const buttonTable = document.getElementById('button-table');
    const customBody = buttonTable.querySelector('#custom-button-section');
    customBody.innerHTML = '';
    customRowButtons = [];

    customRows.forEach((row, idx) => {
        let tr = document.createElement('tr');
        let leftTd = document.createElement('td');
        let rightTd = document.createElement('td');
        let editButton, confirmButton;

        let removeButton = document.createElement('button');
        removeButton.className = 'button button-custom-row button-remove';
        removeButton.textContent = '✖';

        if (editingIndex === idx) {
            confirmButton = document.createElement('button');
            confirmButton.className = 'button button-custom-row button-confirm';
            confirmButton.textContent = '✔';
            confirmButton.disabled = false;
            leftTd.appendChild(confirmButton);

            removeButton.disabled = false;
            removeButton.style.background = '';
            rightTd.appendChild(removeButton);
        } else {
            editButton = document.createElement('button');
            editButton.className = 'button button-custom-row button-edit';
            editButton.textContent = '✎';
            editButton.disabled = editingIndex !== null;
            editButton.style.background = editButton.disabled ? '#ccc' : '';
            leftTd.appendChild(editButton);

            removeButton.disabled = editingIndex !== null;
            removeButton.style.background = removeButton.disabled ? '#ccc' : '';
            rightTd.appendChild(removeButton);
        }
        tr.appendChild(leftTd);
        tr.appendChild(rightTd);
        customBody.appendChild(tr);
        customRowButtons[idx] = { confirmButton, editButton, removeButton };
    });
    updateButtonStates();
    attachCustomRowButtonListeners();
}

function renderCustomRows() {
    const customSection = document.getElementById('custom-row-section');
    customSection.innerHTML = '';

    //get current month display from dropdown or config
    let monthsDisplay = DEFAULT_MONTHS_DISPLAY;
    const monthsDropdown = document.getElementById('month-display-dropdown');
    if (monthsDropdown) {
        monthsDisplay = parseInt(monthsDropdown.value) || DEFAULT_MONTHS_DISPLAY;
    }

    //set number of value columns (exclude header column)
    let valueColumns = monthsDisplay - 1;

    customRows.forEach((row, idx) => {
        //if months display is greater than current months display, add zeros for new months, else trim excess months
        if (row.values.length < valueColumns) {
            row.values = row.values.concat(Array(valueColumns - row.values.length).fill(0));
        } else if (row.values.length > valueColumns) {
            row.values = row.values.slice(0, valueColumns);
        }

        let tr = document.createElement('tr');
        tr.dataset.index = idx;
        
        //if editingIndex matches current index, render as editable row, else render as static row
        if (editingIndex === idx) {
            //create row header cell with text input
            let headerTd = document.createElement('td');
            headerTd.innerHTML = `<input class="input-text" type="text" value="${row.header}" />`;
            tr.appendChild(headerTd);

            //create tax checkbox cell with tooltip
            let taxTd = document.createElement('td');
            taxTd.innerHTML = `
                <div style="display:inline-block; position:relative;">
                    <label style='margin-left:0.5rem;'>Tax:</label>
                    <input class="input-checkbox" type="checkbox" ${row.tax ? 'checked' : ''} style="margin-right:4px;" />
                    <span 
                        class="tax-tooltip-icon"
                        onmouseenter="showTooltip(event, 'Used to indicate if the row is used for tax purposes. If the row is an entitlement, it sets whether the row is taxable income or non-taxable income. If the row is a deduction, it sets whether or not the row is a tax to be added to total taxes.')"
                        onmouseleave="hideTooltip()"
                    >?</span>
                </div>
            `;
            tr.appendChild(taxTd);

            //loop through values (created based upon months display) and create num input cells
            for (let i = 0; i < row.values.length; i++) {
                let value = row.values[i];
                let sign = row.type === 'D' ? '-' : '';
                let valueAttr = value !== 0 && value !== "0" ? `value="${value}"` : '';
                let placeholderAttr = value === 0 || value === "0" ? 'placeholder="0"' : '';
                let valueTd = document.createElement('td');
                
                valueTd.innerHTML = `
                    <span>${sign}$&nbsp;&nbsp;</span>
                    <input type="text" class="input-num input-num-mid"
                        ${valueAttr}
                        ${placeholderAttr}
                        onkeypress="return /[0-9]/.test(event.key)"
                        maxlength="5"
                    />
                `;
                tr.appendChild(valueTd);
            }
        } 
        customSection.appendChild(tr);
    });
    renderCustomRowButtonTable();
}

function attachCustomRowButtonListeners() {
    customRowButtons.forEach((button, idx) => {
        if (button.confirmButton) {
            button.confirmButton.onclick = function() {
                // Select the correct row by data-index in the custom-row-section
                const customSection = document.getElementById('custom-row-section');
                const tr = customSection.querySelector(`tr[data-index="${editingIndex}"]`);
                // Get header input
                const headerInput = tr.querySelector('input.input-text');
                // Get tax checkbox
                const taxCheckbox = tr.querySelector('input[type="checkbox"]');
                // Get value inputs
                const valueInputs = tr.querySelectorAll('input.input-num');
                customRows[editingIndex].header = headerInput ? headerInput.value.trim() : '';
                customRows[editingIndex].tax = taxCheckbox ? taxCheckbox.checked : false;
                let values = [];
                valueInputs.forEach(inp => {
                    let val = inp.value.replace(/[^\d.-]/g, '');
                    val = val ? parseFloat(val) : 0;
                    values.push(val);
                });
                customRows[editingIndex].values = values;
                editingIndex = null;
                updatePaydf();
            };
        }

        if (button.editButton) {
            button.editButton.onclick = function() {
                if (editingIndex !== null) return;
                editingIndex = idx;
                renderCustomRows();
                updateButtonStates();
            };
        }

        if (button.removeButton) {
            button.removeButton.onclick = function() {
                customRows.splice(idx, 1);
                editingIndex = null;
                updatePaydf();
            };
        }
    });
}


// =========================
// update buttons
// =========================

function updateButtonStates() {
    const disable = editingIndex !== null;
    document.getElementById('add-entitlement-button').disabled = disable;
    document.getElementById('add-deduction-button').disabled = disable;
    document.getElementById('update-les-button').disabled = disable;
    document.getElementById('export-button').disabled = disable;
    document.getElementById('add-entitlement-button').style.background = disable ? '#ccc' : '';
    document.getElementById('add-deduction-button').style.background = disable ? '#ccc' : '';
    document.getElementById('update-les-button').style.background = disable ? '#ccc' : '';
    document.getElementById('export-button').style.background = disable ? '#ccc' : '';
}


// =========================
// export paydf
// =========================

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


// =========================
// tooltip functionality
// =========================

function showTooltip(evt, text) {
    const tooltip = document.getElementById('tooltip');
    tooltip.innerText = text;
    tooltip.style.left = (evt.pageX + 10) + 'px';
    tooltip.style.top = (evt.pageY + 10) + 'px';
    tooltip.style.display = 'block';
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    tooltip.style.display = 'none';
}



// =========================
// delegate event listeners
// =========================

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-button')) {
        const modalId = e.target.getAttribute('data-modal');
        if (modalId) {
            const modalCheckbox = document.getElementById(modalId);
            if (modalCheckbox) {
                modalCheckbox.checked = true;
            }
        }
    }

    if (e.target && e.target.id === 'update-les-button') {
        e.preventDefault();
        updatePaydf();
    }

    if (e.target.id === 'add-entitlement-button') {
        if (editingIndex !== null) return;

        if (customRows.length >= MAX_CUSTOM_ROWS) {
            alert('You can only add up to ' + MAX_CUSTOM_ROWS + ' custom rows.');
            return;
        }

        const paydfTable = document.getElementById('paydf-table');
        const headerRow = paydfTable.querySelector('tr');
        numMonths = headerRow.children.length - 2;
        const values = Array(numMonths).fill(0);
        editingIndex = customRows.length;
        customRows.push({ header: '', type: 'E', tax: false, values });
        renderCustomRows();
        updateButtonStates();
    }

    if (e.target.id === 'add-deduction-button') {
        if (editingIndex !== null) return;

        if (customRows.length >= MAX_CUSTOM_ROWS) {
            alert('You can only add up to ' + MAX_CUSTOM_ROWS + ' custom rows.');
            return;
        }

        const paydfTable = document.getElementById('paydf-table');
        const headerRow = paydfTable.querySelector('tr');
        numMonths = headerRow.children.length - 2;
        const values = Array(numMonths).fill(0);
        editingIndex = customRows.length;
        customRows.push({ header: '', type: 'D', tax: false, values });
        renderCustomRows();
        updateButtonStates();
    }

    if (e.target && e.target.id === 'export-button') {
        e.preventDefault();
        exportPaydf();
    }
});

document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'month-display-dropdown') {
        e.preventDefault();
        updatePaydf();
    }

    if (e.target && e.target.id === 'highlight-changes-checkbox') {
        highlight_changes();
    }

    if (e.target && e.target.id === 'show-all-variables-checkbox') {
        show_all_variables();
    }

    if (e.target && e.target.id === 'show-all-options-checkbox') {
        show_all_options();
    }
});

document.addEventListener('mousemove', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }
});

document.addEventListener('mouseleave', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        hideTooltip();
    }
}, true);
