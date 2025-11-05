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
function getRowValue(header, key = null) {
    const pay = window.CONFIG.pay || [];
    const tsp = window.CONFIG.tsp || [];
    let row = pay.find(r => r.header === header) || tsp.find(r => r.header === header);
    if (!row) return null;
    if (key !== null) {
        return row.hasOwnProperty(key) ? row[key] : null;
    }
    return row;
}


function displayBadge(badgeName, list) {
    const badge = document.getElementById(`badge-${badgeName}`);
    if (!badge) return;
    if (list && list.length > 0) {
        badge.textContent = list.length;
        badge.style.display = 'inline-block';
    } else {
        badge.textContent = '';
        badge.style.display = 'none';
    }
}


function openDynamicModal(width = 'mid') {
    document.getElementById('modal-dynamic').checked = true;
    const modalInner = document.getElementById('modal-inner-dynamic');
    modalInner.classList.remove('modal-size-short', 'modal-size-mid', 'modal-size-wide');
    if (width === 'wide') {
        modalInner.classList.add('modal-size-wide');
    } else if (width === 'short') {
        modalInner.classList.add('modal-size-short');
    } else {
        modalInner.classList.add('modal-size-mid');
    }
}


function createStandardInput(header, field, value = '') {
    const wrapper = document.createElement('div');
    wrapper.className = 'input-wrapper';

    let input;
    let adornment = null;

    if (field === 'select') {
        input = document.createElement('select');
        let options = [];

        if (header === 'Years') {
            const now = new Date();
            const startYear = now.getFullYear();
            const endYear = startYear - 50;
            for (let y = startYear; y >= endYear; y--) {
                options.push(y);
            }
            input.classList.add('input-short');
        }

        else if (header === 'Months') {
            options = window.CONFIG.MONTHS.map(([key, _]) => key);
            input.classList.add('input-short');
        }

        else if (header === 'Branch') {
            options = Object.values(window.CONFIG.BRANCHES);
            input.classList.add('input-long');
            value = window.CONFIG.BRANCHES[value];
        }

        else if (header === 'Component') {
            options = window.CONFIG.COMPONENTS;
            input.classList.add('input-long');
        }

        else if (header === 'Grade') {
            options = window.CONFIG.GRADES;
            input.classList.add('input-short');
        }

        else if (header === 'OCONUS Country') {
            const uniqueCountries = [
                ...new Set(window.CONFIG.OCONUS_LOCATIONS.map(loc => loc.country))
            ];
            options = uniqueCountries;
            input.classList.add('input-long');
        }

        else if (header === 'Home of Record') {
            options = Object.values(window.CONFIG.HOME_OF_RECORDS);
            input.classList.add('input-long');
            value = window.CONFIG.HOME_OF_RECORDS[value];
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

        options.forEach(opt => {
            let o = document.createElement('option');
            o.value = opt;
            o.textContent = opt;
            if (opt === value) o.selected = true;
            input.appendChild(o);
        });

        wrapper.appendChild(input);
        return wrapper;
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
    }

    else if (field === 'float') {
        input = document.createElement('input');
        input.type = 'text';
        input.value = Math.abs(value);
        input.placeholder = '0.00';

        input.classList.add('input-mid');

        if (header === 'TSP Goal') {
            input.maxLength = 8;
            input.addEventListener('input', setInputRestriction('float', 5));
        }
        else{
            input.maxLength = 9;
        input.addEventListener('input', setInputRestriction('float', 6));
        }

        const isNegative = value < 0 ? true : false;
        adornment = document.createElement('span');
        adornment.textContent = isNegative ? '-$' : '$';
        adornment.className = 'input-adornment-left';
        wrapper.appendChild(adornment);
        wrapper.appendChild(input);
        return wrapper;
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

        wrapper.appendChild(input);
        return wrapper;
    }
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
            if (val.length > 1) {
                val = val.replace(/^0+/, '');
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


/**
 * Sets up a locality dropdown that is filtered by the selected country.
 * @param {string} countryDropdownId - The id of the country <select> element.
 * @param {string} localityContainerId - The id of the container where the locality dropdown will be rendered.
 */
function setOCONUSLocalityDropdown(countryDropdownId, localityContainerId) {
    const countrySelect = document.getElementById(countryDropdownId);
    const localityContainer = document.getElementById(localityContainerId);

    // Hide locality dropdown initially
    localityContainer.style.display = 'none';

    countrySelect.addEventListener('change', function () {
        const selectedCountry = countrySelect.value;
        // Filter localities for selected country
        const localities = window.CONFIG.OCONUS_LOCATIONS
            .filter(loc => loc.country === selectedCountry)
            .map(loc => loc.locality);

        // Clear and (re)create locality dropdown
        localityContainer.innerHTML = '';
        if (localities.length > 0) {
            let localityWrapper = document.createElement('div');
            let localitySelect = document.createElement('select');
            localitySelect.id = localityContainerId.replace('-location', '-id');
            localitySelect.name = 'OCONUS Locality';
            localitySelect.classList.add('input-long');
            localities.forEach(loc => {
                let o = document.createElement('option');
                o.value = loc;
                o.textContent = loc;
                localitySelect.appendChild(o);
            });
            localityWrapper.appendChild(localitySelect);
            localityContainer.appendChild(localityWrapper);
            localityContainer.style.display = '';
        } else {
            localityContainer.style.display = 'none';
        }
    });
}