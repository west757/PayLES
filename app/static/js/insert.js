// states
let selectedMethod = null;
let selectedRowType = null;

// attach inject modal event listeners
function attachInjectModalListeners() {
    resetInjectModal();

    const injectInputs = [
        { location: 'inject-template-value-location', header: 'Inject Template Value', field: 'float' },
        { location: 'inject-custom-header-location', header: 'Inject Custom Header', field: 'string' },
        { location: 'inject-custom-value-location', header: 'Inject Custom Value', field: 'float' }
    ];

    injectInputs.forEach(item => {
        const location = document.getElementById(item.location);
        let wrapper = createStandardInput(item.header, item.field);
        const input = wrapper.querySelector('input, select');
        input.id = item.location.replace('-location', '');
        input.name = item.header;
        location.innerHTML = '';
        location.appendChild(wrapper);
    });

    const el = getInjectModalElements();

    // method radio buttons (template/custom)
    [el.methodTemplate, el.methodCustom].forEach(radio => {
        radio.addEventListener('change', function() {
            selectedMethod = this.value;
            resetInjectModal();

            if (this.value === 'template') {
                el.methodTemplate.checked = true;
                el.templateTypes.style.display = 'flex';
            } else if (this.value === 'custom') {
                el.methodCustom.checked = true;
                el.customTypes.style.display = 'flex';
            }
        });
    });

    // template row type radio buttons (entitlement/deduction/allotment)
    [el.typeEntitlement, el.typeDeduction, el.typeAllotment].forEach(radio => {
        radio.addEventListener('change', function() {
            selectedRowType = this.value;
            el.templateSection.style.display = 'flex';
            el.customSection.style.display = 'none';
            populateTemplateDropdown(selectedRowType);
        });
    });

    // custom row type radio buttons (income/expense)
    [el.typeIncome, el.typeExpense].forEach(radio => {
        radio.addEventListener('change', function() {
            selectedRowType = this.value;
            el.templateSection.style.display = 'none';
            el.customSection.style.display = 'flex';
            setCustomInfo(selectedRowType, el.info);
        });
    });

    el.templateButton.addEventListener('click', function() {
        let method = 'template';
        let header = el.templateSelect.value;
        let value = el.templateValue.value.trim();
        if (!validateAddRow({ method, header, value })) return;

        htmx.ajax('POST', '/route_insert_row', {
            target: '#budgets',
            swap: 'innerHTML',
            values: {
                method: method,
                type: selectedRowType,
                header: header,
                value: value
            }
        });
        el.injectModalCheckbox.checked = false;
    });

    el.customButton.addEventListener('click', function() {
        let method = 'custom';
        let header = el.customHeader.value;
        let value = el.customValue.value.trim();
        let tax = el.customTax.checked ? 'true' : 'false';
        if (!validateAddRow({ method, header, value })) return;

        htmx.ajax('POST', '/route_insert_row', {
            target: '#budgets',
            swap: 'innerHTML',
            values: {
                method: method,
                type: selectedRowType,
                header: header,
                value: value,
                tax: tax
            }
        });
        el.injectModalCheckbox.checked = false;
    });
}


// reset inject modal
function resetInjectModal() {
    const el = getInjectModalElements();

    el.methodTemplate.checked = false;
    el.methodCustom.checked = false;

    el.templateTypes.style.display = 'none';
    el.typeEntitlement.checked = false;
    el.typeDeduction.checked = false;
    el.typeAllotment.checked = false;

    el.customTypes.style.display = 'none';
    el.typeIncome.checked = false;
    el.typeExpense.checked = false;

    el.templateSection.style.display = 'none';
    el.templateSelect.innerHTML = '';
    el.customSection.style.display = 'none';
    el.customTax.checked = false;

    el.info.innerHTML = '';
}


// get inject modal elements
function getInjectModalElements() {
    return {
        injectModalCheckbox: document.getElementById('inject'),
        methodTemplate: document.getElementById('inject-method-template'),
        methodCustom: document.getElementById('inject-method-custom'),

        templateTypes: document.getElementById('inject-template-types'),
        typeEntitlement: document.getElementById('inject-type-entitlement'),
        typeDeduction: document.getElementById('inject-type-deduction'),
        typeAllotment: document.getElementById('inject-type-allotment'),

        customTypes: document.getElementById('inject-custom-types'),
        typeIncome: document.getElementById('inject-type-income'),
        typeExpense: document.getElementById('inject-type-expense'),

        templateSection: document.getElementById('inject-template'),
        templateSelect: document.getElementById('inject-template-select'),
        templateValue: document.getElementById('inject-template-value'),
        templateButton: document.getElementById('inject-template-button'),

        customSection: document.getElementById('inject-custom'),
        customHeader: document.getElementById('inject-custom-header'),
        customValue: document.getElementById('inject-custom-value'),
        customTax: document.getElementById('inject-custom-tax'),
        customButton: document.getElementById('inject-custom-button'),

        info: document.getElementById('inject-info')
    };
}


