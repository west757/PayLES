function buildInitialsInputs() {
    const initialsYM = document.getElementById('initials-ym');
    if (initialsYM && window.CONFIG && window.CONFIG.MONTHS_SHORT) {
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonthIdx = now.getMonth(); 

        // Year dropdown
        const selectYear = document.createElement('select');
        selectYear.id = 'input-select-initials-ym-year';
        selectYear.className = 'input-short';
        selectYear.name = 'input-select-initials-ym-year';
        for (let y = window.CONFIG.OLDEST_YEAR; y <= currentYear; y++) {
            const option = document.createElement('option');
            option.value = y;
            option.textContent = y;
            if (y === currentYear) option.selected = true;
            selectYear.appendChild(option);
        }

        // Month dropdown
        const selectMonth = document.createElement('select');
        selectMonth.id = 'input-select-initials-ym-month';
        selectMonth.className = 'input-short';
        selectMonth.name = 'input-select-initials-ym-month';
        window.CONFIG.MONTHS_SHORT.forEach((m, idx) => {
            const option = document.createElement('option');
            option.value = m;
            option.textContent = m;
            if (idx === currentMonthIdx) option.selected = true;
            selectMonth.appendChild(option);
        });

        initialsYM.innerHTML = '';
        initialsYM.appendChild(selectYear);
        initialsYM.appendChild(selectMonth);
    }


    const initialsMonthsInService = document.getElementById('initials-mis');
    if (initialsMonthsInService) {
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'input-int-initials-mis';
        input.className = 'input-short';
        input.name = 'Months in Service';
        input.maxLength = 3;
        input.value = 0;
        input.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 3);
        });
        initialsMonthsInService.innerHTML = '';
        initialsMonthsInService.appendChild(input);
    }


    const initialsGrade = document.getElementById('initials-grade');
    if (initialsGrade && window.CONFIG && window.CONFIG.GRADES) {
        const select = document.createElement('select');
        select.id = 'input-select-initials-grade';
        select.className = 'input-short';
        select.name = 'Grade';
        window.CONFIG.GRADES.forEach(grade => {
            const option = document.createElement('option');
            option.value = grade;
            option.textContent = grade;
            select.appendChild(option);
        });
        initialsGrade.innerHTML = '';
        initialsGrade.appendChild(select);
    }


    // Dependents
    const initialsDependents = document.getElementById('initials-deps');
    if (initialsDependents) {
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'input-int-initials-deps';
        input.className = 'input-short';
        input.name = 'Dependents';
        input.maxLength = 1;
        input.placeholder = '0-9';
        input.value = 0;
        input.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 1);
        });
        initialsDependents.innerHTML = '';
        initialsDependents.appendChild(input);
    }

    // Combat Zone
    const initialsCombatZone = document.getElementById('initials-cz');
    if (initialsCombatZone && window.CONFIG && window.CONFIG.COMBAT_ZONES) {
        const select = document.createElement('select');
        select.id = 'input-select-initials-cz';
        select.className = 'input-short';
        select.name = 'Combat Zone';
        window.CONFIG.COMBAT_ZONES.forEach(zone => {
            const option = document.createElement('option');
            option.value = zone;
            option.textContent = zone;
            select.appendChild(option);
        });
        initialsCombatZone.innerHTML = '';
        initialsCombatZone.appendChild(select);
    }

    // Home of Record
    const initialsHomeOfRecord = document.getElementById('initials-hor');
    if (initialsHomeOfRecord && window.CONFIG && window.CONFIG.HOME_OF_RECORDS) {
        const select = document.createElement('select');
        select.id = 'input-select-initials-hor';
        select.className = 'input-long';
        select.name = 'Home of Record';

        // Add the "Choose an option" first
        const defaultOption = document.createElement('option');
        defaultOption.value = "Choose an option";
        defaultOption.textContent = "Choose an option";
        select.appendChild(defaultOption);

        // Add the rest from the home_of_record column
        window.CONFIG.HOME_OF_RECORDS.forEach(record => {
            const option = document.createElement('option');
            option.value = record.longname;
            option.textContent = record.longname;
            select.appendChild(option);
        });

        initialsHomeOfRecord.innerHTML = '';
        initialsHomeOfRecord.appendChild(select);
    }

    // Zip Code
    const initialsZipCode = document.getElementById('initials-zc');
    if (initialsZipCode) {
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'input-int-initials-zc';
        input.className = 'input-mid';
        input.name = 'Zip Code';
        input.maxLength = 5;
        input.placeholder = '12345';
        input.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 5);
        });
        initialsZipCode.innerHTML = '';
        initialsZipCode.appendChild(input);
    }

    // Federal Filing Status
    const initialsFederalFilingStatus = document.getElementById('initials-ffs');
    if (initialsFederalFilingStatus && window.CONFIG && window.CONFIG.FEDERAL_FILING_STATUSES) {
        const select = document.createElement('select');
        select.id = 'input-select-initials-ffs';
        select.className = 'input-mid';
        select.name = 'Federal Filing Status';
        window.CONFIG.FEDERAL_FILING_STATUSES.forEach(status => {
            const option = document.createElement('option');
            option.value = status;
            option.textContent = status;
            select.appendChild(option);
        });
        initialsFederalFilingStatus.innerHTML = '';
        initialsFederalFilingStatus.appendChild(select);
    }

    // State Filing Status
    const initialsStateFilingStatus = document.getElementById('initials-sfs');
    if (initialsStateFilingStatus && window.CONFIG && window.CONFIG.STATE_FILING_STATUSES) {
        const select = document.createElement('select');
        select.id = 'input-select-initials-sfs';
        select.className = 'input-mid';
        select.name = 'State Filing Status';
        window.CONFIG.STATE_FILING_STATUSES.forEach(status => {
            const option = document.createElement('option');
            option.value = status;
            option.textContent = status;
            select.appendChild(option);
        });
        initialsStateFilingStatus.innerHTML = '';
        initialsStateFilingStatus.appendChild(select);
    }

    // SGLI Coverage
    const initialsSgliCoverage = document.getElementById('initials-sc');
    if (initialsSgliCoverage && window.CONFIG && window.CONFIG.SGLI_COVERAGES) {
        const select = document.createElement('select');
        select.id = 'input-select-initials-sc';
        select.className = 'input-mid';
        select.name = 'SGLI Coverage';
        window.CONFIG.SGLI_COVERAGES.forEach(sgli => {
            const option = document.createElement('option');
            option.value = sgli;
            option.textContent = sgli;
            select.appendChild(option);
        });
        initialsSgliCoverage.innerHTML = '';
        initialsSgliCoverage.appendChild(select);
    }



    const tspInitials = [
        'tradbase', 'tradspecialty', 'tradincentive', 'tradbonus',
        'rothbase', 'rothspecialty', 'rothincentive', 'rothbonus'
    ];

    tspInitials.forEach(id => {
        const el = document.getElementById(`initials-${id}`);
        if (el) {
            // Create input
            const input = document.createElement('input');
            input.type = 'text';
            input.id = `input-int-initials-${id}`;
            input.className = 'input-short';
            input.name = `input-int-initials-${id}`;
            input.maxLength = 3;
            input.placeholder = '0';
            input.value = 0;
            input.addEventListener('input', function(e) {
                e.target.value = e.target.value.replace(/\D/g, '').slice(0, 3);
            });

            // Percent sign
            const percentSpan = document.createElement('span');
            percentSpan.textContent = ' %';
            percentSpan.style.marginLeft = '0.5rem';

            el.innerHTML = '';
            el.appendChild(input);
            el.appendChild(percentSpan);
        }
    });



    const ytdInitials = [
        'ytd-income', 'ytd-expenses', 'ytd-tsp-contribution', 'ytd-charity'
    ];

    ytdInitials.forEach(id => {
        const el = document.getElementById(`initials-${id}`);
        if (el) {
            // Dollar sign
            const dollarSpan = document.createElement('span');
            dollarSpan.textContent = '$';
            dollarSpan.style.marginRight = '0.5rem';

            // Create input
            const input = document.createElement('input');
            input.type = 'text';
            input.id = `input-float-initials-${id}`;
            input.className = 'input-mid2';
            input.name = `input-float-initials-${id}`;
            input.maxLength = 7;
            input.placeholder = '0.00';
            input.value = '0.00';
            input.addEventListener('input', function(e) {
                // Allow only numbers and up to one decimal point, max 2 decimals
                let val = e.target.value.replace(/[^0-9.]/g, '');
                const parts = val.split('.');
                if (parts.length > 2) val = parts[0] + '.' + parts[1];
                if (parts[1]) val = parts[0] + '.' + parts[1].slice(0,2);
                e.target.value = val.slice(0, 7);
            });

            el.innerHTML = '';
            el.appendChild(dollarSpan);
            el.appendChild(input);
        }
    });

}


