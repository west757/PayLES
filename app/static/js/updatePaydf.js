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

    // Show all error toasts
    errors.forEach(msg => showToast(msg));

    return errors.length === 0;
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
