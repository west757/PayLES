function attachManualsListeners() {
    const manualsInputs = [
        { location: 'manuals-years-location', header: 'Years', field: 'select' },
        { location: 'manuals-months-location', header: 'Months', field: 'select' },
        { location: 'manuals-branch-location', header: 'Branch', field: 'select' },
        { location: 'manuals-component-location', header: 'Component', field: 'select' },
        { location: 'manuals-grade-location', header: 'Grade', field: 'select' },
        { location: 'manuals-zipcode-location', header: 'Zip Code', field: 'string' },
        { location: 'manuals-oconus-country-location', header: 'OCONUS Country', field: 'select' },
        { location: 'manuals-oconus-locality-location', header: 'OCONUS Locality', field: 'select' },
        { location: 'manuals-home-of-record-location', header: 'Home of Record', field: 'select' },
        { location: 'manuals-dependents-location', header: 'Dependents', field: 'select' },
        { location: 'manuals-federal-filing-status-location', header: 'Federal Filing Status', field: 'select' },
        { location: 'manuals-state-filing-status-location', header: 'State Filing Status', field: 'select' },
        { location: 'manuals-sgli-coverage-location', header: 'SGLI Coverage', field: 'select' },
        { location: 'manuals-drills-location', header: 'Drills', field: 'select' },
        { location: 'manuals-trad-base-rate-location', header: 'Trad TSP Base Rate', field: 'int' },
        { location: 'manuals-trad-specialty-rate-location', header: 'Trad TSP Specialty Rate', field: 'int' },
        { location: 'manuals-trad-incentive-rate-location', header: 'Trad TSP Incentive Rate', field: 'int' },
        { location: 'manuals-trad-bonus-rate-location', header: 'Trad TSP Bonus Rate', field: 'int' },
        { location: 'manuals-roth-base-rate-location', header: 'Roth TSP Base Rate', field: 'int' },
        { location: 'manuals-roth-specialty-rate-location', header: 'Roth TSP Specialty Rate', field: 'int' },
        { location: 'manuals-roth-incentive-rate-location', header: 'Roth TSP Incentive Rate', field: 'int' },
        { location: 'manuals-roth-bonus-rate-location', header: 'Roth TSP Bonus Rate', field: 'int' },
        { location: 'manuals-trad-ytd-location', header: 'YTD Trad TSP', field: 'float' },
        { location: 'manuals-trad-exempt-ytd-location', header: 'YTD Trad TSP Exempt', field: 'float' },
        { location: 'manuals-roth-ytd-location', header: 'YTD Roth TSP', field: 'float' },
        { location: 'manuals-agency-match-ytd-location', header: 'YTD Agency Match', field: 'float' },
        { location: 'manuals-agency-auto-ytd-location', header: 'YTD Agency Auto', field: 'float' },
    ];

    manualsInputs.forEach(item => {
        const location = document.getElementById(item.location);
        let wrapper = createStandardInput(item.header, item.field);
        const input = wrapper.querySelector('input, select');
        input.id = item.location.replace('-location', '');
        input.name = item.header;
        location.innerHTML = '';
        location.appendChild(wrapper);
    });

    setOCONUSLocalityDropdown('manuals-oconus-country', 'manuals-oconus-locality-location');
}


function attachHomeListeners() {
    const tabButtons = document.querySelectorAll('.button-tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => {
                c.classList.remove('active');
                // remove display block immediately, but allow fade out
                c.style.display = '';
            });
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            const tabContent = document.getElementById(tabId);

            tabContent.style.display = 'block';
            void tabContent.offsetWidth;
            tabContent.classList.add('active');
        });
    });

    attachManualsListeners();
    const buttonManuals = document.getElementById('button-manuals');
    buttonManuals.addEventListener('click', submitManuals);

    // disable inputs on any home form submit
    document.querySelectorAll('#form-single, #form-joint, #form-manuals, #form-example').forEach(form => {
        form.addEventListener('submit', function(e) {
            disableInputs();
        });
    });
}


function attachDragAndDropListeners() {
    const inputFiledrop = document.getElementById("input-filedrop");
    const inputFileSingle = document.getElementById("input-file-single");

    // prevent default browser behavior for drag/drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        inputFiledrop.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    // highlight drop area on dragenter/dragover
    ['dragenter', 'dragover'].forEach(eventName => {
        inputFiledrop.addEventListener(eventName, function() {
            inputFiledrop.classList.add('drag-active');
        }, false);
    });

    // remove highlight on dragleave/drop
    ['dragleave', 'drop'].forEach(eventName => {
        inputFiledrop.addEventListener(eventName, function() {
            inputFiledrop.classList.remove('drag-active');
        }, false);
    });

    // handle dropped files
    inputFiledrop.addEventListener('drop', function(e) {
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            inputFileSingle.files = e.dataTransfer.files;
        }
    });
}


function submitManuals(e) {
    e.preventDefault();

    //if (!validateManuals()) return;

    const form = document.getElementById('form-manuals');
    const formData = new FormData(form);

    htmx.ajax('POST', '/route_manual', {
        target: '#content',
        swap: 'innerHTML',
        values: Object.fromEntries(formData.entries())
    });
}


function validateManuals() {
    const inputIntmanualsZC = document.getElementById('manuals-zip-code-id');
    const inputIntmanualsDeps = document.getElementById('manuals-dependents-id');
    const inputSelectmanualsHor = document.getElementById('manuals-home-of-record-id');

    if (!inputIntmanualsZC.value.match(/^\d{5}$/)) {
        showToast('Zip code must be exactly 5 digits.');
        return false;
    }

    if (!inputIntmanualsDeps.value.match(/^\d$/)) {
        showToast('Dependents must be a single digit (0-9).');
        return false;
    }

    if (inputSelectmanualsHor.value === "Choose an option") {
        showToast('Please choose a home of record.');
        return false;
    }

    return true;
}