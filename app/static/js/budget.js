// states
let isEditing = false;
let currentEdit = null;


function enterEditMode(cellButton, rowHeader, colMonth, value, fieldType) {
    if (isEditing) return;

    isEditing = true;
    currentEdit = {cellButton, rowHeader, colMonth, value, fieldType};

    showOverlay();
    disableInputsExcept([]);

    let input;

    if (fieldType === 'select') {
        input = document.createElement('select');
        let options = [];

        if (rowHeader === 'Grade') options = window.GRADES;
        else if (rowHeader === 'Home of Record') options = window.HOME_OF_RECORDS;
        else if (rowHeader === 'Federal Filing Status') options = ['Single', 'Married', 'Head of Household'];
        else if (rowHeader === 'State Filing Status') options = ['Single', 'Married'];
        else if (rowHeader === 'SGLI Coverage') options = window.SGLI_COVERAGES;
        else if (rowHeader === 'Combat Zone') options = ['No', 'Yes'];

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

    cellButton.style.display = 'none';
    let cell = cellButton.parentElement;
    cell.appendChild(input);

    let buttonContainer = document.createElement('div');
    buttonContainer.style.display = 'flex';
    buttonContainer.style.justifyContent = 'center';
    buttonContainer.style.gap = '2px';
    buttonContainer.style.marginBottom = '4px';
    buttonContainer.style.zIndex = 9999;

    let onetimeButton = document.createElement('button');
    onetimeButton.textContent = '▼';
    onetimeButton.style.background = 'green';
    onetimeButton.style.color = 'white';
    onetimeButton.onclick = function() {
        handleEditSubmit(false);
    };

    let repeatButton = document.createElement('button');
    repeatButton.textContent = '▶';
    repeatButton.style.background = 'green';
    repeatButton.style.color = 'white';
    repeatButton.onclick = function() {
        handleEditSubmit(true);
    };

    let cancelButton = document.createElement('button');
    cancelButton.textContent = '✖';
    cancelButton.style.background = 'red';
    cancelButton.style.color = 'white';
    cancelButton.onclick = function() {
        exitEditMode();
    };

    buttonContainer.appendChild(onetimeButton);
    buttonContainer.appendChild(repeatButton);
    buttonContainer.appendChild(cancelButton);

    cell.insertBefore(buttonContainer, input);

    disableInputsExcept([input, onetimeButton, repeatButton, cancelButton]);
}



function exitEditMode() {
    if (!isEditing || !currentEdit) return;

    let {cellButton} = currentEdit;
    let cell = cellButton.parentElement;

    cell.querySelectorAll('input, select, div').forEach(el => {
        if (el !== cellButton) el.remove();
    });

    cellButton.style.display = '';
    hideOverlay();
    enableAllInputs();
    isEditing = false;
    currentEdit = null;
}



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
    return true;
}



function handleEditSubmit(repeat) {
    let {rowHeader, colMonth, fieldType} = currentEdit;

    let input = document.querySelector('.input-int, .input-string, .input-decimal, select');
    let value = input.value;

    if (!validateInput(fieldType, rowHeader, value)) return;

    exitEditMode();
    update_budget_cell(rowHeader, colMonth, value, repeat);
}


function update_budget_cell(rowHeader, colMonth, value, repeat) {
    htmx.ajax('POST', '/update_cells', {
        target: '#budget',
        swap: 'innerHTML',
        values: {
            row_header: rowHeader,
            col_month: colMonth,
            value: value,
            repeat: repeat
        }
    });

    showToast(`Updated ${rowHeader} for ${colMonth} to ${value} (${repeat ? 'repeat' : 'onetime'})`);
}
