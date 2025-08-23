// --- Modal State ---
let selectedRowType = null; // 'e' or 'd'
let selectedMethod = null; // 'template' or 'custom'

// --- DOM Elements ---
const rowTypeEntitlement = document.getElementById('row-type-entitlement');
const rowTypeDeduction = document.getElementById('row-type-deduction');
const methodSection = document.getElementById('add-row-method-section');
const methodTemplate = document.getElementById('add-row-method-template');
const methodCustom = document.getElementById('add-row-method-custom');
const templateSection = document.getElementById('add-row-template-section');
const customSection = document.getElementById('add-row-custom-section');
const templateDropdown = document.getElementById('add-row-template-dropdown');
const templateValue = document.getElementById('add-row-template-value');
const templateSubmit = document.getElementById('add-row-template-submit');
const customHeader = document.getElementById('add-row-custom-header');
const customTax = document.getElementById('add-row-custom-tax');
const customValue = document.getElementById('add-row-custom-value');
const customSubmit = document.getElementById('add-row-custom-submit');
const errorDiv = document.getElementById('add-row-modal-error');
const addRowModalCheckbox = document.getElementById('add-custom-row-modal');
const addRowButton = document.getElementById('button-add-row');


// --- Utility: Get reserved headers and template rows from window ---
function getReservedHeaders() {
    // BUDGET_TEMPLATE and VARIABLE_TEMPLATE headers + custom row headers already in budget
    let reserved = [];
    if (window.BUDGET_TEMPLATE) {
        reserved = reserved.concat(window.BUDGET_TEMPLATE.map(r => r.header));
    }
    if (window.VARIABLE_TEMPLATE) {
        reserved = reserved.concat(window.VARIABLE_TEMPLATE.map(r => r.header));
    }
    if (window.BUDGET_DATA) {
        window.BUDGET_DATA.forEach(r => {
            if (r.custom) reserved.push(r.header);
        });
    }
    return reserved.map(h => h.toLowerCase());
}

function getTemplateRows(rowType) {
    // Only rows of type 'e' (entitlement) or 'd'/'a' (deduction/allotment) not already in budget
    let inBudget = window.BUDGET_DATA ? window.BUDGET_DATA.map(r => r.header) : [];
    let templateRows = [];
    if (window.BUDGET_TEMPLATE) {
        templateRows = window.BUDGET_TEMPLATE.filter(row => {
            if (rowType === 'e') {
                return row.type === 'e' && !inBudget.includes(row.header);
            } else if (rowType === 'd') {
                return (row.type === 'd' || row.type === 'a') && !inBudget.includes(row.header);
            }
            return false;
        });
    }
    return templateRows;
}




// reset add row modal
function resetAddRowModal() {
    selectedRowType = null;
    selectedMethod = null;
    methodSection.style.display = 'none';
    templateSection.style.display = 'none';
    customSection.style.display = 'none';
    templateDropdown.innerHTML = '';
    templateValue.value = '';
    customHeader.value = '';
    customTax.checked = false;
    customValue.value = '';
    errorDiv.textContent = '';
}


// --- Populate Template Dropdown ---
function populateTemplateDropdown(rowType) {
    templateDropdown.innerHTML = '';
    let rows = getTemplateRows(rowType);
    if (rows.length === 0) {
        let opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'No available rows';
        templateDropdown.appendChild(opt);
        templateDropdown.disabled = true;
        templateValue.disabled = true;
        templateSubmit.disabled = true;
        return;
    }
    rows.forEach(row => {
        let opt = document.createElement('option');
        opt.value = row.header;
        opt.textContent = row.longname || row.header;
        templateDropdown.appendChild(opt);
    });
    templateDropdown.disabled = false;
    templateValue.disabled = false;
    templateSubmit.disabled = false;
}


// Row type radio buttons
[rowTypeEntitlement, rowTypeDeduction].forEach(radio => {
    radio.addEventListener('change', function() {
        resetAddRowModal();
        selectedRowType = this.value;
        methodSection.style.display = 'flex';
    });
});

// Method radio buttons
[methodTemplate, methodCustom].forEach(radio => {
    radio.addEventListener('change', function() {
        templateSection.style.display = 'none';
        customSection.style.display = 'none';
        errorDiv.textContent = '';
        selectedMethod = this.value;
        if (selectedMethod === 'template') {
            templateSection.style.display = 'flex';
            populateTemplateDropdown(selectedRowType);
        } else if (selectedMethod === 'custom') {
            customSection.style.display = 'flex';
        }
    });
});

// Template submit
templateSubmit.addEventListener('click', function() {
    errorDiv.textContent = '';
    let header = templateDropdown.value;
    let value = templateValue.value.trim();
    if (!header) {
        errorDiv.textContent = 'Please select a row.';
        return;
    }
    if (!/^\d{0,4}(\.\d{0,2})?$/.test(value) || value === '') {
        errorDiv.textContent = 'Enter a valid initial value (up to 4 digits before and 2 after decimal).';
        return;
    }
    // Send AJAX to add row
    htmx.ajax('POST', '/add_custom_row', {
        target: '#budget',
        swap: 'innerHTML',
        values: {
            method: 'template',
            row_type: selectedRowType,
            header: header,
            value: value
        }
    });
    addRowModalCheckbox.checked = false;
});

// Custom submit
customSubmit.addEventListener('click', function() {
    errorDiv.textContent = '';
    let header = customHeader.value.trim();
    let tax = customTax.checked ? 'true' : 'false';
    let value = customValue.value.trim();
    let reserved = getReservedHeaders();
    if (!header) {
        errorDiv.textContent = 'Enter a row header.';
        return;
    }
    if (reserved.includes(header.toLowerCase())) {
        errorDiv.textContent = 'Row header is reserved or already used.';
        return;
    }
    if (!/^[A-Za-z0-9 _\-]{2,32}$/.test(header)) {
        errorDiv.textContent = 'Row header must be 2-32 characters, letters/numbers/spaces/-/_ only.';
        return;
    }
    if (!/^\d{0,4}(\.\d{0,2})?$/.test(value) || value === '') {
        errorDiv.textContent = 'Enter a valid initial value (up to 4 digits before and 2 after decimal).';
        return;
    }
    // Send AJAX to add row
    htmx.ajax('POST', '/add_custom_row', {
        target: '#budget',
        swap: 'innerHTML',
        values: {
            method: 'custom',
            row_type: selectedRowType,
            header: header,
            tax: tax,
            value: value
        }
    });
    addRowModalCheckbox.checked = false;
});

// --- Modal Close on Escape ---
document.addEventListener('keydown', function(e) {
    if ((e.key === 'Escape' || e.key === 'Esc') && addRowModalCheckbox.checked) {
        addRowModalCheckbox.checked = false;
        resetAddRowModal();
    }
});

// --- Reset modal when closed manually ---
addRowModalCheckbox.addEventListener('change', function() {
    if (!this.checked) resetAddRowModal();
});

// --- Expose for testing ---
window.resetAddRowModal = resetAddRowModal;