function buildManualInputs() {
    const manuals = [
        { container: 'manual-year', field: 'select', rowHeader: 'Year' },
        { container: 'manual-month', field: 'select', rowHeader: 'Months' },
        { container: 'manual-branch', field: 'select', rowHeader: 'Branch' },
        { container: 'manual-component', field: 'select', rowHeader: 'Component' },
        { container: 'manual-grade', field: 'select', rowHeader: 'Grade' },
        { container: 'manual-zip-code', field: 'string', rowHeader: 'Zip Code' },
        { container: 'manual-oconus-locality-code', field: 'string', rowHeader: 'OCONUS Locality Code' },
        { container: 'manual-home-of-record', field: 'select', rowHeader: 'Home of Record Long' },
        { container: 'manual-dependents', field: 'select', rowHeader: 'Dependents' },
        { container: 'manual-federal-filing-status', field: 'select', rowHeader: 'Federal Filing Status' },
        { container: 'manual-state-filing-status', field: 'select', rowHeader: 'State Filing Status' },
        { container: 'manual-sgli-coverage', field: 'select', rowHeader: 'SGLI Coverage' },
        { container: 'manual-combat-zone', field: 'select', rowHeader: 'Combat Zone' },
        { container: 'manual-drills', field: 'select', rowHeader: 'Drills' },
    ];

    manuals.forEach(manual => {
        const container = document.getElementById(manual.container);
        let inputWrapper = createStandardInput(manual.rowHeader, manual.field);
        const input = inputWrapper.querySelector('input, select');
        input.id = manual.container + '-id';
        input.name = manual.rowHeader;
        container.innerHTML = '';
        container.appendChild(inputWrapper);
    });
}


function attachHomeListeners() {
    const tabButtons = document.querySelectorAll('.button-tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            const tabContent = document.getElementById(tabId);
            tabContent.classList.add('active');
        });
    });

    //buildInitialsInputs();


    //const buttonInitials = document.getElementById('button-initials');
    //buttonInitials.addEventListener('click', submitInitials);

    // disable inputs on any home form submit
    document.querySelectorAll('#form-single, #form-joint, #form-initials, #form-example').forEach(form => {
        form.addEventListener('submit', function(e) {
            disableInputs();
        });
    });
}


function attachDragAndDropListeners() {
    const inputFiledropSingle = document.getElementById("input-filedrop-single");
    const inputFileSingle = document.getElementById("input-file-single");

    if (!inputFiledropSingle || !inputFileSingle) return;

    // prevent default browser behavior for drag/drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        inputFiledropSingle.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    // highlight drop area on dragenter/dragover
    ['dragenter', 'dragover'].forEach(eventName => {
        inputFiledropSingle.addEventListener(eventName, function() {
            inputFiledropSingle.classList.add('drag-active');
        }, false);
    });

    // remove highlight on dragleave/drop
    ['dragleave', 'drop'].forEach(eventName => {
        inputFiledropSingle.addEventListener(eventName, function() {
            inputFiledropSingle.classList.remove('drag-active');
        }, false);
    });

    // handle dropped files
    inputFiledropSingle.addEventListener('drop', function(e) {
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            inputFileSingle.files = e.dataTransfer.files;
        }
    });
}


function submitInitials(e) {
    e.preventDefault();

    if (!validateinitialsBudgetForm()) {
        return;
    }

    const form = document.getElementById('form-initials');
    const formData = new FormData(form);

    htmx.ajax('POST', '/route_initials', {
        target: '#content',
        swap: 'innerHTML',
        values: Object.fromEntries(formData.entries())
    });
}


function validateinitialsBudgetForm() {
    const inputIntInitialsZC = document.getElementById('initials-zip-code-id');
    const inputIntInitialsDeps = document.getElementById('initials-dependents-id');
    const inputSelectInitialsHor = document.getElementById('initials-home-of-record-id');

    if (!inputIntInitialsZC.value.match(/^\d{5}$/)) {
        showToast('Zip code must be exactly 5 digits.');
        return false;
    }

    if (!inputIntInitialsDeps.value.match(/^\d$/)) {
        showToast('Dependents must be a single digit (0-9).');
        return false;
    }

    if (inputSelectInitialsHor.value === "Choose an option") {
        showToast('Please choose a home of record.');
        return false;
    }

    return true;
}