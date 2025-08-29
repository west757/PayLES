// states
let selectedRowType = null;
let selectedMethod = null;


// attach inject modal event listeners
function attachInjectModalListeners() {
    const el = getInjectModalElements();
    resetInjectModal('all');

    // attach type radio button event listeners
    [el.typeEntitlement, el.typeDeduction, el.typeAllotment].forEach(radio => {
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

    //attach custom header event listener
    el.customHeader.addEventListener('input', setInputRestriction('text', 20));

    // attach template and custom value event listeners
    [el.templateValue, el.customValue].forEach(input => {
        input.addEventListener('input', setInputRestriction('money'));
    });

    // attach template button event listener
    el.templateButton.addEventListener('click', function() {
        let header = el.templateSelect.value;
        let value = el.templateValue.value.trim();

        if (!validateInject({ mode: 'template', header, value })) return;

        htmx.ajax('POST', '/add_injects', {
            target: '#budget',
            swap: 'innerHTML',
            values: {
                method: 'template',
                type: selectedRowType,
                header: header,
                value: value
            }
        });
        el.injectModalCheckbox.checked = false;
    });

    // attach custom button event listener
    el.customButton.addEventListener('click', function() {
        let header = el.customHeader.value;
        let tax = el.customTax.checked ? 'true' : 'false';
        let value = el.customValue.value.trim();

        if (!validateInject({ mode: 'custom', header, value })) return;

        htmx.ajax('POST', '/add_injects', {
            target: '#budget',
            swap: 'innerHTML',
            values: {
                method: 'custom',
                type: selectedRowType,
                header: header,
                value: value,
                tax: tax
            }
        });
        el.injectModalCheckbox.checked = false;
    });
}


// reset inject modal according to scope
function resetInjectModal(scope = 'all') {
    const el = getInjectModalElements();

    el.methodSection.style.display = 'none';
    el.templateSection.style.display = 'none';
    el.customSection.style.display = 'none';
    el.templateInfo.style.display = 'none';
    el.customInfo.style.display = 'none';

    if (scope === 'all') {
        el.typeEntitlement.checked = false;
        el.typeDeduction.checked = false;
        el.typeAllotment.checked = false;
    } 
    else if (scope === 'method') {
        el.methodSection.style.display = 'flex';
        el.methodTemplate.checked = false;
        el.methodCustom.checked = false;
    } 
    else if (scope === 'template') {
        el.methodSection.style.display = 'flex';
        el.templateSection.style.display = 'flex';
        el.templateSelect.innerHTML = '';
        el.templateValue.value = '';
        el.templateInfo.style.display = 'block';
        el.customInfo.style.display = 'none';
    } 
    else if (scope === 'custom') {
        el.methodSection.style.display = 'flex';
        el.customSection.style.display = 'flex';
        el.customHeader.value = '';
        el.customTax.checked = false;
        el.customValue.value = '';
        el.templateInfo.style.display = 'none';
        el.customInfo.style.display = 'block';

        // Set custom info based on selectedRowType
        let infoHtml = '';
        if (selectedRowType === 'e') {
            infoHtml = `<strong>Example Entitlements:</strong>
                <ul>
                    <li>Second Job</li>
                    <li>Tips</li>
                    <li>Gift Money</li>
                    <li>Rental Income</li>
                    <li>Capital Gains</li>
                    <li>Royalties</li>
                </ul>`;
        } else if (selectedRowType === 'd') {
            infoHtml = `<strong>Example Deductions:</strong>
                <ul>
                    <li>Rent</li>
                    <li>Haircuts</li>
                    <li>Groceries</li>
                    <li>Pet Expenses</li>
                    <li>Vehicle Maintenance</li>
                    <li>Insurance</li>
                    <li>Phone Plan</li>
                </ul>`;
        } else if (selectedRowType === 'a') {
            infoHtml = `<strong>Example Allotments:</strong>
                <ul>
                    <li>Child Support Payments</li>
                    <li>Alimony</li>
                </ul>`;
        } else {
            infoHtml = '';
        }
        el.customInfo.innerHTML = infoHtml;
    }
}


// get inject modal elements
function getInjectModalElements() {
    return {
        injectModalCheckbox: document.getElementById('inject'),
        typeEntitlement: document.getElementById('inject-type-entitlement'),
        typeDeduction: document.getElementById('inject-type-deduction'),
        typeAllotment: document.getElementById('inject-type-allotment'),
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
        templateInfo: document.getElementById('inject-template-info'),
        customInfo: document.getElementById('inject-custom-info'),
    };
}


// validate inject inputs
function validateInject({ mode, header, value }) {
    if (mode === 'template') {
        if (!header || header === '' || header === 'choose-header') {
            showToast('Please select a template row from the dropdown.');
            return false;
        }
    }

    if (mode === 'custom') {
        const customRows = (window.CONFIG.budget || []).filter(r => r.modal === 'inject');
        const reservedHeaders = (window.CONFIG.headers || []).map(h => h.header.toLowerCase());

        if (customRows.length >= window.CONFIG.MAX_CUSTOM_ROWS) {
            showToast('Maximum number of custom rows reached. Cannot have more than ' + window.CONFIG.MAX_CUSTOM_ROWS + ' custom rows.');
            return;
        }

        if (!header || header.trim().length === 0) {
            showToast('Please enter a row header.');
            return false;
        }

        if (reservedHeaders.includes(header.trim().toLowerCase())) {
            showToast('Row header ' + header + ' is reserved or already in use. If you are trying to create an LES-specific row, try choosing from the template options where it may already be defined.');
            return false;
        }

        if (!/^[A-Za-z0-9 _\-]{1,20}$/.test(header.trim())) {
            showToast('Row header cannot be longer than 20 characters and no special characters.');
            return false;
        }
    }

    if (!/^\d{0,4}(\.\d{0,2})?$/.test(value) || value === '') {
        showToast('Please enter a valid initial value (up to 4 digits before and 2 after decimal).');
        return false;
    }

    return true;
}


function populateTemplateDropdown(rowType) {
    const el = getInjectModalElements();
    const templateDropdown = el.templateSelect;
    const templateValue = el.templateValue;
    const templateSubmit = el.templateButton;
    const infoDiv = document.getElementById('inject-template-info');
    templateDropdown.innerHTML = '';

    // add "Select header" as first option
    let firstOpt = document.createElement('option');
    firstOpt.value = 'choose-header';
    firstOpt.textContent = 'Choose header';
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
        if (infoDiv) infoDiv.textContent = '';
        return;
    }

    rows.forEach(row => {
        let opt = document.createElement('option');
        opt.value = row.header;
        opt.textContent = row.header;
        opt.dataset.tooltip = row.tooltip || '';
        templateDropdown.appendChild(opt);
    });

    templateDropdown.disabled = false;
    templateValue.disabled = false;
    templateSubmit.disabled = false;

    // show tooltip for selected header in info div
    templateDropdown.addEventListener('change', function() {
        const selected = templateDropdown.selectedOptions[0];
        if (infoDiv) {
            infoDiv.textContent = selected && selected.dataset.tooltip ? selected.dataset.tooltip : '';
        }
    });

    if (infoDiv) infoDiv.textContent = '';
}


function getTemplateRows(rowType) {
    const headers = window.CONFIG.headers || [];
    const inBudget = window.CONFIG.budget ? window.CONFIG.budget.map(r => r.header) : [];

    let subset = headers.filter(row => {
        if (rowType === 'e') {
            return row.type === 'e';
        } else if (rowType === 'd') {
            return row.type === 'd';
        } else if (rowType === 'a') {
            return row.type === 'a';
        }
        return false;
    });

    subset = subset.filter(row => !inBudget.includes(row.header));
    subset.sort((a, b) => a.header.localeCompare(b.header));

    return subset;
}