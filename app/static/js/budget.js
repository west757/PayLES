// states
let isEditing = false;
let currentEdit = null;


function enterEditMode(cellButton, rowHeader, colMonth, value, fieldType) {
    if (isEditing) return;

    isEditing = true;
    currentEdit = {cellButton, rowHeader, colMonth, value, fieldType};

    //showOverlay();
    disableInputsExcept([]);

    let input, inputWrapper;

    if (fieldType === 'select') {
        input = document.createElement('select');
        let options = [];

        if (rowHeader === 'Grade') {
            options = window.GRADES;
            input.classList.add('input-short');
        }
        else if (rowHeader === 'Home of Record') {
            options = window.HOME_OF_RECORDS;
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
            options = window.SGLI_COVERAGES;
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

    else if (fieldType === 'int' && rowHeader.toLowerCase().includes('tsp')) {
        inputWrapper = document.createElement('div');
        inputWrapper.style.display = 'flex';
        inputWrapper.style.alignItems = 'center';
        inputWrapper.style.gap = '4px';

        input = document.createElement('input');
        input.classList.add('input-short');
        input.type = 'text';
        input.maxLength = 3;
        let numValue = String(value).replace('%', '').trim();
        input.placeholder = numValue;
        input.value = '';
        input.addEventListener('input', function(e) {
            input.value = input.value.replace(/\D/g, '').slice(0, 3);
        });

        let percentSpan = document.createElement('span');
        percentSpan.textContent = '%';
        percentSpan.style.marginLeft = '2px';

        inputWrapper.appendChild(input);
        inputWrapper.appendChild(percentSpan);
    }

    else if (fieldType === 'int' && rowHeader === 'Dependents') {
        input = document.createElement('input');
        input.classList.add('input-short');
        input.type = 'text';
        input.maxLength = 1;
        input.placeholder = "0-9";
        input.value = '';
        input.addEventListener('input', function(e) {
            input.value = input.value.replace(/\D/g, '').slice(0, 1);
        });
        inputWrapper = input;
    }

    else if (fieldType === 'string') {
        input = document.createElement('input');
        input.classList.add('input-mid');
        input.type = 'text';
        if (rowHeader === 'Zip Code') {
            input.maxLength = 5;
            input.placeholder = value;
            input.value = '';
            input.addEventListener('input', function(e) {
                input.value = input.value.replace(/\D/g, '').slice(0, 5);
            });
        } else {
            input.maxLength = 5;
            input.placeholder = value;
            input.value = '';
        }
        inputWrapper = input;
    }

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

        let dollarSpan = document.createElement('span');
        dollarSpan.textContent = (isNegative ? '-$' : '$');
        dollarSpan.style.marginRight = '2px';

        input = document.createElement('input');
        input.classList.add('input-mid');
        input.type = 'text';
        input.maxLength = 7;
        input.placeholder = numValue;
        input.value = '';

        inputWrapper.appendChild(dollarSpan);
        inputWrapper.appendChild(input);
    }

    else {
        input = document.createElement('input');
        input.classList.add('input-mid');
        input.type = 'text';
        input.placeholder = value;
        input.value = '';
        inputWrapper = input;
    }

    cellButton.style.display = 'none';
    let cell = cellButton.parentElement;
    cell.appendChild(inputWrapper);

    let buttonContainer = document.createElement('div');
    buttonContainer.className = 'editingButtonContainer';

    let onetimeButton = document.createElement('button');
    onetimeButton.textContent = '▼';
    onetimeButton.classList.add('editing-button', 'onetime-button');
    onetimeButton.onclick = function() {
        updateCells(false);
    };

    let repeatButton = document.createElement('button');
    repeatButton.textContent = '▶';
    repeatButton.classList.add('editing-button', 'repeat-button');
    repeatButton.onclick = function() {
        updateCells(true);
    };

    let cancelButton = document.createElement('button');
    cancelButton.textContent = '✖';
    cancelButton.classList.add('editing-button', 'cancel-button');
    cancelButton.onclick = function() {
        exitEditMode();
    };

    buttonContainer.appendChild(onetimeButton);
    buttonContainer.appendChild(repeatButton);
    buttonContainer.appendChild(cancelButton);

    cell.insertBefore(buttonContainer, inputWrapper);

    disableInputsExcept([input, onetimeButton, repeatButton, cancelButton]);
}


function updateCells(repeat) {
    let {rowHeader, colMonth, fieldType} = currentEdit;

    let input = document.querySelector('.input-int, .input-string, .input-float, select');
    let value = input.value;

    if (!validateInput(fieldType, rowHeader, value)) return;

    exitEditMode();

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
    return true;
}


function exitEditMode() {
    if (!isEditing || !currentEdit) return;

    let {cellButton} = currentEdit;
    let cell = cellButton.parentElement;

    cell.querySelectorAll('input, select, div').forEach(el => {
        if (el !== cellButton) el.remove();
    });

    cellButton.style.display = '';
    //hideOverlay();
    enableAllInputs();
    isEditing = false;
    currentEdit = null;
}