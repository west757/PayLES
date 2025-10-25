// confirmation alert to user before changing pages when budgets.html is loaded
function budgetUnloadPrompt(e) {
    e.preventDefault();
    e.returnValue = "Please confirm to return to the home page. You will lose all existing data on this page and will be unable to return. \n\nTo save a copy of your budget, please use the export function.";
}


function buildEditModal(header, month, field) {
    openDynamicModal('short');

    const content = document.getElementById('modal-content-dynamic');
    content.innerHTML = '';

    const monthLong = getRowValue('Month Long', month);
    const monthTitle = document.createElement('h2');
    monthTitle.textContent = monthLong;
    monthTitle.style.textAlign = 'center';
    content.appendChild(monthTitle);

    const row = getRowValue(header);
    type = row.type ? row.type : null;

    let headerTitleName = header;
    // if row is ent/ded/alt, use tooltip for title
    if (type === 'ent' || type === 'ded' || type === 'alt') {
        const headersList = window.CONFIG.headers || [];
        const meta = headersList.find(h => h.header === header);
        if (meta && meta.tooltip && meta.tooltip !== 'none') {
            headerTitleName = meta.tooltip;
        }
    }

    const headerTitle = document.createElement('h2');
    headerTitle.textContent = headerTitleName;
    headerTitle.style.textAlign = 'center';
    content.appendChild(headerTitle);

    let cancelOnly = false;
    const body = document.createElement('div');
    body.className = 'modal-dynamic-body';

    if (header === 'Drills') {
        const component = getRowValue('Component', month);
        if (component !== 'NG' && component !== 'RES') {
            cancelOnly = true;
            body.textContent = 'You are currently not in the National Guard or Reserves component for this month. In order to set the number of drills, you must be in that component.';
        }
    }

    const rateSIBHeaders = [
        'Trad TSP Specialty Rate', 'Trad TSP Incentive Rate', 'Trad TSP Bonus Rate',
        'Roth TSP Specialty Rate', 'Roth TSP Incentive Rate', 'Roth TSP Bonus Rate'
    ];
    if (rateSIBHeaders.includes(header)) {
        let baseHeader = header.startsWith('Trad') ? 'Trad TSP Base Rate' : 'Roth TSP Base Rate';
        const baseRate = parseFloat(getRowValue(baseHeader, month));
        if (baseRate === 0) {
            cancelOnly = true;
            body.textContent = 'You cannot set a specialty/incentive/bonus rate when ' + baseHeader + ' is 0.';
        }
    }

    if (!cancelOnly) {
        body.appendChild(createStandardInput(header, field, getRowValue(header, month)));
    }

    content.appendChild(body);

    const buttons = document.createElement('div');
    buttons.className = 'modal-dynamic-buttons';

    if (!cancelOnly) {
        const buttonOnetime = document.createElement('button');
        buttonOnetime.textContent = 'One-Time';
        buttonOnetime.classList.add('button-generic', 'button-positive');
        buttonOnetime.onclick = function() {
            submitEditModal(header, month, field, false);
        };
        buttons.appendChild(buttonOnetime);

        const buttonRepeat = document.createElement('button');
        buttonRepeat.textContent = 'Repeat';
        buttonRepeat.classList.add('button-generic', 'button-positive');
        buttonRepeat.onclick = function() {
            submitEditModal(header, month, field, true);
        };
        buttons.appendChild(buttonRepeat);
    }

    const buttonCancel = document.createElement('button');
    buttonCancel.textContent = 'Cancel';
    buttonCancel.classList.add('button-generic', 'button-negative');
    buttonCancel.onclick = function() {
        document.getElementById('modal-dynamic').checked = false;
    };
    buttons.appendChild(buttonCancel);

    content.appendChild(buttons);
}


