// load config data from hidden div into global CONFIG variable
function getConfigData() {
    const configData = JSON.parse(document.getElementById('config-data').textContent);
    window.CONFIG = Object.assign(window.CONFIG || {}, configData);
}


// show toast messages for 6 seconds and 0.5 second fade transition
function showToast(message, duration = 6500) {
    const MAX_TOASTS = 3;
    const container = document.getElementById('toast-container');

    while (container.children.length >= MAX_TOASTS) {
        container.removeChild(container.firstChild);
    }

    let toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;

    let closeButton = document.createElement('span');
    closeButton.textContent = '✖';
    closeButton.className = 'toast-close';
    closeButton.onclick = () => toast.remove();
    toast.appendChild(closeButton);

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, duration);
}


// displays tooltip overlay
function showTooltip(evt, text) {
    const tooltipContainer = document.getElementById('tooltip-container');
    tooltipContainer.innerText = text;
    tooltipContainer.style.left = (evt.pageX + 16) + 'px';
    tooltipContainer.style.top = (evt.pageY - 16) + 'px';
    tooltipContainer.style.display = 'block';
}


// hides tooltip overlay
function hideTooltip() {
    const tooltipContainer = document.getElementById('tooltip-container');
    tooltipContainer.style.display = 'none';
}


// disable all inputs except those in exceptions array
function disableInputs(exceptions=[]) {
    document.querySelectorAll('input, button, select, textarea').forEach(el => {
        if (!exceptions.includes(el)) {
            el.disabled = true;
        }
    });
}


// enable all inputs
function enableInputs() {
    document.querySelectorAll('input, button, select, textarea').forEach(el => {
        el.disabled = false;
    });
}


// format number as money string
function formatValue(value) {
    let num = Number(value);
    if (isNaN(num)) return value;
    let sign = num < 0 ? '-' : '';
    num = Math.abs(num);
    return `${sign}$${num.toFixed(2)}`;
}


// returns either the entire row object or the value for a specific key in the row
function getRowValue(budgetName, header, key = null) {
    let budget;
    if (budgetName === 'pay') {
        budget = window.CONFIG.pay;
    } else if (budgetName === 'tsp') {
        budget = window.CONFIG.tsp;
    }

    const row = budget.find(r => r.header === header);
    if (!row) return null;

    if (key !== null) {
        return row.hasOwnProperty(key) ? row[key] : null;
    }
    return row;
}


