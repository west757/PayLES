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
// delegate event listeners
// =========================

document.addEventListener('click', function(e) {
    if (e.target && e.target.id === 'update-les-button') {
        e.preventDefault();
        disableAllInputs();
        updatePaydf();
    }
});


document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'months-display-dropdown') {
        e.preventDefault();
        disableAllInputs();
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