// submit handler for modal edit
function submitEditModal(header, month, field, repeat) {
    const input = document.querySelector('#modal-content-dynamic input, #modal-content-dynamic select');
    let value = input.value;

    // remove leading zeros for int fields
    if (field === 'int' && value.length > 1) {
        value = value.replace(/^0+/, '');
    }

    if (!validateBudgetInput(field, header, value, repeat, month)) return;

    document.getElementById('modal-dynamic').checked = false;

    htmx.ajax('POST', '/route_update_cell', {
        target: '#budgets',
        swap: 'innerHTML',
        values: {
            header: header,
            month: month,
            value: value,
            repeat: repeat
        }
    });
}


function validateBudgetInput(field, header, value, repeat = false, month = null) {
    if (value === '' || value === null || value === undefined) {
        showToast('A value must be entered.');
        return false;
    }

    if (field === 'int') {
        if (isNaN(parseInt(value, 10))) {
            showToast('Value must be a number.');
            return false;
        }
    }

    if (field === 'float') {
        if (isNaN(parseFloat(value))) {
            showToast('Value must be a number.');
            return false;
        }
        if (!/^\d{0,6}(\.\d{0,2})?$/.test(value)) {
            showToast('Value must be a number up to 6 digits before and 2 digits after the decimal.');
            return false;
        }
        if (value.length > 9) {
            showToast('Value cannot be greater than 9 characters.');
            return false;
        }
    }

    if (field === 'string') {
        const invalidChars = /[^A-Za-z0-9_\- ]/;
        if (invalidChars.test(value)) {
            showToast('Text contains invalid characters. Only characters allowed are letters, numbers, underscore, hyphen, and space.');
            return false;
        }
    }
    
    // this may cause issues if zip code is N/A
    if (header === 'Zip Code') {
        if (!/^\d{5}$/.test(value)) {
            showToast('Zip code must be exactly 5 digits.');
            return false;
        }
    }

    if (
        header.includes('Base Rate') ||
        header.includes('Specialty Rate') ||
        header.includes('Incentive Rate') ||
        header.includes('Bonus Rate')
    ) {
        const months = window.CONFIG.months;
        const monthStartIndex = months.indexOf(month);
        const isTrad = header.startsWith('Trad');
        const isRoth = header.startsWith('Roth');
        let rateType = '';

        if (header.includes('Base Rate')) rateType = 'Base Rate';
        if (header.includes('Specialty Rate')) rateType = 'Specialty Rate';
        if (header.includes('Incentive Rate')) rateType = 'Incentive Rate';
        if (header.includes('Bonus Rate')) rateType = 'Bonus Rate';

        for (let i = monthStartIndex; i < months.length; i++) {
            const month = months[i];

            // get base rates for this month
            const tradTSPBaseRate = parseInt(getRowValue('Trad TSP Base Rate', month), 10) || 0;
            const rothTSPBaseRate = parseInt(getRowValue('Roth TSP Base Rate', month), 10) || 0;

            // get current values for this rate type
            let tradValue = parseInt(getRowValue(`Trad TSP ${rateType}`, month), 10) || 0;
            let rothValue = parseInt(getRowValue(`Roth TSP ${rateType}`, month), 10) || 0;

            // for the column being edited, use the new value
            if (isTrad) tradValue = parseInt(value, 10) || 0;
            if (isRoth) rothValue = parseInt(value, 10) || 0;

            // combined rate check
            if ((tradValue + rothValue) > 100) {
                showToast(`The combined percentages for ${rateType.toLowerCase()} cannot exceed 100% in ${month}.`);
                return false;
            }

            // for specialty/incentive/bonus, check associated base rate is not 0 when repeating
            if (
                repeat &&
                (rateType === 'Specialty Rate' || rateType === 'Incentive Rate' || rateType === 'Bonus Rate')
            ) {
                if (isTrad && tradTSPBaseRate === 0) {
                    showToast(`Cannot repeat ${rateType.toLowerCase()} into months where Trad base rate is 0% (${month}).`);
                    return false;
                }
                if (isRoth && rothTSPBaseRate === 0) {
                    showToast(`Cannot repeat ${rateType.toLowerCase()} into months where Roth base rate is 0% (${month}).`);
                    return false;
                }
            }

            if (!repeat) break;
        }
    }

    return true;
}