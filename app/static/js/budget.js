// states
let isEditing = false;
let currentEdit = null;


function enterEditMode(cellButton, rowHeader, colMonth, value, fieldType) {
    if (isEditing) return;

    isEditing = true;
    currentEdit = {cellButton, rowHeader, colMonth, value, fieldType};

    disableInputs([]);

    let input, inputWrapper;

    // dropdown inputs
    if (fieldType === 'select') {
        input = document.createElement('select');
        let options = [];

        if (rowHeader === 'Grade') {
            options = window.CONFIG.GRADES;
            input.classList.add('input-short');
        }
        else if (rowHeader === 'Home of Record') {
            options = window.CONFIG.HOME_OF_RECORDS;
            input.classList.add('input-short');
        }
        else if (rowHeader === 'Federal Filing Status') {
            options = ['Single', 'Married', 'Head of Household'];
            input.classList.add('input-mid');
        }
        else if (rowHeader === 'State Filing Status') {
            options = ['Single', 'Married'];
            input.classList.add('input-mid');
        }
        else if (rowHeader === 'SGLI Coverage') {
            options = window.CONFIG.SGLI_COVERAGES;
            input.classList.add('input-mid');
        }
        else if (rowHeader === 'Combat Zone') {
            options = ['No', 'Yes'];
            input.classList.add('input-short');
        }

        options.forEach(opt => {
            let o = document.createElement('option');
            o.value = opt;
            o.textContent = opt;
            if (opt === value) o.selected = true;
            input.appendChild(o);
        });
        inputWrapper = input;
    } 

    // dependents input
    else if (fieldType === 'int' && rowHeader === 'Dependents') {
        input = document.createElement('input');
        input.classList.add('table-input', 'input-short');
        input.type = 'text';
        input.maxLength = 1;
        input.placeholder = "0-9";
        input.value = '';
        input.addEventListener('input', setInputRestriction('number', 1));
        inputWrapper = input;
    }

    // tsp inputs
    else if (fieldType === 'int' && rowHeader.toLowerCase().includes('tsp')) {
        inputWrapper = document.createElement('div');
        inputWrapper.style.display = 'flex';
        inputWrapper.style.alignItems = 'center';
        inputWrapper.style.gap = '4px';

        input = document.createElement('input');
        input.classList.add('table-input', 'input-short');
        input.type = 'text';
        input.maxLength = 3;
        let numValue = String(value).replace('%', '').trim();
        input.placeholder = numValue;
        input.value = '';
        input.addEventListener('input', setInputRestriction('number', 3));

        let percentSpan = document.createElement('span');
        percentSpan.textContent = '%';

        inputWrapper.appendChild(input);
        inputWrapper.appendChild(percentSpan);
    }

    // string inputs
    else if (fieldType === 'string') {
        input = document.createElement('input');
        input.classList.add('table-input', 'input-mid');
        input.type = 'text';

        if (rowHeader === 'Zip Code') {
            input.maxLength = 5;
            input.placeholder = value;
            input.value = '';
            input.addEventListener('input', setInputRestriction('number', 5));
        } else {
            input.maxLength = 20;
            input.placeholder = value;
            input.value = '';
            input.addEventListener('input', setInputRestriction('text', 20));
        }

        inputWrapper = input;
    }

    // float inputs
    else if (fieldType === 'float') {
        inputWrapper = document.createElement('div');
        inputWrapper.style.display = 'flex';
        inputWrapper.style.alignItems = 'center';
        inputWrapper.style.gap = '4px';

        let isNegative = false;
        let numValue = value;
        if (typeof value === 'string') {
            isNegative = value.startsWith('-');
            numValue = value.replace(/[^0-9.]/g, '');
        } else if (typeof value === 'number' && value < 0) {
            isNegative = true;
            numValue = Math.abs(value).toString();
        }

        let signSpan = document.createElement('span');
        signSpan.textContent = (isNegative ? '-$' : '$');

        input = document.createElement('input');
        input.classList.add('table-input', 'input-mid2', 'input-float');
        input.type = 'text';
        input.maxLength = 7;
        input.placeholder = numValue;
        input.value = '';

        input.addEventListener('input', setInputRestriction('money'));

        inputWrapper.appendChild(signSpan);
        inputWrapper.appendChild(input);
    }

    // cell edit buttons
    cellButton.style.display = 'none';
    let cell = cellButton.parentElement;
    cell.classList.add('editing-cell');
    cell.appendChild(inputWrapper);

    let buttonContainer = document.createElement('div');
    buttonContainer.className = 'editingButtonContainer';

    let onetimeButton = document.createElement('button');
    onetimeButton.textContent = '▼';
    onetimeButton.classList.add('editing-button', 'onetime-button');
    onetimeButton.setAttribute('data-tooltip', 'One-Time Change');
    onetimeButton.onclick = function() {
        updateBudget(false);
    };

    let repeatButton = document.createElement('button');
    repeatButton.textContent = '▶';
    repeatButton.classList.add('editing-button', 'repeat-button');
    repeatButton.setAttribute('data-tooltip', 'Repeat Change');
    repeatButton.onclick = function() {
        updateBudget(true);
    };

    let cancelButton = document.createElement('button');
    cancelButton.textContent = '✖';
    cancelButton.classList.add('editing-button', 'cancel-button');
    cancelButton.setAttribute('data-tooltip', 'Cancel');
    cancelButton.onclick = function() {
        exitEditMode();
    };

    buttonContainer.appendChild(onetimeButton);
    buttonContainer.appendChild(repeatButton);
    buttonContainer.appendChild(cancelButton);

    cell.insertBefore(buttonContainer, inputWrapper);

    disableInputs([input, onetimeButton, repeatButton, cancelButton]);
}


