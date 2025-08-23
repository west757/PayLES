// states
let selectedRowType = null;
let selectedMethod = null;


// attach inject modal event listeners
function attachInjectModalListeners() {
    const el = getInjectModalElements();
    resetInjectModal('all');

    // attach type radio button event listeners
    [el.typeEntitlement, el.typeDeduction].forEach(radio => {
        radio.addEventListener('change', function() {
            resetInjectModal('method');
            selectedRowType = this.value;
        });
    });

    // attach method radio button event listeners
    [el.methodTemplate, el.methodCustom].forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'template') {
                resetInjectModal('template');
                selectedMethod = 'template';
                populateTemplateDropdown(selectedRowType);
            } else if (this.value === 'custom') {
                resetInjectModal('custom');
                selectedMethod = 'custom';
            }
        });
    });

    // attach template button event listener
    if (el.templateButton) {
        el.templateButton.addEventListener('click', function() {
            let header = el.templateSelect.value;
            let value = el.templateValue.value.trim();

            if (!validateInject({ mode: 'template', header, value })) return;

            htmx.ajax('POST', '/update_inject', {
                target: '#budget',
                swap: 'innerHTML',
                values: {
                    method: 'template',
                    row_type: selectedRowType,
                    header: header,
                    value: value
                }
            });
            el.injectModalCheckbox.checked = false;
        });
    }

    // attach custom button event listener
    if (el.customButton) {
        el.customButton.addEventListener('click', function() {
            let header = el.customHeader.value;
            let tax = el.customTax.checked ? 'true' : 'false';
            let value = el.customValue.value.trim();

            if (!validateInject({ mode: 'custom', header, value })) return;

            htmx.ajax('POST', '/update_inject', {
                target: '#budget',
                swap: 'innerHTML',
                values: {
                    method: 'custom',
                    row_type: selectedRowType,
                    header: header,
                    value: value,
                    tax: tax
                }
            });
            el.injectModalCheckbox.checked = false;
        });
    }
}


// reset inject modal according to scope
function resetInjectModal(scope = 'all') {
    const el = getInjectModalElements();

    el.methodSection.style.display = 'none';
    el.templateSection.style.display = 'none';
    el.customSection.style.display = 'none';

    if (scope === 'all') {
        el.typeEntitlement.checked = false;
        el.typeDeduction.checked = false;
    } 
    else if (scope === 'method') {
        el.methodSection.style.display = 'flex';
        el.methodTemplate.checked = false;
        el.methodCustom.checked = false;
    } 
    else if (scope === 'template') {
        el.templateSection.style.display = 'flex';
        el.templateSelect.innerHTML = '';
        el.templateValue.value = '';
    } 
    else if (scope === 'custom') {
        el.customSection.style.display = 'flex';
        el.customHeader.value = '';
        el.customTax.checked = false;
        el.customValue.value = '';
    }
}


// get inject modal elements
function getInjectModalElements() {
    return {
        injectModalCheckbox: document.getElementById('inject'),
        typeEntitlement: document.getElementById('inject-type-entitlement'),
        typeDeduction: document.getElementById('inject-type-deduction'),
        methodSection: document.getElementById('inject-method'),
        methodTemplate: document.getElementById('inject-method-template'),
        methodCustom: document.getElementById('inject-method-custom'),
        templateSection: document.getElementById('inject-template'),
        templateSelect: document.getElementById('inject-template-select'),
        templateValue: document.getElementById('inject-template-value'),
        templateButton: document.getElementById('inject-template-button'),
        customSection: document.getElementById('inject-custom'),
        customHeader: document.getElementById('inject-custom-header'),
        customTax: document.getElementById('inject-custom-tax'),
        customValue: document.getElementById('inject-custom-value'),
        customButton: document.getElementById('inject-custom-button'),
    };
}


// validate inject inputs
function validateInject({ mode, header, value }) {
    if (mode === 'template') {
        if (!header || header === '' || header === 'select-header') {
            showToast('Please select a template row from the dropdown.');
            return false;
        }
    }

    if (mode === 'custom') {
        getReservedHeaders();

        if (!header || header.trim().length === 0) {
            showToast('Please enter a row header.');
            return false;
        }

        if (reservedHeaders.includes(header.trim().toLowerCase())) {
            showToast('Row header is reserved or already in use.');
            return false;
        }

        if (!/^[A-Za-z0-9 _\-]{2,32}$/.test(header.trim())) {
            showToast('Row header must be 2-32 characters, letters/numbers/spaces/-/_ only.');
            return false;
        }
    }

    if (!/^\d{0,4}(\.\d{0,2})?$/.test(value) || value === '') {
        showToast('Please enter a valid initial value (up to 4 digits before and 2 after decimal).');
        return false;
    }

    return true;
}


// populate the template dropdown based on the selected row type
function populateTemplateDropdown(rowType) {
    const el = getInjectModalElements();
    const templateDropdown = el.templateSelect;
    const templateValue = el.templateValue;
    const templateSubmit = el.templateButton;
    templateDropdown.innerHTML = '';

    // Add "Select a header" option
    let firstOpt = document.createElement('option');
    firstOpt.value = 'select-header';
    firstOpt.textContent = 'Select a Header';
    templateDropdown.appendChild(firstOpt);

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
            if (r.inject) reserved.push(r.header);
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