function attachHomeListeners() {
    const tabButtons = document.querySelectorAll('.tab-button');
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

    buildInitialsInputs();



    // After initialsYM and initialsMonthsInService are created
    const selectYear = document.getElementById('input-select-initials-ym-year');
    const selectMonth = document.getElementById('input-select-initials-ym-month');
    const inputMIS = document.getElementById('input-int-initials-mis');

    function calculateMonthsInService(year, monthShort) {
        const now = new Date();
        const startYear = parseInt(year, 10);
        const startMonthIdx = window.CONFIG.MONTHS_SHORT.indexOf(monthShort);
        const months = (now.getFullYear() - startYear) * 12 + (now.getMonth() - startMonthIdx);
        return Math.max(months, 0);
    }

    function calculateYearMonthFromMIS(mis) {
        const now = new Date();
        let totalMonths = parseInt(mis, 10);
        if (isNaN(totalMonths) || totalMonths < 0) totalMonths = 0;
        let year = now.getFullYear();
        let monthIdx = now.getMonth();
        year -= Math.floor(totalMonths / 12);
        monthIdx -= (totalMonths % 12);
        if (monthIdx < 0) {
            year -= 1;
            monthIdx += 12;
        }
        return { year, monthShort: window.CONFIG.MONTHS_SHORT[monthIdx] };
    }

    // When year/month changes, update MIS
    if (selectYear && selectMonth && inputMIS) {
        selectYear.addEventListener('change', function() {
            inputMIS.value = calculateMonthsInService(selectYear.value, selectMonth.value);
        });
        selectMonth.addEventListener('change', function() {
            inputMIS.value = calculateMonthsInService(selectYear.value, selectMonth.value);
        });

        // When MIS changes, update year/month
        inputMIS.addEventListener('input', function() {
            const { year, monthShort } = calculateYearMonthFromMIS(inputMIS.value);
            selectYear.value = year;
            selectMonth.value = monthShort;
        });
    }




    const buttonInitials = document.getElementById('button-initials');
    buttonInitials.addEventListener('click', submitInitials);

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
    const inputIntInitialsZC = document.getElementById('input-int-initials-zc');
    const inputIntInitialsDeps = document.getElementById('input-int-initials-deps');
    const inputSelectInitialsHor = document.getElementById('input-select-initials-hor');

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