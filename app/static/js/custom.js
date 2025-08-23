// states
let selectedRowType = null;
let selectedMethod = null;

// --- Utility: Get reserved headers and template rows from window ---
function getReservedHeaders() {
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



// Helper to get all modal elements
function getCustomModalElements() {
    return {
        customModalCheckbox: document.getElementById('custom'),
        typeEntitlement: document.getElementById('custom-type-entitlement'),
        typeDeduction: document.getElementById('custom-type-deduction'),
        methodSection: document.getElementById('custom-method'),
        methodTemplate: document.getElementById('custom-method-template'),
        methodBlank: document.getElementById('custom-method-blank'),
        templateSection: document.getElementById('custom-template'),
        templateSelect: document.getElementById('custom-template-select'),
        templateValue: document.getElementById('custom-template-value'),
        templateButton: document.getElementById('custom-template-button-add'),
        blankSection: document.getElementById('custom-blank'),
        blankHeader: document.getElementById('custom-blank-header'),
        blankTax: document.getElementById('custom-blank-tax'),
        blankValue: document.getElementById('custom-blank-value'),
        blankButton: document.getElementById('custom-blank-button-add'),
    };
}



// Reset modal elements based on scope
function resetCustomModal(scope = 'all') {
    const el = getCustomModalElements();

    if (scope === 'all') {
        selectedRowType = null;
        selectedMethod = null;

        // Hide all sections except type
        if (el.methodSection) el.methodSection.style.display = 'none';
        if (el.templateSection) el.templateSection.style.display = 'none';
        if (el.blankSection) el.blankSection.style.display = 'none';

        // Reset all inputs
        if (el.templateSelect) el.templateSelect.innerHTML = '';
        if (el.templateValue) el.templateValue.value = '';
        if (el.blankHeader) el.blankHeader.value = '';
        if (el.blankTax) el.blankTax.checked = false;
        if (el.blankValue) el.blankValue.value = '';

        // Uncheck radio buttons
        if (el.typeEntitlement) el.typeEntitlement.checked = false;
        if (el.typeDeduction) el.typeDeduction.checked = false;
        if (el.methodTemplate) el.methodTemplate.checked = false;
        if (el.methodBlank) el.methodBlank.checked = false;
    }
    else if (scope === 'method') {
        selectedMethod = null;
        // Reset method, template, and blank sections
        if (el.methodTemplate) el.methodTemplate.checked = false;
        if (el.methodBlank) el.methodBlank.checked = false;
        if (el.templateSection) el.templateSection.style.display = 'none';
        if (el.blankSection) el.blankSection.style.display = 'none';
        if (el.templateSelect) el.templateSelect.innerHTML = '';
        if (el.templateValue) el.templateValue.value = '';
        if (el.blankHeader) el.blankHeader.value = '';
        if (el.blankTax) el.blankTax.checked = false;
        if (el.blankValue) el.blankValue.value = '';
        // Show method section
        if (el.methodSection) el.methodSection.style.display = 'flex';
    }
    else if (scope === 'template') {
        // Reset template section only
        if (el.templateSelect) el.templateSelect.innerHTML = '';
        if (el.templateValue) el.templateValue.value = '';
        if (el.templateSection) el.templateSection.style.display = 'flex';
        if (el.blankSection) el.blankSection.style.display = 'none';
    }
    else if (scope === 'blank') {
        // Reset blank section only
        if (el.blankHeader) el.blankHeader.value = '';
        if (el.blankTax) el.blankTax.checked = false;
        if (el.blankValue) el.blankValue.value = '';
        if (el.blankSection) el.blankSection.style.display = 'flex';
        if (el.templateSection) el.templateSection.style.display = 'none';
    }
}



// --- Attach custom modal event listeners ---
function attachCustomModalListeners() {
    const el = getCustomModalElements();

    // Initial state
    resetCustomModal('all');

    // Type radio buttons
    [el.typeEntitlement, el.typeDeduction].forEach(radio => {
        radio.addEventListener('change', function() {
            resetCustomModal('method');
            selectedRowType = this.value;
        });
    });

    // Method radio buttons
    [el.methodTemplate, el.methodBlank].forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'template') {
                resetCustomModal('template');
                selectedMethod = 'template';
                populateTemplateDropdown(selectedRowType);
            } else if (this.value === 'blank') {
                resetCustomModal('blank');
                selectedMethod = 'blank';
            }
        });
    });

    // Template submit
    if (el.templateButton) {
        el.templateButton.addEventListener('click', function() {
            let header = el.templateSelect.value;
            let value = el.templateValue.value.trim();
            if (!header) {
                showToast('Please select a row.');
                return;
            }
            if (!/^\d{0,4}(\.\d{0,2})?$/.test(value) || value === '') {
                showToast('Enter a valid initial value (up to 4 digits before and 2 after decimal).');
                return;
            }
            htmx.ajax('POST', '/update_custom', {
                target: '#budget',
                swap: 'innerHTML',
                values: {
                    method: 'template',
                    row_type: selectedRowType,
                    header: header,
                    value: value
                }
            });
            el.customModalCheckbox.checked = false;
        });
    }

    // Blank submit
    if (el.blankButton) {
        el.blankButton.addEventListener('click', function() {
            let header = el.blankHeader.value.trim();
            let tax = el.blankTax.checked ? 'true' : 'false';
            let value = el.blankValue.value.trim();
            let reserved = getReservedHeaders();
            if (!header) {
                showToast('Enter a row header.');
                return;
            }
            if (reserved.includes(header.toLowerCase())) {
                showToast('Row header is reserved or already used.');
                return;
            }
            if (!/^[A-Za-z0-9 _\-]{2,32}$/.test(header)) {
                showToast('Row header must be 2-32 characters, letters/numbers/spaces/-/_ only.');
                return;
            }
            if (!/^\d{0,4}(\.\d{0,2})?$/.test(value) || value === '') {
                showToast('Enter a valid initial value (up to 4 digits before and 2 after decimal).');
                return;
            }
            htmx.ajax('POST', '/update_custom', {
                target: '#budget',
                swap: 'innerHTML',
                values: {
                    method: 'blank',
                    row_type: selectedRowType,
                    header: header,
                    tax: tax,
                    value: value
                }
            });
            el.customModalCheckbox.checked = false;
        });
    }

    // Modal close on escape
    document.addEventListener('keydown', function(e) {
        if ((e.key === 'Escape' || e.key === 'Esc') && el.customModalCheckbox && el.customModalCheckbox.checked) {
            el.customModalCheckbox.checked = false;
            resetCustomModal('all');
        }
    });

    // Reset modal when closed manually
    if (el.customModalCheckbox) {
        el.customModalCheckbox.addEventListener('change', function() {
            if (!this.checked) resetCustomModal('all');
        });
    }
}



// --- Populate Template Dropdown ---
function populateTemplateDropdown(rowType) {
    const el = getCustomModalElements();
    const templateDropdown = el.templateSelect;
    const templateValue = el.templateValue;
    const templateSubmit = el.templateButton;
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


// Expose for main.js
window.attachCustomModalListeners = attachCustomModalListeners;
window.resetCustomModal = resetCustomModal;