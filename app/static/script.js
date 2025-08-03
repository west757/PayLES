const DEFAULT_MONTHS_DISPLAY = 6;
const MONTHS_SHORT = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];

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



function updatePaydf() {
    const optionsForm = document.getElementById('options-form');
    const settingsForm = document.getElementById('settings-form');
    const formData = new FormData(optionsForm);
    const monthsDropdown = settingsForm.querySelector('[name="months_display"]');
    formData.append('months_display', monthsDropdown.value);

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
        renderCustomRows();
    });
}


function highlight_changes() {
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
                cell.style.backgroundColor = '#b9f755';
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



const MAX_CUSTOM_ROWS = 9;
let customRows = [];
let editingIndex = null;


function renderCustomRowButtonTable() {
    const btnTable = document.getElementById('custom-row-button-table');
    const paydfTable = document.getElementById('paydf-table');
    if (!btnTable || !paydfTable) return;

    // Get all button table bodies
    const variableBody = btnTable.querySelector('#variable-reference-body');
    const edaBody = btnTable.querySelector('#eda-reference-body');
    const customBody = btnTable.querySelector('#custom-reference-body');
    const calcBody = btnTable.querySelector('#calculation-reference-body');
    if (!variableBody || !edaBody || !customBody || !calcBody) return;

    // Clear all bodies
    variableBody.innerHTML = '';
    edaBody.innerHTML = '';
    customBody.innerHTML = '';
    calcBody.innerHTML = '';

    // Helper to add blank row
    function addBlankBtnRow(className) {
        const tr = document.createElement('tr');
        tr.className = className;
        const leftTd = document.createElement('td');
        leftTd.className = 'custom-row-btn-td';
        const rightTd = document.createElement('td');
        rightTd.className = 'custom-row-btn-td';
        tr.appendChild(leftTd);
        tr.appendChild(rightTd);
        return tr;
    }

    // 1. Variable rows
    const variableRows = paydfTable.querySelectorAll('tbody.pos-table-section .variable-row');
    variableRows.forEach(row => {
        variableBody.appendChild(addBlankBtnRow(row.className));
    });

    // 2. EDA rows (Entitlement/Deduction/Allowance)
    const edaRows = paydfTable.querySelectorAll('tbody.pos-table-section tr:not(.variable-row)');
    edaRows.forEach(row => {
        edaBody.appendChild(addBlankBtnRow(row.className));
    });

    // 3. Custom rows
    const customRowsSection = document.getElementById('custom-row-section');
    if (customRowsSection) {
        const customRowsTrs = customRowsSection.querySelectorAll('tr');
        customRowsTrs.forEach((row, idx) => {
            const tr = addBlankBtnRow(row.className);
            // Only add buttons for custom rows
            if (customRows[idx]) {
                const leftTd = tr.children[0];
                const rightTd = tr.children[1];
                if (editingIndex === idx) {
                    const confirmBtn = document.createElement('button');
                    confirmBtn.className = 'custom-row-btn confirm custom-row-confirm';
                    confirmBtn.innerHTML = '&#10003;';
                    leftTd.appendChild(confirmBtn);
                } else {
                    const editBtn = document.createElement('button');
                    editBtn.className = 'custom-row-btn edit custom-row-edit';
                    editBtn.innerHTML = '&#9998;';
                    if (editingIndex !== null) editBtn.disabled = true;
                    leftTd.appendChild(editBtn);
                }
                const removeBtn = document.createElement('button');
                removeBtn.className = 'custom-row-btn remove custom-row-remove';
                removeBtn.innerHTML = '&#10005;';
                if (editingIndex !== null && editingIndex !== idx) removeBtn.disabled = true;
                rightTd.appendChild(removeBtn);
                tr.dataset.index = idx;
            }
            customBody.appendChild(tr);
        });
    }

    // 4. Calculation rows
    const calcRows = paydfTable.querySelectorAll('tbody:not(.pos-table-section):not(#custom-row-section) tr');
    calcRows.forEach(row => {
        calcBody.appendChild(addBlankBtnRow(row.className));
    });
}

function renderCustomRows() {
    const customSection = document.getElementById('custom-row-section');
    if (!customSection) return;
    customSection.innerHTML = '';
    customRows.forEach((row, idx) => {
        let tr = document.createElement('tr');
        tr.className = 'pos-table';
        tr.dataset.index = idx;
        // Only render custom row data, no button logic or inline styles
        if (editingIndex === idx) {
            let headerTd = document.createElement('td');
            let inputDiv = document.createElement('div');
            inputDiv.style.flex = '1';
            inputDiv.style.paddingLeft = '4px';
            inputDiv.innerHTML = `<input type="text" id="custom-row-header" value="${row.header}" maxlength="32" style="width:120px;">`;
            headerTd.appendChild(inputDiv);
            tr.appendChild(headerTd);
            // Tax cell
            let taxTd = document.createElement('td');
            taxTd.innerHTML = `Tax: <input type="checkbox" id="custom-row-tax" ${row.tax ? 'checked' : ''}>`;
            tr.appendChild(taxTd);
            for (let i = 1; i < row.values.length; i++) {
                let valueTd = document.createElement('td');
                valueTd.innerHTML = `
                    ${row.type === 'D' ? '-' : ''}$<input type="text" class="custom-row-value" value="${row.values[i]}" maxlength="5" style="width:60px;" pattern="\\d{1,5}" title="Enter up to 5 digits">`;
                tr.appendChild(valueTd);
            }
        } else {
            let headerTd = document.createElement('td');
            let textDiv = document.createElement('div');
            textDiv.style.flex = '1';
            textDiv.style.paddingLeft = '4px';
            textDiv.textContent = row.header;
            headerTd.appendChild(textDiv);
            tr.appendChild(headerTd);
            // Tax cell
            let taxTd = document.createElement('td');
            taxTd.textContent = row.tax ? 'Taxable' : 'Non-Taxable';
            tr.appendChild(taxTd);
            for (let i = 1; i < row.values.length; i++) {
                let valueTd = document.createElement('td');
                valueTd.textContent = `${row.type === 'D' ? '-' : ''}$${row.values[i]}`;
                tr.appendChild(valueTd);
            }
        }
        customSection.appendChild(tr);
    });
    document.getElementById('add-row-entitlement').disabled = editingIndex !== null || customRows.length >= MAX_CUSTOM_ROWS;
    document.getElementById('add-row-deduction').disabled = editingIndex !== null || customRows.length >= MAX_CUSTOM_ROWS;
    let maxInfo = document.getElementById('custom-row-max-info');
    if (!maxInfo) {
        maxInfo = document.createElement('div');
        maxInfo.id = 'custom-row-max-info';
        maxInfo.style.marginBottom = '8px';
        document.getElementById('settings-form').prepend(maxInfo);
    }
    maxInfo.textContent = `Custom rows allowed: ${MAX_CUSTOM_ROWS - customRows.length}`;
    renderCustomRowButtonTable();
}

function insertCustomRow(type) {
    if (editingIndex !== null || customRows.length >= MAX_CUSTOM_ROWS) return;
    const table = document.getElementById('paydf-table');
    const headerRow = table.querySelector('.pos-table-header');
    const months = Array.from(headerRow.querySelectorAll('td')).slice(1).map(td => td.textContent.trim());
    let values = Array(months.length).fill(0);
    customRows.push({ header: '', type, tax: false, values });
    editingIndex = customRows.length - 1;
    renderCustomRows();
    // No need to call renderCustomRowButtonTable here, renderCustomRows will do it
}


// Confirm custom row (make static, send to backend)
function confirmCustomRow() {
    // Gather values
    const type = document.getElementById('add-row-entitlement').disabled ? 'E' : 'D';
    const header = document.getElementById('custom-row-header').value.trim();
    const tax = document.getElementById('custom-row-tax').checked;
    const valueInputs = document.querySelectorAll('.custom-row-value');
    let values = [];
    for (let inp of valueInputs) {
        let val = inp.value.replace(/\D/g, '');
        val = val ? Math.min(parseInt(val), 99999) : 0;
        values.push(val);
    }

    // Store in hidden input for backend
    let customRowData = {
        header: header,
        type: type,
        tax: tax,
        values: values
    };
    let hidden = document.getElementById('custom-row-hidden');
    if (!hidden) {
        hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.id = 'custom-row-hidden';
        hidden.name = 'custom_row';
        document.getElementById('options-form').appendChild(hidden);
    }
    hidden.value = JSON.stringify(customRowData);

    // Re-enable add buttons
    document.getElementById('add-row-entitlement').disabled = false;
    document.getElementById('add-row-deduction').disabled = false;

    // Remove editable row, insert static row
    let customSection = document.getElementById('custom-row-section');
    customSection.innerHTML = '';
    let row = document.createElement('tr');
    row.className = 'pos-table';
    row.innerHTML = `
        <td>
            <button class="custom-row-edit" style="background:#4CAF50;color:white;border:none;padding:4px 8px;margin-right:4px;">&#9998;</button>
            <button class="custom-row-remove" style="background:#f44336;color:white;border:none;padding:4px 8px;">&#10005;</button>
        </td>
        <td>${header}</td>
        <td>${tax ? 'Taxable' : 'Non-Taxable'}</td>
        ${values.map(v => `<td>${type === 'D' ? '-' : ''}$${v}</td>`).join('')}
    `;
    customSection.appendChild(row);

    // Trigger updatePaydf to send to backend
    updatePaydf();
}


function removeCustomRow() {
    let idx = editingIndex;
    if (idx === null) {
        // Find index from clicked button
        const btn = event.target;
        const tr = btn.closest('tr');
        idx = parseInt(tr.dataset.index);
    }
    customRows.splice(idx, 1);
    editingIndex = null;
    renderCustomRows();
    renderCustomRowButtonTable(); // Ensure button table is updated after removing row
    let hidden = document.getElementById('custom-row-hidden');
    if (customRows.length === 0 && hidden) hidden.remove();
    else if (hidden) hidden.value = JSON.stringify(customRows);
    document.getElementById('add-row-entitlement').disabled = false;
    document.getElementById('add-row-deduction').disabled = false;
    updatePaydf();
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
    //update les button
    if (e.target && e.target.id === 'update-les-button') {
        e.preventDefault();
        updatePaydf();
    }

    //export button
    if (e.target && e.target.id === 'export-button') {
        e.preventDefault();
        exportPaydf();
    }


     // Add Entitlement Row
    if (e.target && e.target.id === 'add-row-entitlement') {
        e.target.disabled = true;
        document.getElementById('add-row-deduction').disabled = true;
        insertCustomRow('E');
    }

    // Add Deduction Row
    if (e.target && e.target.id === 'add-row-deduction') {
        e.target.disabled = true;
        document.getElementById('add-row-entitlement').disabled = true;
        insertCustomRow('D');
    }

    // Confirm Custom Row
    if (e.target && e.target.classList.contains('custom-row-confirm')) {
        confirmCustomRow();
    }

    // Remove Custom Row
    if (e.target && e.target.classList.contains('custom-row-remove')) {
        removeCustomRow();
    }

    if (e.target && e.target.classList.contains('custom-row-edit')) {
        const tr = e.target.closest('tr');
        const idx = parseInt(tr.dataset.index);
        if (editingIndex !== null) return;
        editingIndex = idx;
        renderCustomRows();
    }
});

document.addEventListener('change', function(e) {
    //months dropdown
    if (e.target && e.target.id === 'months-dropdown') {
        e.preventDefault();
        updatePaydf();
        updateMonthDropdowns(parseInt(e.target.value));
    }

    //highlight changes checkbox
    if (e.target && e.target.id === 'highlight-changes-checkbox') {
        highlight_changes();
    }

    //show all variables checkbox
    if (e.target && e.target.id === 'show-all-variables-checkbox') {
        show_all_variables();
    }

    //show all options checkbox
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

// Auto-confirm edit mode row on update triggers
function autoConfirmEditRow() {
    if (editingIndex !== null) {
        confirmCustomRow();
    }
}

document.getElementById('update-les-button')?.addEventListener('click', autoConfirmEditRow);
document.getElementById('months-dropdown')?.addEventListener('change', autoConfirmEditRow);

// Initial render
window.addEventListener('DOMContentLoaded', function() {
    renderCustomRows();
    renderCustomRowButtonTable();
});

// Update button table on window resize
window.addEventListener('resize', renderCustomRowButtonTable);
