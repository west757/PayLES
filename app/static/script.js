const DEFAULT_MONTHS_DISPLAY = 4;
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
    // Add customRows as JSON
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
        // After backend update, reset editingIndex and re-enable buttons
        editingIndex = null;
        updateButtonStates();
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
let customRows = []; // Array of custom row objects
let editingIndex = null; // Index of the row being edited, or null if none


function renderCustomRows() {
    const customSection = document.getElementById('custom-row-section');
    customSection.innerHTML = '';
    customRows.forEach((row, idx) => {
        let tr = document.createElement('tr');
        tr.className = 'pos-table custom-row';
        tr.dataset.index = idx;
        if (editingIndex === idx) {
            // Editable row: show inputs, confirm/remove buttons
            tr.innerHTML = `
                <td><input type="text" value="${row.header}" /></td>
                <td><input type="checkbox" ${row.tax ? 'checked' : ''} /></td>
                ${row.values.slice(1).map(v => `<td><input type="text" value="${v}" /></td>`).join('')}
                <td>
                    <button class="custom-row-confirm">✔</button>
                    <button class="custom-row-remove">✖</button>
                </td>
            `;
        } else {
            // Static row: show values, edit/remove buttons
            tr.innerHTML = `
                <td>${row.header}</td>
                <td>${row.tax ? 'Taxable' : 'Non-Taxable'}</td>
                ${row.values.slice(1).map(v => `<td>${row.type === 'D' ? '-' : ''}$${v}</td>`).join('')}
                <td>
                    <button class="custom-row-edit">✎</button>
                    <button class="custom-row-remove">✖</button>
                </td>
            `;
        }
        customSection.appendChild(tr);
    });
}


function updateButtonStates() {
    const disable = editingIndex !== null;
    document.getElementById('add-row-entitlement').disabled = disable;
    document.getElementById('add-row-deduction').disabled = disable;
    document.getElementById('update-les-button').disabled = disable;
    document.getElementById('export-button').disabled = disable;
    // Optionally gray out buttons visually
    // Disable all edit/remove except for the editing row
    document.querySelectorAll('.custom-row-edit, .custom-row-remove').forEach((btn, idx) => {
        btn.disabled = disable && editingIndex !== idx;
        btn.style.background = btn.disabled ? '#ccc' : '';
    });
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


    // Add Entitlement
    if (e.target.id === 'add-row-entitlement') {
        if (editingIndex !== null) return;
        editingIndex = customRows.length;
        customRows.push({ header: '', type: 'E', tax: false, values: [0,0,0,0] });
        renderCustomRows();
        updateButtonStates();
    }

    // Add Deduction
    if (e.target.id === 'add-row-deduction') {
        if (editingIndex !== null) return;
        editingIndex = customRows.length;
        customRows.push({ header: '', type: 'D', tax: false, values: [0,0,0,0] });
        renderCustomRows();
        updateButtonStates();
    }

    // Confirm Custom Row
    if (e.target.classList.contains('custom-row-confirm')) {
        // Gather input values and update customRows[editingIndex]
        // ... (input parsing logic here)
        editingIndex = null;
        updatePaydf();
    }

    // Remove Custom Row
    if (e.target.classList.contains('custom-row-remove')) {
        const idx = editingIndex !== null ? editingIndex : parseInt(e.target.closest('tr').dataset.index);
        customRows.splice(idx, 1);
        editingIndex = null;
        updatePaydf();
    }

    // Edit Custom Row
    if (e.target.classList.contains('custom-row-edit')) {
        const idx = parseInt(e.target.closest('tr').dataset.index);
        if (editingIndex !== null) return;
        editingIndex = idx;
        renderCustomRows();
        updateButtonStates();
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
