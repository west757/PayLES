// editing states
let isEditing = false;
let currentEdit = null;


function enterEditMode(cellButton, header, month, value, field) {
    if (isEditing) return;

    isEditing = true;
    currentEdit = {cellButton, header, month, value, field};

    disableInputs([]);

    // Use standardized input creation
    let inputWrapper = createStandardInput(header, field, value);

    // Find the actual input/select inside the wrapper for enabling/disabling
    let input = inputWrapper.querySelector('input, select') || inputWrapper;

    // cell edit buttons
    cellButton.style.display = 'none';
    let cell = cellButton.parentElement;
    cell.classList.add('editing-cell');
    cell.appendChild(inputWrapper);

    let buttonContainer = document.createElement('div');
    buttonContainer.className = 'editingButtonContainer';

    let onetimeButton = document.createElement('button');
    onetimeButton.textContent = '▼';
    onetimeButton.classList.add('editing-button', 'onetime-button', 'tooltip');
    onetimeButton.setAttribute('data-tooltip', 'One-Time Change');
    onetimeButton.onclick = function() {
        hideTooltip();
        updateBudget(false);
    };

    let repeatButton = document.createElement('button');
    repeatButton.textContent = '▶';
    repeatButton.classList.add('editing-button', 'repeat-button', 'tooltip');
    repeatButton.setAttribute('data-tooltip', 'Repeat Change');
    repeatButton.onclick = function() {
        hideTooltip();
        updateBudget(true);
    };

    let cancelButton = document.createElement('button');
    cancelButton.textContent = '✖';
    cancelButton.classList.add('editing-button', 'cancel-button', 'tooltip');
    cancelButton.setAttribute('data-tooltip', 'Cancel');
    cancelButton.onclick = function() {
        hideTooltip();
        exitEditMode();
    };

    buttonContainer.appendChild(onetimeButton);
    buttonContainer.appendChild(repeatButton);
    buttonContainer.appendChild(cancelButton);

    cell.insertBefore(buttonContainer, inputWrapper);

    disableInputs([input, onetimeButton, repeatButton, cancelButton]);
}


function updateBudget(repeat) {
    let {header, month, field} = currentEdit;

    let input = document.querySelector('.table-input, select');
    let value = input.value;

    if (field === 'int') {
        value = parseInt(value, 10);
    } else if (field === 'float') {
        value = parseFloat(value);
    }

    if (!validateInput(field, header, value, repeat)) return;

    exitEditMode();

    htmx.ajax('POST', '/route_update_cell', {
        target: '#budget',
        swap: 'innerHTML',
        values: {
            header: header,
            month: month,
            value: value,
            repeat: repeat
        }
    });
}


