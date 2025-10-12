// states
let selectedMethod = null;
let selectedRowType = null;

// attach inject modal event listeners
function attachInjectModalListeners() {
    resetInjectModal();

    const injectInputs = [
        { container: 'inject-template-value', field: 'float', rowHeader: 'Template Value' },
        { container: 'inject-custom-header', field: 'string', rowHeader: 'Custom Header' },
        { container: 'inject-custom-value', field: 'float', rowHeader: 'Custom Value' }
    ];

    injectInputs.forEach(item => {
        const container = document.getElementById(item.container);
        let inputWrapper = createStandardInput(item.rowHeader, item.field);
        const input = inputWrapper.querySelector('input, select');
        input.id = item.container + '-id';
        input.name = item.rowHeader;
        container.innerHTML = '';
        container.appendChild(inputWrapper);
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
            target: '#tables',
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
            target: '#tables',
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


// attach account modal event listeners
function attachAccountModalListeners() {
    //resetAccountModal();

    const injectInputs = [
        { container: 'account-tsp-header', field: 'string', rowHeader: 'Account TSP Header' },
        { container: 'account-tsp-value', field: 'float', rowHeader: 'Account TSP Value' },
        { container: 'account-tsp-interest', field: 'int', rowHeader: 'Account TSP Interest' },
        { container: 'account-bank-header', field: 'string', rowHeader: 'Account Bank Header' },
        { container: 'account-bank-value', field: 'float', rowHeader: 'Account Bank Value' },
        { container: 'account-bank-percent', field: 'int', rowHeader: 'Account Bank Percent' },
        { container: 'account-bank-interest', field: 'int', rowHeader: 'Account Bank Interest' },
        { container: 'account-special-header', field: 'string', rowHeader: 'Account Special Header' },
        { container: 'account-special-value', field: 'float', rowHeader: 'Account Special Value' },
        { container: 'account-special-percent', field: 'int', rowHeader: 'Account Special Percent' },
        { container: 'account-special-interest', field: 'int', rowHeader: 'Account Special Interest' }
    ];

    injectInputs.forEach(item => {
        const container = document.getElementById(item.container);
        let inputWrapper = createStandardInput(item.rowHeader, item.field);
        const input = inputWrapper.querySelector('input, select');
        input.id = item.container + '-id';
        input.name = item.rowHeader;
        container.innerHTML = '';
        container.appendChild(inputWrapper);
    });

    const el = getAccountModalElements();

    // method radio buttons (template/custom)
    [el.methodTSP, el.methodBank, el.methodSpecial].forEach(radio => {
        radio.addEventListener('change', function() {
            selectedMethod = this.value;
            resetAccountModal();

            if (this.value === 'tsp') {
                el.methodTSP.checked = true;
                el.accountTSP.style.display = 'flex';
            } else if (this.value === 'bank') {
                el.methodBank.checked = true;
                el.accountBank.style.display = 'flex';
            } else if (this.value === 'special') {
                el.methodSpecial.checked = true;
                el.accountSpecial.style.display = 'flex';
            }
        });
    });

    el.accountTSPButton.addEventListener('click', function() {
        let method = 'tsp';
        const header = el.accountTSPHeader.value.trim();
        const value = el.accountTSPValue.value.trim();
        const percent = 100;
        const interest = el.accountTSPInterest.value.trim();
        
        console.log({ method, header, value, percent, interest });

        if (!validateAddRow({ method, header, value, percent, interest })) return;

        htmx.ajax('POST', '/route_insert_row', {
            target: '#tables',
            swap: 'innerHTML',
            values: {
                method: method,
                header: header,
                value: value,
                interest: interest,
            }
        });
        document.getElementById('account').checked = false;
    });

    el.accountBankButton.addEventListener('click', function() {
        let method = 'bank';
        const header = el.accountBankHeader.value.trim();
        const value = el.accountBankValue.value.trim();
        const percent = el.accountBankPercent.value.trim();
        const interest = el.accountBankInterest.value.trim();

        if (!validateAddRow({ method, header, value, percent, interest })) return;

        htmx.ajax('POST', '/route_insert_row', {
            target: '#tables',
            swap: 'innerHTML',
            values: {
                method: method,
                header: header,
                value: value,
                percent: percent,
                interest: interest,
            }
        });
        document.getElementById('account').checked = false;
    });

    el.accountSpecialButton.addEventListener('click', function() {
        let method = 'special';
        const header = el.accountSpecialHeader.value.trim();
        const value = el.accountSpecialValue.value.trim();
        const percent = el.accountSpecialPercent.value.trim();
        const interest = el.accountSpecialInterest.value.trim();

        if (!validateAddRow({ method, header, value, percent, interest })) return;

        htmx.ajax('POST', '/route_insert_row', {
            target: '#tables',
            swap: 'innerHTML',
            values: {
                method: method,
                header: header,
                value: value,
                percent: percent,
                interest: interest,
            }
        });
        document.getElementById('account').checked = false;
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


function resetAccountModal() {
    const el = getAccountModalElements();

    el.methodTSP.checked = false;
    el.methodBank.checked = false;
    el.methodSpecial.checked = false;

    el.accountTSP.style.display = 'none';
    el.accountTSPHeader.value = '';
    el.accountTSPValue.value = '';
    el.accountTSPInterest.value = '0';

    el.accountBank.style.display = 'none';
    el.accountBankHeader.value = '';
    el.accountBankValue.value = '';
    el.accountBankPercent.value = '100';
    el.accountBankInterest.value = '0';

    el.accountSpecial.style.display = 'none';
    el.accountSpecialHeader.value = '';
    el.accountSpecialValue.value = '';
    el.accountSpecialPercent.value = '100';
    el.accountSpecialInterest.value = '0';
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
        templateValue: document.getElementById('inject-template-value-id'),
        templateButton: document.getElementById('inject-template-button'),

        customSection: document.getElementById('inject-custom'),
        customHeader: document.getElementById('inject-custom-header-id'),
        customValue: document.getElementById('inject-custom-value-id'),
        customTax: document.getElementById('inject-custom-tax'),
        customButton: document.getElementById('inject-custom-button'),

        info: document.getElementById('inject-info')
    };
}


// get account modal elements
function getAccountModalElements() {
    return {
        methodTSP: document.getElementById('account-method-tsp'),
        methodBank: document.getElementById('account-method-bank'),
        methodSpecial: document.getElementById('account-method-special'),

        accountTSP: document.getElementById('account-tsp'),
        accountTSPHeader: document.getElementById('account-tsp-header-id'),
        accountTSPValue: document.getElementById('account-tsp-value-id'),
        accountTSPInterest: document.getElementById('account-tsp-interest-id'),
        accountTSPButton: document.getElementById('account-tsp-button'),

        accountBank: document.getElementById('account-bank'),
        accountBankHeader: document.getElementById('account-bank-header-id'),
        accountBankValue: document.getElementById('account-bank-value-id'),
        accountBankPercent: document.getElementById('account-bank-percent-id'),
        accountBankInterest: document.getElementById('account-bank-interest-id'),
        accountBankButton: document.getElementById('account-bank-button'),

        accountSpecial: document.getElementById('account-special'),
        accountSpecialHeader: document.getElementById('account-special-header-id'),
        accountSpecialValue: document.getElementById('account-special-value-id'),
        accountSpecialPercent: document.getElementById('account-special-percent-id'),
        accountSpecialInterest: document.getElementById('account-special-interest-id'),
        accountSpecialButton: document.getElementById('account-special-button')
    };
}


function validateAddRow({ method, header, value, percent, interest }) {
    if (window.CONFIG.budget.length >= window.CONFIG.MAX_ROWS) {
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


// set custom info
function setCustomInfo(rowType, infoDiv) {
    let text = '';
    if (rowType === 'e') {
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
    } else if (rowType === 'd') {
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

