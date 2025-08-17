//constants and global variables
let editingIndex = null;
let customRows = [];
let customRowButtons = [];



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

                console.log(window.RESERVED_HEADERS);
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
// delegate event listeners
// =========================

document.addEventListener('click', function(e) {
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
});