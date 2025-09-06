// states
let selectedMethod = null;
let selectedRowType = null;

// attach inject modal event listeners
function attachInjectModalListeners() {
    const el = getInjectModalElements();
    resetInjectModal();

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
            console.log("test in method radio button change");
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

    // attach input restrictions and button listeners
    el.customHeader.addEventListener('input', setInputRestriction('text', 20));
    [el.templateValue, el.customValue].forEach(input => {
        input.addEventListener('input', setInputRestriction('money'));
    });

    el.templateButton.addEventListener('click', function() {
        let method = 'template';
        let header = el.templateSelect.value;
        let value = el.templateValue.value.trim();
        if (!validateAddRow({ method, header, value })) return;

        htmx.ajax('POST', '/route_add_row', {
            target: '#budget',
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
        let tax = el.customTax.checked ? 'true' : 'false';
        let value = el.customValue.value.trim();
        if (!validateAddRow({ method, header, value })) return;

        htmx.ajax('POST', '/route_add_row', {
            target: '#budget',
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
    const el = getAccountModalElements();
    resetAccountModal();
    populateAccountRowList();

    el.accountButton.addEventListener('click', function() {
        let method = 'account';
        const header = el.accountHeader.value.trim();
        const value = el.accountValue.value.trim();
        const percent = el.accountPercent.value.trim();
        const interest = el.accountInterest.value.trim();

        let type = null;
        if (el.TypeMonthly.checked) type = el.TypeMonthly.value;
        else if (el.TypeContinuous.checked) type = el.TypeContinuous.value;
        else if (el.TypeYTD.checked) type = el.TypeYTD.value;

        const selectedRows = getSelectedAccountRows();

        if (!validateAddRow({ method, header, value, selectedRows: selectedRows, interest: interest})) return;

        htmx.ajax('POST', '/route_add_row', {
            target: '#budget',
            swap: 'innerHTML',
            values: {
                method: method,
                type: type,
                header: header,
                value: value,
                percent: percent,
                interest: interest,
                rows: selectedRows.join(',')
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
    el.templateValue.value = '';
    el.customSection.style.display = 'none';
    el.customHeader.value = '';
    el.customTax.checked = false;
    el.customValue.value = '';

    el.info.innerHTML = '';
}


function resetAccountModal() {
    const el = getAccountModalElements();

    el.accountRowSelectable.forEach(div => div.classList.remove('selected'));
    el.accountHeader.value = '';
    el.accountValue.value = '';
    el.accountPercent.value = '';
    el.accountInterest.value = '';
    el.TypeMonthly.checked = false;
    el.TypeContinuous.checked = false;
    el.TypeYTD.checked = false;
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
        customTax: document.getElementById('inject-custom-tax'),
        customValue: document.getElementById('inject-custom-value'),
        customButton: document.getElementById('inject-custom-button'),

        info: document.getElementById('inject-info')
    };
}


// get account modal elements
function getAccountModalElements() {
    return {
        accountRowSelectable: document.querySelectorAll('.account-row-selectable'),
        accountHeader: document.getElementById('account-header'),
        accountValue: document.getElementById('account-value'),
        accountPercent: document.getElementById('account-percent'),
        accountInterest: document.getElementById('account-interest'),
        TypeMonthly: document.getElementById('account-type-monthly'),
        TypeContinuous: document.getElementById('account-type-continuous'),
        TypeYTD: document.getElementById('account-type-ytd'),
        accountButton: document.getElementById('account-add-button')
    };
}


// validate inject and account inputs
function validateAddRow({ method, header, value, selectedRows, interest }) {
    if ((window.CONFIG.budget || []).length >= window.CONFIG.MAX_ROWS) {
        showToast('Maximum number of rows reached. Cannot have more than ' + window.CONFIG.MAX_ROWS + ' rows in the budget.');
        return false;
    }


    if (method === 'template') {
        if (!header || header === '' || header === 'choose-header') {
            showToast('Please select a template row from the dropdown.');
            return false;
        }
    }

    if (method === 'custom') {
        const reservedHeaders = (window.CONFIG.headers || []).map(h => h.header.toLowerCase());

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

    if (method === 'account') {
        if (!header || header.trim().length === 0) {
            showToast('Please enter an account header.');
            return false;
        }
        if (!selectedRows || selectedRows.length === 0) {
            showToast('Please select at least one row to track.');
            return false;
        }
        if (!/^\d{0,7}(\.\d{0,2})?$/.test(value)) {
            showToast('Please enter a valid initial value.');
            return false;
        }
        if (interest && !/^\d{0,2}(\.\d{0,2})?%?$/.test(interest)) {
            showToast('Please enter a valid interest rate.');
            return false;
        }
    }

    if ((mode === 'template' || mode === 'custom') && (!/^\d{0,4}(\.\d{0,2})?$/.test(value) || value === '')) {
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


function populateAccountRowList() {
    const listDiv = document.getElementById('account-row-list');
    listDiv.innerHTML = '';
    const budget = window.CONFIG.budget || [];
    const selectable = budget.filter(r => ['e','d','a','c', 'x'].includes(r.type));
    if (selectable.length === 0) {
        listDiv.textContent = 'No eligible rows available.';
        return;
    }
    selectable.forEach(row => {
        const item = document.createElement('div');
        item.className = 'account-row-selectable';
        item.textContent = row.header;
        item.dataset.header = row.header;
        item.tabIndex = 0;
        item.addEventListener('click', function() {
            item.classList.toggle('selected');
        });
        item.addEventListener('keydown', function(e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                item.classList.toggle('selected');
            }
        });
        listDiv.appendChild(item);
    });
}


function getSelectedAccountRows() {
    return Array.from(document.querySelectorAll('.account-row-selectable.selected')).map(div => div.dataset.header);
}