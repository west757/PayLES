// confirmation alert to user before changing off budget page
function budgetUnloadPrompt(e) {
    e.preventDefault();
    e.returnValue = "Please confirm to return to the home page. You will lose all existing data on this page and will be unable to return. \n\nTo save a copy of your budget, please use the export function.";
}


// show toast messages for 6 seconds and 0.5 second fade transition
function showToast(message, duration = 6500) {
    const MAX_TOASTS = 3;
    const container = document.getElementById('toast-container');

    while (container.children.length >= MAX_TOASTS) {
        container.removeChild(container.firstChild);
    }

    let toast = document.createElement('div');
    toast.className = 'toast shadow';
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


function showTooltip(evt, text) {
    const tooltipContainer = document.getElementById('tooltip-container');
    tooltipContainer.innerText = text;
    tooltipContainer.style.left = (evt.pageX + 16) + 'px';
    tooltipContainer.style.top = (evt.pageY - 16) + 'px';
    tooltipContainer.style.display = 'block';
}


function hideTooltip() {
    const tooltipContainer = document.getElementById('tooltip-container');
    tooltipContainer.style.display = 'none';
}


function disableInputs(exceptions=[]) {
    // disable all inputs except those in exceptions array
    document.querySelectorAll('input, button, select, textarea').forEach(el => {
        if (!exceptions.includes(el)) {
            el.disabled = true;
        }
    });
}


function enableInputs() {
    document.querySelectorAll('input, button, select, textarea').forEach(el => {
        el.disabled = false;
    });
}


function highlightChanges() {
    const highlight_color = getComputedStyle(document.documentElement).getPropertyValue('--highlight_yellow_color').trim();
    var checkbox = document.getElementById('checkbox-highlight');
    var table = document.getElementById('budget-table');
    var rows = table.getElementsByTagName('tr');

    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName('td');

        // get row header (first cell)
        var rowHeader = cells[0].textContent.trim();
        
        //start from month 3 (index 2), skip row header and first month
        for (var j = 2; j < cells.length; j++) {
            var cell = cells[j];
            var prevCell = cells[j - 1];

            if (
                checkbox.checked &&
                cell.textContent.trim() !== prevCell.textContent.trim() &&
                !(rowHeader === "Difference" && cell.textContent.trim() === "$0.00")
            ) {
                cell.style.backgroundColor = highlight_color;
            } else {
                cell.style.backgroundColor = '';
            }
        }
    }
}


function toggleRows(type) {
    let checkbox, rows;
    if (type === 'var') {
        checkbox = document.getElementById('checkbox-var');
        rows = document.getElementsByClassName('var-row');
    } else if (type === 'tsp') {
        checkbox = document.getElementById('checkbox-tsp');
        rows = document.getElementsByClassName('tsp-row');
    } else if (type === 'ytd') {
        checkbox = document.getElementById('checkbox-ytd');
        rows = document.getElementsByClassName('ytd-row');
    } else {
        return;
    }

    for (let row of rows) {
        row.style.display = checkbox.checked ? 'table-row' : 'none';
    }
}


function exportBudget() {
    var budgetTable = document.getElementById('budget-table');
    var filetype = document.getElementById('dropdown-export').value;
    var filename = filetype === 'xlsx' ? 'PayLES_Budget.xlsx' : 'PayLES_Budget.csv';

    var clone = budgetTable.cloneNode(true);

    // remove row buttons from export
    clone.querySelectorAll('.remove-row-button').forEach(btn => btn.remove());

    var workbook = XLSX.utils.table_to_book(clone, {sheet: "Budget", raw: true});
    if (filetype === 'xlsx') {
        XLSX.writeFile(workbook, filename);
    } else {
        XLSX.writeFile(workbook, filename, {bookType: 'csv'});
    }
}


