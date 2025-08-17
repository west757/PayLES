//constants and global variables
let editingIndex = null;
let customRows = [];
let customRowButtons = [];

function initConfigVars() {
    const configDiv = document.getElementById('config-data');
    if (configDiv) {
        window.RESERVED_HEADERS = JSON.parse(configDiv.dataset.reservedHeaders);
        window.DEFAULT_MONTHS_DISPLAY = parseInt(configDiv.dataset.defaultMonthsDisplay);
        window.MAX_CUSTOM_ROWS = parseInt(configDiv.dataset.maxCustomRows);
    }
}


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
        show_tsp_options();
        updateButtonStates();
        renderCustomRowButtonTable();
        updateMonthDropdowns();
        stripeTable('paydf-table');
    });
}


function updateMonthDropdowns() {
    const colHeaders = JSON.parse(document.getElementById('button-paydf-tables').dataset.colHeaders);
    // remove the first two column headers (row header and first month)
    const monthOptions = colHeaders.slice(2);

    document.querySelectorAll('select.month-dropdown').forEach(function(select) {
        const currentValue = select.value;
        select.innerHTML = '';
        monthOptions.forEach(function(month) {
            var option = document.createElement('option');
            option.value = month;
            option.textContent = month;
            if (month === currentValue) {
                option.selected = true;
            }
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

    let monthsDisplay = window.DEFAULT_MONTHS_DISPLAY;
    const monthsDropdown = document.getElementById('months-display-dropdown');
    if (monthsDropdown) {
        monthsDisplay = parseInt(monthsDropdown.value) || window.DEFAULT_MONTHS_DISPLAY;
    }
    let valueColumns = monthsDisplay - 1;

    customRows.forEach((row, idx) => {
        if (row.values.length < valueColumns) {
            row.values = row.values.concat(Array(valueColumns - row.values.length).fill(0));
        } else if (row.values.length > valueColumns) {
            row.values = row.values.slice(0, valueColumns);
        }

        let tr = document.createElement('tr');
        tr.dataset.index = idx;

        if (editingIndex === idx) {
            // Editable row
            let headerTd = document.createElement('td');
            headerTd.innerHTML = `<input class="input-text" type="text" value="${row.header}" required maxlength="18"/>`;
            tr.appendChild(headerTd);

            let taxTd = document.createElement('td');
            taxTd.innerHTML = `
                <div style="display:inline-block; position:relative;">
                    <label style='margin-left:0.5rem;'>Tax:</label>
                    <input class="input-checkbox" type="checkbox" ${row.tax ? 'checked' : ''} style="margin-right:4px;" />
                    <span 
                        class="tax-tooltip-icon"
                        onmouseenter="showTooltip(event, 'Used to indicate if the row is used for tax purposes. If an entitlement, sets whether the row is taxable income or non-taxable income. If a deduction, sets the row as a tax to be added to total taxes.')"
                        onmouseleave="hideTooltip()"
                    >?</span>
                </div>
            `;
            tr.appendChild(taxTd);

            for (let i = 0; i < row.values.length; i++) {
                let value = row.values[i];
                let sign = row.sign === -1 ? '-' : '';
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
        } else {
            // Static row
            let headerTd = document.createElement('td');
            headerTd.textContent = row.header;
            tr.appendChild(headerTd);

            let taxTd = document.createElement('td');
            taxTd.textContent = row.tax ? "Taxed" : "Non-Taxed";
            tr.appendChild(taxTd);

            for (let i = 0; i < row.values.length; i++) {
                let value = row.values[i];
                let sign = row.sign === -1 ? '-' : '';
                let valueTd = document.createElement('td');
                valueTd.textContent = `${sign}$${value}`;
                tr.appendChild(valueTd);
            }
        }
        customSection.appendChild(tr);
    });
    renderCustomRowButtonTable();
}


function attachCustomRowButtonListeners() {
    customRowButtons.forEach(function(button, idx) {
        if (button.confirmButton) {
            button.confirmButton.onclick = function() {
                // Select the correct row by data-index in the custom-row-section
                const customSection = document.getElementById('custom-row-section');
                const tr = customSection.querySelector('tr[data-index="' + editingIndex + '"]');
                // Get header input
                const headerInput = tr.querySelector('input.input-text');

                // Check if header is blank
                if (!headerInput.value.trim()) {
                    alert('Header text cannot be blank.');
                    headerInput.focus();
                    return;
                }

                // Gather all headers from PAYDF_TEMPLATE and other custom rows (except the one being edited)
                let allHeaders = [
                    ...window.RESERVED_HEADERS.map(h => h.trim()),
                    ...customRows.filter((row, idx) => idx !== editingIndex && row.header).map(row => row.header.trim())
                ];

                // Check for duplicate header
                const newHeader = headerInput.value.trim();
                if (allHeaders.includes(newHeader)) {
                    alert('Header name "' + headerInput.value.trim() + '" is currently in use or reserved. Please use another name.');
                    headerInput.focus();
                    return;
                }


                // Get tax checkbox
                const taxCheckbox = tr.querySelector('input[type="checkbox"]');
                // Get value inputs
                const valueInputs = tr.querySelectorAll('input.input-num');
                if (headerInput) {
                    customRows[editingIndex].header = headerInput.value.trim();
                } else {
                    customRows[editingIndex].header = '';
                }
                if (taxCheckbox) {
                    customRows[editingIndex].tax = taxCheckbox.checked;
                } else {
                    customRows[editingIndex].tax = false;
                }
                let values = [];
                valueInputs.forEach(function(inp) {
                    let val = inp.value.replace(/[^\d.-]/g, '');
                    if (val) {
                        val = parseFloat(val);
                    } else {
                        val = 0;
                    }
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
        if (customRows.length >= window.MAX_CUSTOM_ROWS) {
            alert('You can only add up to ' + window.MAX_CUSTOM_ROWS + ' custom rows.');
            return;
        }
        const paydfTable = document.getElementById('paydf-table');
        const headerRow = paydfTable.querySelector('tr');
        numMonths = headerRow.children.length - 2;
        const values = Array(numMonths).fill(0);
        editingIndex = customRows.length;
        customRows.push({ header: '', sign: 1, tax: false, values });
        renderCustomRows();
        updateButtonStates();
    }
    if (e.target.id === 'add-deduction-button') {
        if (editingIndex !== null) return;
        if (customRows.length >= window.MAX_CUSTOM_ROWS) {
            alert('You can only add up to ' + window.MAX_CUSTOM_ROWS + ' custom rows.');
            return;
        }
        const paydfTable = document.getElementById('paydf-table');
        const headerRow = paydfTable.querySelector('tr');
        numMonths = headerRow.children.length - 2;
        const values = Array(numMonths).fill(0);
        editingIndex = customRows.length;
        customRows.push({ header: '', sign: -1, tax: false, values });
        renderCustomRows();
        updateButtonStates();
    }

    if (e.target && e.target.id === 'export-button') {
        e.preventDefault();
        exportPaydf();
    }
});


document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'months-display-dropdown') {
        e.preventDefault();
        updatePaydf();
    }

    if (e.target && e.target.id === 'highlight-changes-checkbox') {
        highlight_changes();
    }

    if (e.target && e.target.id === 'show-all-variables-checkbox') {
        show_all_variables();
    }

    if (e.target && e.target.id === 'show-tsp-options-checkbox') {
        show_tsp_options();
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


document.body.addEventListener('htmx:afterSwap', function(evt) {
    initConfigVars();
    stripeTable('paydf-table');
    stripeTable('options-table');
    stripeTable('settings-table');
    attachTspBaseListeners();
    updateTspInputs();
});


// close modals on Escape key press
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' || e.key === 'Esc') {
        document.querySelectorAll('.modal-state:checked').forEach(function(input) {
            input.checked = false;
        });
    }
});


// disable buttons on form submission to prevent multiple submissions
document.addEventListener('DOMContentLoaded', function() {
    initConfigVars();
    attachTspBaseListeners();

    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function() {
            form.querySelectorAll('button, input[type="submit"]').forEach(function(btn) {
                btn.disabled = true;
            });
        });
    });
});


document.body.addEventListener('htmx:beforeRequest', function(evt) {
    if (evt.target && evt.target.id === 'home-form') {
        evt.target.querySelectorAll('button, input[type="submit"]').forEach(function(btn) {
            btn.disabled = true;
        });
    }
});





function attachTspBaseListeners() {
    document.querySelectorAll('input[data-header="Trad TSP Base Rate"], input[data-header="Roth TSP Base Rate"]').forEach(function(input) {
        input.removeEventListener('input', updateTspInputs); // Prevent duplicate listeners
        input.removeEventListener('change', updateTspInputs);
        input.addEventListener('input', updateTspInputs);
        input.addEventListener('change', updateTspInputs);
    });
}





// =========================
// TSP dynamic enable/disable
// =========================
function showTspNotification(message) {
    let notif = document.getElementById('tsp-notification');
    if (!notif) {
        notif = document.createElement('div');
        notif.id = 'tsp-notification';
        notif.style.position = 'fixed';
        notif.style.top = '20px';
        notif.style.left = '50%';
        notif.style.transform = 'translateX(-50%)';
        notif.style.background = '#ffcccc';
        notif.style.color = '#900';
        notif.style.padding = '10px 20px';
        notif.style.borderRadius = '5px';
        notif.style.zIndex = '1000';
        notif.style.fontWeight = 'bold';
        document.body.appendChild(notif);
    }
    notif.textContent = message;
    notif.style.display = 'block';
    setTimeout(() => { notif.style.display = 'none'; }, 4000);
}

function updateTspInputs() {
    const tradBaseInput = document.querySelector('input[data-header="Trad TSP Base Rate"]');
    const rothBaseInput = document.querySelector('input[data-header="Roth TSP Base Rate"]');
    const tradBaseValue = tradBaseInput ? parseInt(tradBaseInput.value || tradBaseInput.placeholder || "0", 10) : 0;
    const rothBaseValue = rothBaseInput ? parseInt(rothBaseInput.value || rothBaseInput.placeholder || "0", 10) : 0;

    let invalidSpecialty = false;

    document.querySelectorAll('.tsp-rate-input').forEach(function(input) {
        const header = input.getAttribute('data-header');
        const type = input.getAttribute('data-tsp-type');
        if (header === "Trad TSP Base Rate" || header === "Roth TSP Base Rate") {
            input.disabled = false;
            return;
        }
        if (type === "trad" && tradBaseValue < 1) {
            input.disabled = true;
            if (parseInt(input.value || "0", 10) > 0) invalidSpecialty = true;
            input.value = "";
        } else if (type === "roth" && rothBaseValue < 1) {
            input.disabled = true;
            if (parseInt(input.value || "0", 10) > 0) invalidSpecialty = true;
            input.value = "";
        } else {
            input.disabled = false;
        }
    });

    // Gray out update buttons if invalid
    const buttonIds = [
        'update-les-button',
        'add-entitlement-button',
        'add-deduction-button',
        'export-button'
    ];
    buttonIds.forEach(function(id) {
        const btn = document.getElementById(id);
        if (btn) {
            btn.disabled = invalidSpecialty || editingIndex !== null;
        }
    });

    // Show notification if invalid
    if (invalidSpecialty) {
        showTspNotification("TSP Specialty/Incentive/Bonus Rates cannot be used unless Base Rate is greater than 0.");
    }
}



document.addEventListener('input', function(e) {
    if (e.target.classList.contains('tsp-rate-input')) {
        // Remove non-digit characters and limit to 2 digits
        let val = e.target.value.replace(/\D/g, '');
        if (val.length > 2) val = val.slice(0, 2);
        e.target.value = val;
    }

    if (e.target.classList.contains('input-num')) {
        // Allow only digits and one decimal point
        let val = e.target.value;
        // Remove invalid characters
        val = val.replace(/[^0-9.]/g, '');
        // Only one decimal point allowed
        let parts = val.split('.');
        if (parts.length > 2) {
            val = parts[0] + '.' + parts.slice(1).join('');
        }
        e.target.value = val;
    }
});