const MONTHS_SHORT = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
const DEFAULT_MONTHS_DISPLAY = 6;
const MAX_CUSTOM_ROWS = 9;


// Drag and drop functionality for file input
(function() {
    var dropContainer = document.getElementById("home-drop");
    var fileInput = document.getElementById("home-input");
    var form = dropContainer.closest("form");

    if (!dropContainer || !fileInput || !form) return;

    // Prevent default drag behaviors
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
        // Only remove if leaving the drop area
        if (e.target === dropContainer) {
            dropContainer.classList.remove("drag-active");
        }
    });

    dropContainer.addEventListener("drop", function(e) {
        dropContainer.classList.remove("drag-active");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            // Optionally auto-submit the form after drop
            if (form) {
                form.dispatchEvent(new Event('submit', {cancelable: true, bubbles: true}));
            }
        }
    });
})();



function getInitialMonth() {
    const el = document.getElementById('initial-month');
    return el ? el.value : MONTHS_SHORT[0];
}

function getMonthOptions(initialMonth, monthsDisplay) {
    let idx = MONTHS_SHORT.indexOf(initialMonth);
    let options = [];
    for (let i = 1; i < monthsDisplay; i++) {
        idx = (idx + 1) % MONTHS_SHORT.length;
        options.push(MONTHS_SHORT[idx]);
    }
    return options;
}