function updateRecommendations() {
    const recs = (window.CONFIG && window.CONFIG.recommendations) || [];
    const recContent = document.getElementById('rec-content');
    const badge = document.getElementById('badge-recs');
    if (badge) {
        if (recs.length > 0) {
            badge.textContent = recs.length;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
    if (recContent) {
        if (recs.length === 0) {
            recContent.innerHTML = '<div class="rec-item">No current recommendations for your budget.</div>';
        } else {
            recContent.innerHTML = recs.map(r => `<div class="rec-item">${r}</div>`).join('');
        }
    }
}


function getBudgetValue(rowHeader, month) {
    const row = window.CONFIG.budget.find(r => r.header === rowHeader);

    if (row && row.hasOwnProperty(month)) {
        return row[month];
    }
    return '';
}


function disableTSPRateButtons() {
    const months = window.CONFIG.months;
    months.forEach(month => {
        const tradBase = getBudgetValue('Trad TSP Base Rate', month);
        const rothBase = getBudgetValue('Roth TSP Base Rate', month);

        const tradRows = [
            'Trad TSP Specialty Rate',
            'Trad TSP Incentive Rate',
            'Trad TSP Bonus Rate'
        ];
        const rothRows = [
            'Roth TSP Specialty Rate',
            'Roth TSP Incentive Rate',
            'Roth TSP Bonus Rate'
        ];

        tradRows.forEach(row => {
            const btn = document.querySelector(`.cell-button[data-row="${row}"][data-month="${month}"]`);
            if (btn) btn.disabled = (parseInt(tradBase, 10) === 0);
        });
        rothRows.forEach(row => {
            const btn = document.querySelector(`.cell-button[data-row="${row}"][data-month="${month}"]`);
            if (btn) btn.disabled = (parseInt(rothBase, 10) === 0);
        });
    });
}


function createStandardInput(rowHeader, field, value = '') {
    const wrapper = document.createElement('div');
    wrapper.className = 'input-wrapper';

    let input;
    let adornment = null;

    if (field === 'select') {
        input = document.createElement('select');
        let options = [];

        if (rowHeader === 'Year') {
            const now = new Date();
            const startYear = now.getFullYear();
            const endYear = startYear - 50;
            for (let y = startYear; y >= endYear; y--) {
                options.push(y);
            }
            input.classList.add('input-short');
        }

        else if (rowHeader === 'Months') {
            options = window.CONFIG.MONTHS_SHORT;
            input.classList.add('input-short');
        }

        else if (rowHeader === 'Home of Record Long') {
            options = window.CONFIG.HOME_OF_RECORDS.map(hor => hor.longname);
            input.classList.add('input-long');
            const defaultOption = document.createElement('option');
            defaultOption.value = "Choose an option";
            defaultOption.textContent = "Choose an option";
            input.appendChild(defaultOption);
        }

        else if (rowHeader === 'Grade') {
            options = window.CONFIG.GRADES;
            input.classList.add('input-short');
        }

        else if (rowHeader === 'Home of Record') {
            options = window.CONFIG.HOME_OF_RECORDS.map(hor => hor.abbr);
            input.classList.add('input-short');
        }

        else if (rowHeader === 'Federal Filing Status') {
            options = window.CONFIG.FEDERAL_FILING_STATUSES;
            input.classList.add('input-mid');
        }

        else if (rowHeader === 'State Filing Status') {
            options = window.CONFIG.STATE_FILING_STATUSES;
            input.classList.add('input-mid');
        }

        else if (rowHeader === 'SGLI Coverage') {
            options = window.CONFIG.SGLI_COVERAGES;
            input.classList.add('input-mid');
        }

        else if (rowHeader === 'Combat Zone') {
            options = window.CONFIG.COMBAT_ZONES;
            input.classList.add('input-short');
        }

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

        const percentHeaders = [
            'Account Bank Percent',
            'Account Bank Interest',
            'Account Special Percent',
            'Account Special Interest'
        ];
        if (percentHeaders.includes(rowHeader)) {
            input.classList.add('table-input', 'input-percent', 'input-short');
            input.placeholder = '0-100';
            input.maxLength = 3;
            input.addEventListener('input', setInputRestriction('int', 3));
            wrapper.appendChild(input);
            adornment = document.createElement('span');
            adornment.textContent = '%';
            adornment.className = 'input-adornment input-adornment-right';
            wrapper.appendChild(adornment);
            return wrapper;
        }

        else if (rowHeader === 'Dependents') {
            input.classList.add('table-input', 'input-short');
            input.placeholder = '0-9';
            input.maxLength = 1;
            input.addEventListener('input', setInputRestriction('int', 1));
        }

        else if (rowHeader && rowHeader.toLowerCase().includes('tsp')) {
            input.classList.add('table-input', 'input-percent', 'input-short');
            
            // Determine max value and maxLength
            let maxVal = 100;
            let maxLength = 3;
            if (rowHeader.toLowerCase().includes('base')) {
                if (rowHeader.toLowerCase().includes('trad')) {
                    maxVal = window.CONFIG.TRAD_TSP_RATE_MAX;
                } else if (rowHeader.toLowerCase().includes('roth')) {
                    maxVal = window.CONFIG.ROTH_TSP_RATE_MAX;
                }
                maxLength = 2;
            }
            input.placeholder = '0-' + maxVal;
            input.maxLength = maxLength;

            // Add beforeinput restriction for TSP fields
            input.addEventListener('beforeinput', function(e) {
                if (e.inputType === 'insertText') {
                    if (!/^[0-9]$/.test(e.data)) {
                        e.preventDefault();
                        return;
                    }
                    // Simulate the value after input
                    let newValue = input.value;
                    const start = input.selectionStart;
                    const end = input.selectionEnd;
                    newValue = newValue.slice(0, start) + e.data + newValue.slice(end);

                    // Prevent exceeding maxLength
                    if (newValue.length > maxLength) {
                        e.preventDefault();
                        return;
                    }
                    // Prevent exceeding maxVal
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
            adornment.className = 'input-adornment input-adornment-right';
            wrapper.appendChild(adornment);
            return wrapper;
        }

        else if (rowHeader === 'Months in Service') {
            input.classList.add('table-input', 'input-short');
            input.placeholder = '0';
            input.maxLength = 3;

            // Prevent non-numeric and >600 on beforeinput
            input.addEventListener('beforeinput', function(e) {
                if (e.inputType === 'insertText') {
                    if (!/^[0-9]$/.test(e.data)) {
                        e.preventDefault();
                        return;
                    }
                    let newValue = input.value;
                    const start = input.selectionStart;
                    const end = input.selectionEnd;
                    newValue = newValue.slice(0, start) + e.data + newValue.slice(end);

                    if (newValue.length > 3) {
                        e.preventDefault();
                        return;
                    }
                    if (newValue && parseInt(newValue, 10) > 600) {
                        e.preventDefault();
                        return;
                    }
                }
            });

            // Enforce max value and max length on input
            input.addEventListener('input', function(e) {
                let val = e.target.value.replace(/\D/g, '');
                if (val.length > 3) {
                    val = val.slice(0, 3);
                }
                if (val && parseInt(val, 10) > 600) {
                    val = '600';
                }
                e.target.value = val;
            });
        }

        else {
            input.classList.add('table-input', 'input-int', 'input-short');
            input.placeholder = '0';
            input.maxLength = 3;
            input.addEventListener('input', setInputRestriction('int', 3));
        }
    }

    else if (field === 'float') {
        input = document.createElement('input');
        input.type = 'text';

        let isNegative = false;
        let numValue = value;

        if (value < 0) {
            isNegative = true;
            numValue = Math.abs(value);
        }

        input.value = numValue;
        input.classList.add('table-input', 'input-float', 'input-mid');
        input.placeholder = '0.00';

        // Determine max digits before decimal for large number inputs
        let digitsBeforeDecimal = 4; // default: 4 before decimal, 1 for '.', 2 after = 7 total
        const largeNumInputs = [
            'YTD Income',
            'YTD Expenses',
            'YTD TSP Contribution',
            'YTD Charity',
            'Template Value',
            'Custom Value',
            'Account TSP Value',
            'Account Bank Value',
            'Account Special Value'
        ];
        if (largeNumInputs.includes(rowHeader)) {
            digitsBeforeDecimal = 6; // 6 before decimal, 1 for '.', 2 after = 9 total
        }

        input.addEventListener('input', setInputRestriction('float', digitsBeforeDecimal));

        adornment = document.createElement('span');
        adornment.textContent = isNegative ? '-$' : '$';
        adornment.className = 'input-adornment input-adornment-left';
        wrapper.appendChild(adornment);
    }

    else if (field === 'string') {
        input = document.createElement('input');
        input.type = 'text';
        input.value = value;

        if (rowHeader === 'Zip Code') {
            input.classList.add('table-input', 'input-mid');
            input.placeholder = '12345';
            input.maxLength = 5;
            input.addEventListener('input', setInputRestriction('text', 5));
        }
        else {
            input.classList.add('table-input', 'input-text');
            input.addEventListener('input', setInputRestriction('text', 20));
        }
    }

    if (input) wrapper.appendChild(input);
    return wrapper;
}



function setInputRestriction(field, maxLength = null) {
    // input restrictions for float inputs
    if (field === 'float') {
        return function(e) {
            let val = e.target.value.replace(/[^0-9.]/g, '');
            let parts = val.split('.');
            // Only allow one decimal point
            if (parts.length > 2) {
                val = parts[0] + '.' + parts.slice(1).join('');
                parts = val.split('.');
            }
            // Restrict digits before decimal
            if (maxLength && parts[0].length > maxLength) {
                parts[0] = parts[0].slice(0, maxLength);
            }
            // Restrict to 2 digits after decimal
            if (parts.length > 1 && parts[1].length > 2) {
                parts[1] = parts[1].slice(0, 2);
            }
            val = parts.length > 1 ? parts[0] + '.' + parts[1] : parts[0];
            // Prevent leading zeros unless immediately followed by a decimal
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

    // input restrictions for text inputs
    if (field === 'text') {
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

