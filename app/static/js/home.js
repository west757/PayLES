function buildSubmitCustom() {
    // Zip Code
    const zipDiv = document.getElementById('submit-custom-zip-code');
    if (zipDiv) {
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'custom_zip_code';
        input.className = 'input-mid';
        input.name = 'zip_code';
        input.maxLength = 5;
        input.placeholder = '12345';
        input.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 5);
        });
        zipDiv.innerHTML = '';
        zipDiv.appendChild(input);
    }

    // Grade
    const gradeDiv = document.getElementById('submit-custom-grade');
    if (gradeDiv && window.CONFIG && window.CONFIG.GRADES) {
        const select = document.createElement('select');
        select.id = 'custom_grade';
        select.className = 'input-short';
        select.name = 'grade';
        window.CONFIG.GRADES.forEach(grade => {
            const option = document.createElement('option');
            option.value = grade;
            option.textContent = grade;
            select.appendChild(option);
        });
        gradeDiv.innerHTML = '';
        gradeDiv.appendChild(select);
    }

    // Dependents
    const dependentsDiv = document.getElementById('submit-custom-dependents');
    if (dependentsDiv) {
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'custom_dependents';
        input.className = 'input-short';
        input.name = 'dependents';
        input.maxLength = 1;
        input.placeholder = '0-9';
        input.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 1);
        });
        dependentsDiv.innerHTML = '';
        dependentsDiv.appendChild(input);
    }

    // Combat Zone
    const combatZoneDiv = document.getElementById('submit-custom-combat-zone');
    if (combatZoneDiv && window.CONFIG && window.CONFIG.COMBAT_ZONES) {
        const select = document.createElement('select');
        select.id = 'custom_combat_zone';
        select.className = 'input-short';
        select.name = 'combat_zone';
        window.CONFIG.COMBAT_ZONES.forEach(zone => {
            const option = document.createElement('option');
            option.value = zone;
            option.textContent = zone;
            select.appendChild(option);
        });
        combatZoneDiv.innerHTML = '';
        combatZoneDiv.appendChild(select);
    }

    // Home of Record
    const horDiv = document.getElementById('submit-custom-home-of-record');
    if (horDiv && window.CONFIG && window.CONFIG.HOME_OF_RECORDS) {
        const select = document.createElement('select');
        select.id = 'custom_home_of_record';
        select.className = 'input-long';
        select.name = 'home_of_record';
        window.CONFIG.HOME_OF_RECORDS.forEach(hor => {
            const option = document.createElement('option');
            option.value = hor;
            option.textContent = hor;
            select.appendChild(option);
        });
        horDiv.innerHTML = '';
        horDiv.appendChild(select);
    }

    // Federal Filing Status
    const fedDiv = document.getElementById('submit-custom-federal-filing-status');
    if (fedDiv && window.CONFIG && window.CONFIG.FEDERAL_FILING_STATUSES) {
        const select = document.createElement('select');
        select.id = 'custom_federal_filing_status';
        select.className = 'input-mid';
        select.name = 'federal_filing_status';
        window.CONFIG.FEDERAL_FILING_STATUSES.forEach(status => {
            const option = document.createElement('option');
            option.value = status;
            option.textContent = status;
            select.appendChild(option);
        });
        fedDiv.innerHTML = '';
        fedDiv.appendChild(select);
    }

    // State Filing Status
    const stateDiv = document.getElementById('submit-custom-state-filing-status');
    if (stateDiv && window.CONFIG && window.CONFIG.STATE_FILING_STATUSES) {
        const select = document.createElement('select');
        select.id = 'custom_state_filing_status';
        select.className = 'input-mid';
        select.name = 'state_filing_status';
        window.CONFIG.STATE_FILING_STATUSES.forEach(status => {
            const option = document.createElement('option');
            option.value = status;
            option.textContent = status;
            select.appendChild(option);
        });
        stateDiv.innerHTML = '';
        stateDiv.appendChild(select);
    }

    // SGLI Coverage
    const sgliDiv = document.getElementById('submit-custom-sgli-coverage');
    if (sgliDiv && window.CONFIG && window.CONFIG.SGLI_COVERAGES) {
        const select = document.createElement('select');
        select.id = 'custom_sgli_coverage';
        select.className = 'input-mid';
        select.name = 'sgli_coverage';
        window.CONFIG.SGLI_COVERAGES.forEach(sgli => {
            const option = document.createElement('option');
            option.value = sgli;
            option.textContent = sgli;
            select.appendChild(option);
        });
        sgliDiv.innerHTML = '';
        sgliDiv.appendChild(select);
    }
}


function attachHomeListeners() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const tabId = 'tab-' + btn.getAttribute('data-tab');
            const tabContent = document.getElementById(tabId);
            if (tabContent) {
                tabContent.classList.add('active');
            }
        });
    });

    buildSubmitCustom();

    const submitCustomButton = document.getElementById('submit-custom-button');
    submitCustomButton.addEventListener('click', customBudgetSubmit);

    // disable inputs on any home form submit
    document.querySelectorAll('#form-submit-single, #form-submit-joint, #form-submit-custom, #form-submit-example').forEach(form => {
        form.addEventListener('submit', function(e) {
            disableInputs();
        });
    });
}


function attachDragAndDropListeners() {
    const dropContainer = document.getElementById("submit-single-drop");
    const fileInput = document.getElementById("submit-single-input");

    if (!dropContainer || !fileInput) return;

    // prevent default browser behavior for drag/drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropContainer.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    // highlight drop area on dragenter/dragover
    ['dragenter', 'dragover'].forEach(eventName => {
        dropContainer.addEventListener(eventName, function() {
            dropContainer.classList.add('drag-active');
        }, false);
    });

    // remove highlight on dragleave/drop
    ['dragleave', 'drop'].forEach(eventName => {
        dropContainer.addEventListener(eventName, function() {
            dropContainer.classList.remove('drag-active');
        }, false);
    });

    // handle dropped files
    dropContainer.addEventListener('drop', function(e) {
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
        }
    });
}


function customBudgetSubmit(e) {
    e.preventDefault();

    if (!validateCustomBudgetForm()) {
        return;
    }

    const form = document.getElementById('form-submit-custom');
    const formData = new FormData(form);

    htmx.ajax('POST', '/route_submit_custom', {
        target: '#content',
        swap: 'innerHTML',
        values: Object.fromEntries(formData.entries())
    });
}


function validateCustomBudgetForm() {
    const zipInput = document.getElementById('custom_zip_code');
    const dependentsInput = document.getElementById('custom_dependents');
    const homeOfRecordSelect = document.getElementById('custom_home_of_record');

    if (!zipInput.value.match(/^\d{5}$/)) {
        showToast('Zip code must be exactly 5 digits.');
        return false;
    }

    if (!dependentsInput.value.match(/^\d$/)) {
        showToast('Dependents must be a single digit (0-9).');
        return false;
    }

    if (homeOfRecordSelect.value === "Select a Home of Record") {
        showToast('Please choose a home of record.');
        return false;
    }

    return true;
}