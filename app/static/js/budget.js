// --- CONFIG EXAMPLES (replace with actual values or import from config) ---
const GRADES = ["E1", "E2", "E3", "E4", "E5"]; // Example
const TAX_FILING_TYPES_DEDUCTIONS = ["Single", "Married", "Head of Household"];
const COMBAT_ZONE_OPTIONS = ["Yes", "No"];

// --- STATE ---
let isEditing = false;
let currentEdit = null;

// --- UTILS ---
function showOverlay() {
    let overlay = document.createElement('div');
    overlay.id = 'edit-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = 0;
    overlay.style.left = 0;
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.background = 'rgba(220,220,220,0.5)';
    overlay.style.zIndex = 9998;
    overlay.style.pointerEvents = 'none';
    document.body.appendChild(overlay);
}
function hideOverlay() {
    let overlay = document.getElementById('edit-overlay');
    if (overlay) overlay.remove();
}
function disableInputsExcept(exceptions=[]) {
    document.querySelectorAll('input, button, select, textarea').forEach(el => {
        if (!exceptions.includes(el)) {
            el.disabled = true;
        }
    });
}
function enableAllInputs() {
    document.querySelectorAll('input, button, select, textarea').forEach(el => {
        el.disabled = false;
    });
}
function showToast(msg) {
    // Use your existing toast function
    if (window.showToast) window.showToast(msg);
    else alert(msg);
}

// --- MAIN EDIT HANDLER ---
function enterEditMode(cellBtn, rowHeader, colMonth, value, fieldType) {
    if (isEditing) return;
    isEditing = true;
    currentEdit = {cellBtn, rowHeader, colMonth, value, fieldType};

    showOverlay();
    disableInputsExcept([]);

    // Create input box
    let input;
    if (fieldType === 'select') {
        input = document.createElement('select');
        let options = [];
        if (rowHeader === 'grade') options = GRADES;
        else if (rowHeader === 'federal filing status') options = TAX_FILING_TYPES_DEDUCTIONS;
        else if (rowHeader === 'combat zone') options = COMBAT_ZONE_OPTIONS;
        options.forEach(opt => {
            let o = document.createElement('option');
            o.value = opt;
            o.textContent = opt;
            if (opt === value) o.selected = true;
            input.appendChild(o);
        });
    } else if (fieldType === 'int') {
        input = document.createElement('input');
        input.type = 'number';
        input.maxLength = 3;
        input.placeholder = value;
        input.classList.add('input-int');
        input.pattern = '\\d{1,3}';
    } else if (fieldType === 'string') {
        input = document.createElement('input');
        input.type = 'text';
        input.maxLength = 5;
        input.placeholder = value;
        input.classList.add('input-string');
    } else if (fieldType === 'decimal') {
        input = document.createElement('input');
        input.type = 'text';
        input.maxLength = 7;
        input.placeholder = value;
        input.classList.add('input-decimal');
    }

    // Insert input box into cell
    cellBtn.style.display = 'none';
    let cell = cellBtn.parentElement;
    cell.appendChild(input);

    // Create buttons
    let btnContainer = document.createElement('div');
    btnContainer.style.display = 'flex';
    btnContainer.style.justifyContent = 'center';
    btnContainer.style.gap = '8px';
    btnContainer.style.marginBottom = '4px';
    btnContainer.style.zIndex = 9999;

    // Onetime button
    let onetimeBtn = document.createElement('button');
    onetimeBtn.textContent = 'Onetime ▼';
    onetimeBtn.style.background = 'green';
    onetimeBtn.style.color = 'white';
    onetimeBtn.onclick = function() {
        handleEditSubmit(false);
    };

    // Repeat button
    let repeatBtn = document.createElement('button');
    repeatBtn.textContent = 'Repeat ▶';
    repeatBtn.style.background = 'green';
    repeatBtn.style.color = 'white';
    repeatBtn.onclick = function() {
        handleEditSubmit(true);
    };

    // Cancel button
    let cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel ✖';
    cancelBtn.style.background = 'red';
    cancelBtn.style.color = 'white';
    cancelBtn.onclick = function() {
        exitEditMode();
    };

    btnContainer.appendChild(onetimeBtn);
    btnContainer.appendChild(repeatBtn);
    btnContainer.appendChild(cancelBtn);

    cell.insertBefore(btnContainer, input);

    // Only enable the edit controls
    disableInputsExcept([input, onetimeBtn, repeatBtn, cancelBtn]);
}

// --- EXIT EDIT MODE ---
function exitEditMode() {
    if (!isEditing || !currentEdit) return;
    let {cellBtn} = currentEdit;
    let cell = cellBtn.parentElement;
    // Remove input and buttons
    cell.querySelectorAll('input, select, div').forEach(el => {
        if (el !== cellBtn) el.remove();
    });
    cellBtn.style.display = '';
    hideOverlay();
    enableAllInputs();
    isEditing = false;
    currentEdit = null;
}

// --- VALIDATION ---
function validateInput(fieldType, rowHeader, value) {
    if (value === '' || value === null || value === undefined) {
        showToast('A value must be entered.');
        return false;
    }
    if (fieldType === 'int') {
        let num = parseInt(value, 10);
        if (isNaN(num)) {
            showToast('Value must be a number.');
            return false;
        }
        if (rowHeader.toLowerCase().includes('tsp rate') && (num < 0 || num > 100)) {
            showToast('TSP rate must be between 0 and 100.');
            return false;
        }
        if (value.length > 3) {
            showToast('Value must be at most 3 digits.');
            return false;
        }
    }
    if (fieldType === 'string') {
        if (value.length > 5) {
            showToast('Value must be at most 5 characters.');
            return false;
        }
    }
    if (fieldType === 'decimal') {
        if (!/^\d{0,4}(\.\d{0,2})?$/.test(value)) {
            showToast('Value must be a decimal with up to 4 digits before and 2 after the decimal.');
            return false;
        }
        if (value.length > 7) {
            showToast('Value must be at most 7 characters.');
            return false;
        }
    }
    // Add more validation as needed
    return true;
}

// --- SUBMIT HANDLER ---
function handleEditSubmit(repeat) {
    let {rowHeader, colMonth, fieldType} = currentEdit;
    let input = document.querySelector('.input-int, .input-string, .input-decimal, select');
    let value = input.value;
    if (!validateInput(fieldType, rowHeader, value)) return;
    exitEditMode();
    update_budget_cell(rowHeader, colMonth, value, repeat);
}

// --- UPDATE CELL FUNCTION (stub) ---
function update_budget_cell(rowHeader, colMonth, value, repeat) {
    // Implement AJAX/htmx call to backend here
    // Example:
    // htmx.ajax('POST', '/update_cells', {row_header: rowHeader, col_month: colMonth, value, repeat});
    showToast(`Updated ${rowHeader} for ${colMonth} to ${value} (${repeat ? 'repeat' : 'onetime'})`);
}

// --- CELL BUTTON CLICK HANDLER ---
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('cell-button')) {
        // Get rowHeader, colMonth, value, fieldType from data attributes or DOM
        let rowHeader = e.target.getAttribute('data-row');
        let colMonth = e.target.getAttribute('data-col');
        let value = e.target.innerText;
        let fieldType = e.target.getAttribute('data-field'); // You need to set this attribute in your HTML
        enterEditMode(e.target, rowHeader, colMonth, value, fieldType);
    }
});
