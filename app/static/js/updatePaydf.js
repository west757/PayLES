//update paydf
function updatePaydf() {
    if (!validateOptionsForm()) {
        enableAllInputs();
        return; // Block submission if validation fails
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
    });
}


function validateOptionsForm() {
    const optionsForm = document.getElementById('options-form');

    const zipInput = optionsForm.querySelector('input[name="zip_code_f"]');
    const zip = zipInput.value.trim();
    if (!/^\d{5}$/.test(zip)) {
        showToast("Zip code must be exactly 5 digits");
        return false;
    }

    return true;
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
