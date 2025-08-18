//update paydf
function updatePaydf() {
    if (!validateOptionsForm()) {
        enableAllInputs();
        return;
    }

    const optionsForm = document.getElementById('options-form');
    const settingsForm = document.getElementById('settings-form');
    const monthsDropdown = settingsForm.querySelector('[name="months_display"]');

    const formData = new FormData(optionsForm);
    formData.append('months_display', monthsDropdown.value);
    formData.append('custom_rows', JSON.stringify(customRows));

    disableAllInputs();

    fetch('/update_paydf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(html => {
        document.getElementById('paydf').innerHTML = html;
        editingIndex = null;
        highlight_changes();
        show_all_variables();
        show_tsp_options();
        updateMonthDropdowns();
        //updateButtonStates();
        renderCustomRowButtonTable();
        enableAllInputs();
        updateTspRateFields();
    });
}

// validate options form
function validateOptionsForm() {
    const optionsForm = document.getElementById('options-form');
    let errors = [];

    // validate zip code is exactly 5 digits
    const zipInput = optionsForm.querySelector('input[name="zip_code_f"]');
    const zip = zipInput.value.trim();
    if (!/^\d{5}$/.test(zip)) {
        errors.push("Zip code must be exactly 5 digits");
    }

    // validate trad tsp rates are not above max rate value
    const tradBaseRate = document.getElementById('trad_tsp_base_rate_f');
    if (tradBaseRate && parseInt(tradBaseRate.value, 10) > window.TRAD_TSP_RATE_MAX) {
        errors.push(`Trad TSP Base Rate cannot exceed ${window.TRAD_TSP_RATE_MAX}%`);
    }
    ['trad_tsp_specialty_rate_f', 'trad_tsp_incentive_rate_f', 'trad_tsp_bonus_rate_f'].forEach(id => {
        const input = document.getElementById(id);
        if (input && parseInt(input.value, 10) > 100) {
            errors.push("TSP rates cannot exceed 100%");
        }
    });

    // validate roth tsp rates are not above max rate value
    const rothBaseRate = document.getElementById('roth_tsp_base_rate_f');
    if (rothBaseRate && parseInt(rothBaseRate.value, 10) > window.ROTH_TSP_RATE_MAX) {
        errors.push(`Roth TSP Base Rate cannot exceed ${window.ROTH_TSP_RATE_MAX}%`);
    }
    ['roth_tsp_specialty_rate_f', 'roth_tsp_incentive_rate_f', 'roth_tsp_bonus_rate_f'].forEach(id => {
        const input = document.getElementById(id);
        if (input && parseInt(input.value, 10) > 100) {
            errors.push("TSP rates cannot exceed 100%");
        }
    });

    // Validate combined trad/roth rates for specialty, incentive, bonus
    const ratePairs = [
        ['trad_tsp_specialty_rate_f', 'roth_tsp_specialty_rate_f', 'Specialty'],
        ['trad_tsp_incentive_rate_f', 'roth_tsp_incentive_rate_f', 'Incentive'],
        ['trad_tsp_bonus_rate_f', 'roth_tsp_bonus_rate_f', 'Bonus']
    ];
    ratePairs.forEach(([tradId, rothId, label]) => {
        const tradVal = parseInt(document.getElementById(tradId)?.value || "0", 10);
        const rothVal = parseInt(document.getElementById(rothId)?.value || "0", 10);
        if (tradVal + rothVal > 100) {
            errors.push(`Combined Trad/Roth TSP ${label} Rate cannot exceed 100%`);
        }
    });

    // Show all error toasts
    errors.forEach(msg => showToast(msg));

    return errors.length === 0;
}




function validateTspRateMonths() {
    const colHeaders = JSON.parse(document.getElementById('button-paydf-tables').dataset.colHeaders);
    const months = colHeaders.slice(2);

    // Helper to get all changes for a type (trad/roth)
    function getBaseRateChanges(type) {
        // Collect all base rate changes (could be multiple if UI allows)
        // For now, assume one change per type
        const rate = parseInt(document.getElementById(`${type}_tsp_base_rate_f`)?.value || "0", 10);
        const month = document.getElementById(`${type}_tsp_base_rate_m`)?.value || months[0];
        return [{ month, rate }];
    }

    // Build month-by-month base rate map for trad/roth
    function buildBaseRateMap(type) {
        const changes = getBaseRateChanges(type);
        let map = [];
        let currentRate = 0;
        let changeIdx = 0;
        for (let i = 0; i < months.length; i++) {
            if (changeIdx < changes.length && months[i] === changes[changeIdx].month) {
                currentRate = changes[changeIdx].rate;
                changeIdx++;
            }
            map.push(currentRate);
        }
        return map;
    }

    const tradBaseMap = buildBaseRateMap('trad');
    const rothBaseMap = buildBaseRateMap('roth');

    // For each type and modal, update dropdowns and inputs
    ['trad', 'roth'].forEach((type) => {
        const baseMap = type === 'trad' ? tradBaseMap : rothBaseMap;
        ['specialty', 'incentive', 'bonus'].forEach((modal) => {
            const rateInput = document.getElementById(`${type}_tsp_${modal}_rate_f`);
            const monthDropdown = document.getElementById(`${type}_tsp_${modal}_rate_m`);
            if (!rateInput || !monthDropdown) return;

            // Clear and repopulate month dropdown
            monthDropdown.innerHTML = '';
            months.forEach((m, idx) => {
                const option = document.createElement('option');
                option.value = m;
                option.textContent = m;
                if (baseMap[idx] > 0) {
                    option.disabled = false;
                } else {
                    option.disabled = true;
                }
                monthDropdown.appendChild(option);
            });

            // If selected month is not available, select first available
            if (monthDropdown.options[monthDropdown.selectedIndex]?.disabled) {
                for (let i = 0; i < monthDropdown.options.length; i++) {
                    if (!monthDropdown.options[i].disabled) {
                        monthDropdown.selectedIndex = i;
                        break;
                    }
                }
            }

            // Disable input if base rate for selected month is 0
            const selectedMonthIdx = months.indexOf(monthDropdown.value);
            if (baseMap[selectedMonthIdx] === 0) {
                rateInput.value = 0;
                rateInput.disabled = true;
            } else {
                rateInput.disabled = false;
            }
        });
    });
}




// populate option month dropdowns
function updateMonthDropdowns() {
    const colHeaders = JSON.parse(document.getElementById('button-paydf-tables').dataset.colHeaders);
    const monthOptions = colHeaders.slice(2);

    document.querySelectorAll('select.month-dropdown').forEach(function(select) {
        const currentValue = select.value;
        select.innerHTML = '';

        monthOptions.forEach(function(month) {
            var option = document.createElement('option');
            option.value = month;
            option.textContent = month;

            if (month === currentValue) {
                option.selected = true;
            }

            select.appendChild(option);
        });
    });
}