function validateAddRow({ method, header, value, percent, interest }) {
    if (window.CONFIG.pay.length >= window.CONFIG.MAX_ROWS) {
        showToast('Maximum number of rows reached. Cannot have more than ' + window.CONFIG.MAX_ROWS + ' rows in the budget.');
        return false;
    }

    if ((!/^\d{0,6}(\.\d{0,2})?$/.test(value) || value === '')) {
        showToast('Please enter a valid initial value (up to 6 digits before and 2 after decimal).');
        return false;
    }

    if (method === 'template') {
        if (header === 'choose-header') {
            showToast('Please select a template row from the dropdown.');
            return false;
        }
    }

    if(method === 'custom' || method === 'tsp' || method === 'bank' || method === 'special') {
        const reservedHeaders = (window.CONFIG.headers || []).map(h => h.header.toLowerCase());

        if (!header || header.trim().length === 0) {
            showToast('Please enter a row header.');
            return false;
        }

        if (reservedHeaders.includes(header.trim().toLowerCase())) {
            showToast('Row header ' + header + ' is reserved or already in use.');
            return false;
        }

        if (!/^[A-Za-z0-9 _\-]{1,20}$/.test(header.trim())) {
            showToast('Row header cannot be longer than 20 characters with no special characters.');
            return false;
        }

        if(method === 'tsp' || method === 'bank' || method === 'special') {
            if (interest == '') {
                showToast('Please enter a valid interest rate.');
                return false;
            }

            if (method === 'bank' || method === 'special') {
                if (percent == '') {
                    showToast('Please enter a valid percent rate.');
                    return false;
                }
            }
        }
    }

    return true;
}


function populateTemplateDropdown(rowType) {
    const el = getInjectModalElements();
    const templateDropdown = el.templateSelect;
    const templateValue = el.templateValue;
    const templateSubmit = el.templateButton;
    const infoDiv = document.getElementById('inject-info');
    templateDropdown.innerHTML = '';

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
    const inPay = window.CONFIG.pay ? window.CONFIG.pay.map(r => r.header) : [];

    let subset = headers.filter(row => {
        if (rowType === 'ent') {
            return row.type === 'ent';
        } else if (rowType === 'ded') {
            return row.type === 'ded';
        } else if (rowType === 'alt') {
            return row.type === 'alt';
        }
        return false;
    });

    subset = subset.filter(row => !inPay.includes(row.header));
    subset.sort((a, b) => a.header.localeCompare(b.header));

    return subset;
}


// set custom info
function setCustomInfo(rowType, infoDiv) {
    let text = '';
    if (rowType === 'inc') {
        text = `<strong>Example Income:</strong>
            <div class="inject-list-grid">
                <ul>
                    <li>Second Job</li>
                    <li>Tips</li>
                    <li>Cash Gifts</li>
                    <li>Prize Money</li>
                    <li>Interest</li>
                    <li>Sold Assets</li>
                </ul>
                <ul>
                    <li>Rental Income</li>
                    <li>Capital Gains</li>
                    <li>Royalties</li>
                    <li>Commissions</li>
                    <li>Compensation</li>
                </ul>
            </div>`;
    } else if (rowType === 'exp') {
        text = `<strong>Example Expenses:</strong>
            <div class="inject-list-grid">
                <ul>
                    <li>Rent</li>
                    <li>Utilities</li>
                    <li>Groceries</li>
                    <li>Eating Out</li>
                    <li>Gas</li>
                    <li>Clothing</li>
                    <li>Tuition</li>
                </ul>
                <ul>
                    <li>Auto Maintenance</li>
                    <li>Entertainment</li>
                    <li>Subscriptions</li>
                    <li>Travel</li>
                    <li>Insurance</li>
                    <li>Cleaning Supplies</li>
                    <li>Pet Expenses</li>
                </ul>
            </div>`;
    }
    infoDiv.innerHTML = text;
    infoDiv.style.display = text ? 'flex' : 'none';
}