function updateMonthDropdowns(monthsDisplayOverride) {
    let displayCount = monthsDisplayOverride || DEFAULT_MONTHS_DISPLAY;
    const initialMonth = getInitialMonth();
    const monthOptions = getMonthOptions(initialMonth, displayCount);
    document.querySelectorAll('select.month-display-dropdown').forEach(function(select) {
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
        highlight_changes();
        show_all_variables();
        show_all_options();
        editingIndex = null;
        updateButtonStates();
        renderCustomRowButtonTable();
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






let customRows = []; // Array of custom row objects
let editingIndex = null; // Index of the row being edited, or null if none
let customRowButtons = [];

function renderCustomRows() {
    const customSection = document.getElementById('custom-row-section');
    customSection.innerHTML = '';

    // Get current month display from dropdown or config
    let monthsDisplay = DEFAULT_MONTHS_DISPLAY;
    const monthsDropdown = document.getElementById('month-display-dropdown');
    if (monthsDropdown) {
        monthsDisplay = parseInt(monthsDropdown.value) || DEFAULT_MONTHS_DISPLAY;
    }

    // Only value columns (exclude header column)
    let valueColumns = monthsDisplay - 1;

    customRows.forEach((row, idx) => {
        // Ensure values array matches valueColumns
        if (row.values.length < valueColumns) {
            // Add zeros for new months
            row.values = row.values.concat(Array(valueColumns - row.values.length).fill(0));
        } else if (row.values.length > valueColumns) {
            // Truncate values for fewer months
            row.values = row.values.slice(0, valueColumns);
        }

        let tr = document.createElement('tr');
        tr.className = 'pos-table custom-row';
        tr.dataset.index = idx;
        
        if (editingIndex === idx) {
            // Editable row: styled inputs, labels, $ and - signs
            let headerTd = document.createElement('td');
            headerTd.innerHTML = `<input type="text" class="text-input" value="${row.header}" />`;
            tr.appendChild(headerTd);

            // Tax cell with label
            let taxTd = document.createElement('td');
            taxTd.innerHTML = `
                <div style="display:inline-block; position:relative;">
                <label style='margin-left:8px;'>Tax:</label>
                    <input type="checkbox" ${row.tax ? 'checked' : ''} style="margin-right:4px;" />
                    <span 
                        class="tax-tooltip-icon" 
                        style="
                            font-size:13px; 
                            cursor:pointer; 
                            position:absolute; 
                            top:-8px; 
                            right:-10px; 
                            background:white;
                            border-radius:50%;
                            padding:0 2px;
                            line-height:1;
                        "
                        onmouseenter="showTooltip(event, 'Used to indicate if the row is used for tax purposes. If the row is an entitlement, it sets whether the row is taxable income or non-taxable income. If the row is a deduction, it sets whether or not the row is a tax to be added to total taxes.')"
                        onmouseleave="hideTooltip()"
                    >?</span>
                </div>
            `;
            tr.appendChild(taxTd);

            // Value inputs for each month column
            for (let i = 0; i < row.values.length; i++) {
                let value = row.values[i];
                let sign = row.type === 'D' ? '-' : '';
                let valueAttr = value !== 0 && value !== "0" ? `value="${value}"` : '';
                let placeholderAttr = value === 0 || value === "0" ? 'placeholder="0"' : '';
                let valueTd = document.createElement('td');
                valueTd.innerHTML = `
                    <span>${sign}$&nbsp;&nbsp;</span>
                    <input type="text" class="num-input num-input-mid"
                        ${valueAttr}
                        ${placeholderAttr}
                        onkeypress="return /[0-9]/.test(event.key)"
                        maxlength="5"
                    />
                `;
                tr.appendChild(valueTd);
            }
        } else {
            // Static row: show values only (no buttons)
            tr.innerHTML = `
                <td>${row.header}</td>
                <td>${row.tax ? 'Taxable' : 'Non-Taxable'}</td>
                ${row.values.map(v => `<td>${row.type === 'D' ? '-' : ''}$${v}</td>`).join('')}
            `;
        }
        customSection.appendChild(tr);
    });
    renderCustomRowButtonTable();
}


function renderCustomRowButtonTable() {
    const btnTable = document.getElementById('custom-row-button-table');
    const customBody = btnTable.querySelector('#custom-reference-body');
    customBody.innerHTML = '';
    customRowButtons = [];
    customRows.forEach((row, idx) => {
        let tr = document.createElement('tr');
        tr.className = 'custom-row-btn-tr';
        let leftTd = document.createElement('td');
        let rightTd = document.createElement('td');
        let editBtn, removeBtn, confirmBtn;

        if (editingIndex === idx) {
            confirmBtn = document.createElement('button');
            confirmBtn.className = 'custom-row-btn confirm custom-row-confirm';
            confirmBtn.textContent = '✔';
            confirmBtn.disabled = false;
            leftTd.appendChild(confirmBtn);

            removeBtn = document.createElement('button');
            removeBtn.className = 'custom-row-btn remove custom-row-remove';
            removeBtn.textContent = '✖';
            removeBtn.disabled = false;
            rightTd.appendChild(removeBtn);

        } else {
            editBtn = document.createElement('button');
            editBtn.className = 'custom-row-btn edit custom-row-edit';
            editBtn.textContent = '✎';
            editBtn.disabled = editingIndex !== null;
            editBtn.style.background = editBtn.disabled ? '#ccc' : '';
            leftTd.appendChild(editBtn);

            removeBtn = document.createElement('button');
            removeBtn.className = 'custom-row-btn remove custom-row-remove';
            removeBtn.textContent = '✖';
            removeBtn.disabled = editingIndex !== null;
            removeBtn.style.background = removeBtn.disabled ? '#ccc' : '';
            rightTd.appendChild(removeBtn);
        }
        tr.appendChild(leftTd);
        tr.appendChild(rightTd);
        customBody.appendChild(tr);
        customRowButtons[idx] = { editBtn, removeBtn, confirmBtn };
    });
    updateButtonStates();
    attachCustomRowButtonListeners();
}

// Attach event listeners after rendering
function attachCustomRowButtonListeners() {
    customRowButtons.forEach((btns, idx) => {
        if (btns.confirmBtn) {
            btns.confirmBtn.onclick = function() {
                const tr = document.querySelector(`#custom-row-section tr[data-index="${editingIndex}"]`);
                // Get header input
                const headerInput = tr.querySelector('input.text-input');
                // Get tax checkbox
                const taxCheckbox = tr.querySelector('input[type="checkbox"]');
                // Get value inputs
                const valueInputs = tr.querySelectorAll('input.num-input');
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

        if (btns.editBtn) {
            btns.editBtn.onclick = function() {
                if (editingIndex !== null) return;
                editingIndex = idx;
                renderCustomRows();
                updateButtonStates();
            };
        }

        if (btns.removeBtn) {
            btns.removeBtn.onclick = function() {
                customRows.splice(idx, 1);
                editingIndex = null;
                updatePaydf();
            };
        }
    });
}

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


//les image tooltip
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



//delegated event listeners for dynamic paydf controls
document.addEventListener('click', function(e) {
    if (e.target && e.target.id === 'update-les-button') {
        e.preventDefault();
        updatePaydf();
    }

    if (e.target && e.target.id === 'export-button') {
        e.preventDefault();
        exportPaydf();
    }

    if (e.target.id === 'add-entitlement-button') {
        if (editingIndex !== null) return;
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
        const paydfTable = document.getElementById('paydf-table');
        const headerRow = paydfTable.querySelector('tr');
        numMonths = headerRow.children.length - 2;
        const values = Array(numMonths).fill(0);
        editingIndex = customRows.length;
        customRows.push({ header: '', type: 'D', tax: false, values });
        renderCustomRows();
        updateButtonStates();
    }
});

document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'months-dropdown') {
        e.preventDefault();
        updatePaydf();
        updateMonthDropdowns(parseInt(e.target.value));
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
