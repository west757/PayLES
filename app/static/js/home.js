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

    const submitCustomZipCode = document.getElementById('submit-custom-zip-code');
    submitCustomZipCode.addEventListener('input', setInputRestriction('number', 5));

    const submitCustomDependents = document.getElementById('submit-custom-dependents');
    submitCustomDependents.addEventListener('input', setInputRestriction('number', 1));

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
    const zipInput = document.getElementById('submit-custom-zip-code');
    const dependentsInput = document.getElementById('submit-custom-dependents');
    const homeOfRecordSelect = document.getElementById('submit-custom-home-of-record');

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