function validateInput(field, header, value, repeat = false) {
    if (value === '' || value === null || value === undefined) {
        showToast('A value must be entered.');
        return false;
    }

    if (field === 'int') {
        let num = parseInt(value, 10);
        if (isNaN(num)) {
            showToast('Value must be a number.');
            return false;
        }
        if (header.toLowerCase().includes('tsp rate') && (num < 0 || num > 100)) {
            showToast('TSP rate must be between 0 and 100.');
            return false;
        }
        if (value.length > 3) {
            showToast('Value must be at most 3 digits.');
            return false;
        }
    }

    if (field === 'float') {
        if (!/^\d{0,4}(\.\d{0,2})?$/.test(value)) {
            showToast('Value must be a decimal with up to 4 digits before and 2 after the decimal.');
            return false;
        }
        if (value.length > 7) {
            showToast('Value must be at most 7 characters.');
            return false;
        }
    }
    
    if (header === 'Zip Code') {
        if (!/^\d{5}$/.test(value)) {
            showToast('Zip code must be exactly 5 digits.');
            return false;
        }
    }


    // TSP base rate validation
    if (header === 'Trad TSP Base Rate') {
        if (value > window.CONFIG.TRAD_TSP_RATE_MAX) {
            showToast(`Trad TSP Base Rate cannot be more than ${window.CONFIG.TRAD_TSP_RATE_MAX}.`);
            return false;
        }

        const month = currentEdit.month;
        const rows = [
            'Trad TSP Specialty Rate',
            'Trad TSP Incentive Rate',
            'Trad TSP Bonus Rate'
        ];

        for (let r of rows) {
            const v = getRowValue('budget', r, month);
            if (parseInt(v, 10) > 0 && value === 0) {
                showToast('Cannot set Trad TSP Base Rate to 0 while a specialty/incentive/bonus rate is greater than 0%.');
                return false;
            }
        }
    }

    if (header === 'Roth TSP Base Rate') {
        if (value > window.CONFIG.ROTH_TSP_RATE_MAX) {
            showToast(`Roth TSP Base Rate cannot be more than ${window.CONFIG.ROTH_TSP_RATE_MAX}.`);
            return false;
        }

        const month = currentEdit.month;
        const rows = [
            'Roth TSP Specialty Rate',
            'Roth TSP Incentive Rate',
            'Roth TSP Bonus Rate'
        ];

        for (let r of rows) {
            const v = getRowValue('budget', r, month);
            if (parseInt(v, 10) > 0 && value === 0) {
                showToast('Cannot set Roth TSP Base Rate to 0 while a specialty/incentive/bonus rate is greater than 0%.');
                return false;
            }
        }

    }

    if (
        header.includes('Specialty Rate') ||
        header.includes('Incentive Rate') ||
        header.includes('Bonus Rate')
    ) {
        if (value > 100) {
            showToast('Specialty/Incentive/Bonus Rate cannot be more than 100%.');
            return false;
        }
        if (header.startsWith('Trad') && getRowValue('tsp', 'Trad TSP Base Rate', currentEdit.month) === 0) {
            showToast('Cannot set Trad TSP Specialty/Incentive/Bonus Rate if base rate is 0%.');
            return false;
        }
        if (header.startsWith('Roth') && getRowValue('tsp', 'Roth TSP Base Rate', currentEdit.month) === 0) {
            showToast('Cannot set Roth TSP Specialty/Incentive/Bonus Rate if base rate is 0%.');
            return false;
        }
    }

    
    if (repeat && (header.includes('Specialty Rate') || header.includes('Incentive Rate') || header.includes('Bonus Rate'))) {
        const months = window.CONFIG.months;
        const startIdx = months.indexOf(currentEdit.month);
        const baseRow = header.startsWith('Trad') ? 'Trad TSP Base Rate' : 'Roth TSP Base Rate';
        console.log('Repeat validation:', months.slice(startIdx), baseRow);
        for (let i = startIdx; i < months.length; i++) { // Only future months
            const baseRate = getRowValue('tsp', baseRow, months[i]);
            if (parseInt(baseRate, 10) === 0) {
                showToast(`Cannot repeat specialty/incentive/bonus rate into months where base rate is 0% (${months[i]}).`);
                return false;
            }
        }
    }

    if (header.includes('TSP Base Rate') || header.includes('Specialty Rate') || header.includes('Incentive Rate') || header.includes('Bonus Rate')) {
        const month = currentEdit.month;
        let tradValue = 0, rothValue = 0;

        if (header.startsWith('Trad')) {
            tradValue = parseInt(value, 10);
            if (header.includes('Base Rate')) rothValue = parseInt(getRowValue('tsp', 'Roth TSP Base Rate', month), 10);
            if (header.includes('Specialty Rate')) rothValue = parseInt(getRowValue('tsp', 'Roth TSP Specialty Rate', month), 10);
            if (header.includes('Incentive Rate')) rothValue = parseInt(getRowValue('tsp', 'Roth TSP Incentive Rate', month), 10);
            if (header.includes('Bonus Rate')) rothValue = parseInt(getRowValue('tsp', 'Roth TSP Bonus Rate', month), 10);
        } else if (header.startsWith('Roth')) {
            rothValue = parseInt(value, 10);
            if (header.includes('Base Rate')) tradValue = parseInt(getRowValue('tsp', 'Trad TSP Base Rate', month), 10);
            if (header.includes('Specialty Rate')) tradValue = parseInt(getRowValue('tsp', 'Trad TSP Specialty Rate', month), 10);
            if (header.includes('Incentive Rate')) tradValue = parseInt(getRowValue('tsp', 'Trad TSP Incentive Rate', month), 10);
            if (header.includes('Bonus Rate')) tradValue = parseInt(getRowValue('tsp', 'Trad TSP Bonus Rate', month), 10);
        }

        if ((tradValue + rothValue) > 100) {
            showToast('Combined Traditional and Roth TSP rates for this type cannot exceed 100%.');
            return false;
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
    disableDrillsButtons();
    disableTSPRateButtons();
    isEditing = false;
    currentEdit = null;
}