function createStandardInput(header, field, value = '') {
    const wrapper = document.createElement('div');
    wrapper.className = 'input-wrapper';

    let input;
    let adornment = null;

    if (field === 'select') {
        input = document.createElement('select');
        let options = [];

        if (header === 'Year') {
            const now = new Date();
            const startYear = now.getFullYear();
            const endYear = startYear - 50;
            for (let y = startYear; y >= endYear; y--) {
                options.push(y);
            }
            input.classList.add('input-short');
        }

        else if (header === 'Months') {
            options = Object.keys(window.CONFIG.MONTHS);
            input.classList.add('input-short');
        }

        else if (header === 'Branch') {
            options = window.CONFIG.BRANCHES_OPTIONS;
            input.classList.add('input-long');
        }

        else if (header === 'Component') {
            options = window.CONFIG.COMPONENTS_OPTIONS;
            input.classList.add('input-long');
        }

        else if (header === 'Grade') {
            options = window.CONFIG.GRADES_OPTIONS;
            input.classList.add('input-short');
        }

        else if (header === 'OCONUS Locality Code') {
            options = [];
            input.classList.add('input-long');
        }

        else if (header === 'Home of Record') {
            options = window.CONFIG.HOME_OF_RECORDS_OPTIONS;
            input.classList.add('input-long');
        }

        else if (header === 'Dependents') {
            const max = window.CONFIG.DEPENDENTS_MAX;
            options = Array.from({length: max + 1}, (_, i) => i);
            input.classList.add('input-short');
        }

        else if (header === 'Federal Filing Status') {
            options = window.CONFIG.TAX_FILING_STATUSES;
            input.classList.add('input-long');
        }

        else if (header === 'State Filing Status') {
            options = window.CONFIG.TAX_FILING_STATUSES.slice(0, 2);
            input.classList.add('input-long');
        }

        else if (header === 'SGLI Coverage') {
            options = window.CONFIG.SGLI_COVERAGES;
            input.classList.add('input-mid');
        }

        else if (header === 'Combat Zone') {
            options = window.CONFIG.COMBAT_ZONES;
            input.classList.add('input-short');
        }

        else if (header === 'Drills') {
            const max = window.CONFIG.DRILLS_MAX;
            options = Array.from({length: max + 1}, (_, i) => i);
            input.classList.add('input-short');
        }

        //else if (header === 'Home of Record Long') {
        //    options = window.CONFIG.HOME_OF_RECORDS_OPTIONS.map(hor => hor.longname);
        //    input.classList.add('input-long');
        //    const defaultOption = document.createElement('option');
        //    defaultOption.value = "Choose an option";
        //    defaultOption.textContent = "Choose an option";
        //    input.appendChild(defaultOption);
        //}

        options.forEach(opt => {
            let o = document.createElement('option');
            o.value = opt;
            o.textContent = opt;
            if (opt === value) o.selected = true;
            input.appendChild(o);
        });
    }

    else if (field === 'int') {
        input = document.createElement('input');
        input.type = 'text';
        input.value = value;

        if (header && header.toLowerCase().includes('tsp')) {
            input.classList.add('input-short');
            
            // determine max value and maxLength
            let maxVal = 100;
            let maxLength = 3;
            if (header.toLowerCase().includes('base')) {
                if (header.toLowerCase().includes('trad')) {
                    maxVal = window.CONFIG.TRAD_TSP_RATE_MAX;
                } else if (header.toLowerCase().includes('roth')) {
                    maxVal = window.CONFIG.ROTH_TSP_RATE_MAX;
                }
                maxLength = 2;
            }
            input.placeholder = '0-' + maxVal;
            input.maxLength = maxLength;

            // add beforeinput restriction for TSP fields
            input.addEventListener('beforeinput', function(e) {
                if (e.inputType === 'insertText') {
                    if (!/^[0-9]$/.test(e.data)) {
                        e.preventDefault();
                        return;
                    }
                    // simulate the value after input
                    let newValue = input.value;
                    const start = input.selectionStart;
                    const end = input.selectionEnd;
                    newValue = newValue.slice(0, start) + e.data + newValue.slice(end);

                    // prevent exceeding maxLength
                    if (newValue.length > maxLength) {
                        e.preventDefault();
                        return;
                    }
                    // prevent exceeding maxVal
                    if (newValue && parseInt(newValue, 10) > maxVal) {
                        e.preventDefault();
                        return;
                    }
                }
            });

            input.addEventListener('input', function(e) {
                let val = e.target.value.replace(/\D/g, '');
                if (maxLength && val.length > maxLength) {
                    val = val.slice(0, maxLength);
                }
                if (val && parseInt(val, 10) > maxVal) {
                    val = maxVal.toString();
                }
                e.target.value = val;
            });

            wrapper.appendChild(input);
            adornment = document.createElement('span');
            adornment.textContent = '%';
            adornment.className = 'input-adornment-right';
            wrapper.appendChild(adornment);
            return wrapper;
        }

        else {
            //input.classList.add('input-int', 'input-short');
            //input.placeholder = '0';
            //input.maxLength = 3;
            //input.addEventListener('input', setInputRestriction('int', 3));
        }
    }

    else if (field === 'float') {
        input = document.createElement('input');
        input.type = 'text';

        const isNegative = value < 0 ? true : false;

        input.value = Math.abs(value);
        input.classList.add('input-mid');
        input.placeholder = '0.00';

        // sets 6 digits before decimal, input restriction automatically handles decimal point and 2 digits after
        input.addEventListener('input', setInputRestriction('float', 6));

        adornment = document.createElement('span');
        adornment.textContent = isNegative ? '-$' : '$';
        adornment.className = 'input-adornment-left';
        wrapper.appendChild(adornment);
    }

    else if (field === 'string') {
        input = document.createElement('input');
        input.type = 'text';
        input.value = value;

        if (header === 'Zip Code') {
            input.classList.add('input-mid');
            input.placeholder = '12345';
            input.maxLength = 5;
            input.addEventListener('input', setInputRestriction('text', 5));
        }
        else {
            input.classList.add('input-long');
            input.addEventListener('input', setInputRestriction('text', 20));
        }
    }

    wrapper.appendChild(input);
    return wrapper;
}



function setInputRestriction(field, maxLength = null) {
    // input restrictions for float inputs
    if (field === 'float') {
        return function(e) {
            let val = e.target.value.replace(/[^0-9.]/g, '');
            let parts = val.split('.');

            // only allow one decimal point
            if (parts.length > 2) {
                val = parts[0] + '.' + parts.slice(1).join('');
                parts = val.split('.');
            }

            // restrict digits before decimal
            if (maxLength && parts[0].length > maxLength) {
                parts[0] = parts[0].slice(0, maxLength);
            }

            // restrict to 2 digits after decimal
            if (parts.length > 1 && parts[1].length > 2) {
                parts[1] = parts[1].slice(0, 2);
            }
            val = parts.length > 1 ? parts[0] + '.' + parts[1] : parts[0];

            // prevent leading zeros unless immediately followed by a decimal
            if (val.startsWith('00')) {
                val = val.replace(/^0+/, '0');
            } else if (val.startsWith('0') && val.length > 1 && val[1] !== '.') {
                val = val.replace(/^0+/, '');
            }
            e.target.value = val;
        };
    }

    // input restrictions for int inputs
    if (field === 'int') {
        return function(e) {
            let val = e.target.value.replace(/\D/g, '');
            if (maxLength && val.length > maxLength) {
                val = val.slice(0, maxLength);
            }
            e.target.value = val;
        };
    }

    // input restrictions for string inputs
    if (field === 'string') {
        return function(e) {
            let val = e.target.value.replace(/[^A-Za-z0-9_\- ]/g, '');
            if (maxLength && val.length > maxLength) {
                val = val.slice(0, maxLength);
            }
            e.target.value = val;
        };
    }

    return function(e) {};
}


function validateInput(field, header, value, repeat = false) {
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
            showToast('Value must be a number with up to 6 digits before and 2 digits after the decimal.');
            return false;
        }
        if (value.length > 9) {
            showToast('Value must be at most 9 characters.');
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
            const v = getRowValue('pay', r, month);
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
            const v = getRowValue('pay', r, month);
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


function addModalDynamicLine(labelText, input) {
    const inputLine = document.createElement('div');
    inputLine.className = 'input-line';

    const label = document.createElement('div');
    label.className = 'input-label';
    label.textContent = labelText;

    inputLine.appendChild(label);
    inputLine.appendChild(input);
    return inputLine;
}