function updateBudget(repeat) {
    let {rowHeader, colMonth, fieldType} = currentEdit;

    let input = document.querySelector('.table-input, select');
    let value = input.value;

    if (fieldType === 'int') {
        value = parseInt(value, 10);
    } else if (fieldType === 'float') {
        value = parseFloat(value);
    }

    if (!validateInput(fieldType, rowHeader, value, repeat)) return;

    exitEditMode();

    htmx.ajax('POST', '/update_budget', {
        target: '#budget',
        swap: 'innerHTML',
        values: {
            row_header: rowHeader,
            col_month: colMonth,
            value: value,
            repeat: repeat
        }
    });

    /*showToast(`Updated ${rowHeader} for ${colMonth} to ${value} (${repeat ? 'repeat' : 'onetime'})`);*/
}


function validateInput(fieldType, rowHeader, value, repeat = false) {
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

    if (fieldType === 'float') {
        if (!/^\d{0,4}(\.\d{0,2})?$/.test(value)) {
            showToast('Value must be a decimal with up to 4 digits before and 2 after the decimal.');
            return false;
        }
        if (value.length > 7) {
            showToast('Value must be at most 7 characters.');
            return false;
        }
    }
    
    if (rowHeader === 'Zip Code') {
        if (!/^\d{5}$/.test(value)) {
            showToast('Zip code must be exactly 5 digits.');
            return false;
        }
    }


    // TSP base rate validation
    if (rowHeader === 'Trad TSP Base Rate') {
        if (value > window.CONFIG.TRAD_TSP_RATE_MAX) {
            showToast(`Trad TSP Base Rate cannot be more than ${window.CONFIG.TRAD_TSP_RATE_MAX}.`);
            return false;
        }

        const month = currentEdit.colMonth;
        const rows = [
            'Trad TSP Specialty Rate',
            'Trad TSP Incentive Rate',
            'Trad TSP Bonus Rate'
        ];

        for (let r of rows) {
            const v = getBudgetValue(r, month);
            if (parseInt(v, 10) > 0 && value === 0) {
                showToast('Cannot set Trad TSP Base Rate to 0 while a specialty/incentive/bonus rate is greater than 0.');
                return false;
            }
        }
    }

    if (rowHeader === 'Roth TSP Base Rate') {
        if (value > window.CONFIG.ROTH_TSP_RATE_MAX) {
            showToast(`Roth TSP Base Rate cannot be more than ${window.CONFIG.ROTH_TSP_RATE_MAX}.`);
            return false;
        }

        const month = currentEdit.colMonth;
        const rows = [
            'Roth TSP Specialty Rate',
            'Roth TSP Incentive Rate',
            'Roth TSP Bonus Rate'
        ];

        for (let r of rows) {
            const v = getBudgetValue(r, month);
            if (parseInt(v, 10) > 0 && value === 0) {
                showToast('Cannot set Roth TSP Base Rate to 0 while a specialty/incentive/bonus rate is greater than 0.');
                return false;
            }
        }

    }

    if (
        rowHeader.includes('Specialty Rate') ||
        rowHeader.includes('Incentive Rate') ||
        rowHeader.includes('Bonus Rate')
    ) {
        if (value > 100) {
            showToast('Specialty/Incentive/Bonus Rate cannot be more than 100.');
            return false;
        }
        if (rowHeader.startsWith('Trad') && getBudgetValue('Trad TSP Base Rate', currentEdit.colMonth) === 0) {
            showToast('Cannot set Trad TSP Specialty/Incentive/Bonus Rate if base rate is 0.');
            return false;
        }
        if (rowHeader.startsWith('Roth') && getBudgetValue('Roth TSP Base Rate', currentEdit.colMonth) === 0) {
            showToast('Cannot set Roth TSP Specialty/Incentive/Bonus Rate if base rate is 0.');
            return false;
        }
    }

    if (
        repeat &&
        (rowHeader.includes('Specialty Rate') ||
         rowHeader.includes('Incentive Rate') ||
         rowHeader.includes('Bonus Rate'))
    ) {
        const months = extractMonthHeaders();
        const startIdx = months.indexOf(currentEdit.colMonth);
        const baseRow = rowHeader.startsWith('Trad') ? 'Trad TSP Base Rate' : 'Roth TSP Base Rate';
        for (let i = startIdx; i < months.length; i++) {
            const baseRate = getBudgetValue(baseRow, months[i]);
            if (parseInt(baseRate, 10) === 0) {
                showToast(`Cannot repeat specialty/incentive/bonus rate into months where base rate is 0 (${months[i]}).`);
                return false;
            }
        }
    }

    return true;
}


function exitEditMode() {
    if (!isEditing || !currentEdit) return;

    let {cellButton} = currentEdit;
    let cell = cellButton.parentElement;
    cell.classList.remove('editing-cell');

    cell.querySelectorAll('input, select, div').forEach(el => {
        if (el !== cellButton) el.remove();
    });

    cellButton.style.display = '';
    enableInputs();
    disableTSPRateButtons();
    isEditing = false;
    currentEdit = null;
}



