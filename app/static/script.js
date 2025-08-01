const DEFAULT_MONTHS_DISPLAY = 4;
const MONTHS_SHORT = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];

// drag and drop functionality for file input
var dropContainer = document.getElementById("home-drop");
var fileInput = document.getElementById("home-input");

dropContainer.addEventListener("dragover", function (e) {
    e.preventDefault();
}, false);

dropContainer.addEventListener("dragenter", function () {
    dropContainer.classList.add("drag-active");
});

dropContainer.addEventListener("dragleave", function () {
    dropContainer.classList.remove("drag-active");
});

dropContainer.addEventListener("drop", function (e) {
    e.preventDefault();
    dropContainer.classList.remove("drag-active");
    fileInput.files = e.dataTransfer.files;
});



function getInitialMonth() {
    const el = document.getElementById('initial-month');
    return el ? el.value : MONTHS_SHORT[0];
}


function getMonthOptions(initialMonth, monthsDisplay) {
    let idx = MONTHS_SHORT.indexOf(initialMonth);
    let options = [];
    for (let i = 1; i < monthsDisplay; i++) {
        idx = (idx + 1) % MONTHS_SHORT.length;
        options.push(MONTHS_SHORT[idx]);
    }
    return options;
}


function updateMonthDropdowns(monthsDisplayOverride) {
    let displayCount = monthsDisplayOverride || DEFAULT_MONTHS_DISPLAY;
    const initialMonth = getInitialMonth();
    const monthOptions = getMonthOptions(initialMonth, displayCount);
    document.querySelectorAll('select.month-dropdown').forEach(function(select) {
        const currentValue = select.value;
        select.innerHTML = '';
        monthOptions.forEach(function(month) {
            const option = document.createElement('option');
            option.value = month;
            option.textContent = month;
            if (month === currentValue) option.selected = true;
            select.appendChild(option);
        });
    });
}





function updatePaydf() {
    const optionsForm = document.getElementById('options-form');
    const settingsForm = document.getElementById('settings-form');
    const formData = new FormData(optionsForm);
    const monthsDropdown = settingsForm.querySelector('[name="months_display"]');
    formData.append('months_display', monthsDropdown.value);

    fetch('/update_paydf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(html => {
        document.getElementById('paydf').innerHTML = html;
        attachPaydfEventListeners();
    });
}


function highlight_changes() {
    var checkbox = document.getElementById('highlight-changes-checkbox');
    var checked = checkbox.checked;
    var table = document.getElementById('paydf-table');
    var rows = table.getElementsByTagName('tr');

    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName('td');

        //skip spacer rows
        if (cells.length < 2) continue;

        // get row header (first cell)
        var rowHeader = cells[0].textContent.trim();

        //start from col 3 (index 2), skip row header and first month
        for (var j = 2; j < cells.length; j++) {
            var cell = cells[j];
            var prevCell = cells[j - 1];

            if (
                checked &&
                cell.textContent.trim() !== prevCell.textContent.trim() &&
                !(rowHeader === "Difference" && cell.textContent.trim() === "$0.00")
            ) {
                cell.style.backgroundColor = '#b9f755';
            } else {
                cell.style.backgroundColor = '';
            }
        }
    }
}


function show_all_variables() {
    var checkbox = document.getElementById('show-all-variables-checkbox');
    var checked = checkbox.checked;
    var rows = document.getElementsByClassName('paydf-variable-row');

    for (var row of rows) {
        if (checked) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    }
}


function show_all_options() {
    var checkbox = document.getElementById('show-all-options-checkbox');
    var checked = checkbox.checked;
    var rows = document.getElementsByClassName('options-standard-row');

    for (var row of rows) {
        if (checked) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    }
}



// export paydf
async function downloadFile() {
    const filetype = document.getElementById('export-dropdown').value;

    const formData = new FormData();
    formData.append('filetype', filetype);

    const response = await fetch('/export', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;

    a.download = filetype === 'csv' ? 'payles.csv' : 'payles.xlsx';

    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
}


//les image tooltip
function showTooltip(evt, text) {
    const tooltip = document.getElementById('tooltip');
    tooltip.innerText = text;
    tooltip.style.left = (evt.pageX + 10) + 'px';
    tooltip.style.top = (evt.pageY + 10) + 'px';
    tooltip.style.display = 'block';
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    tooltip.style.display = 'none';
}





//delegated event listeners for dynamic paydf controls
document.addEventListener('click', function(e) {
    if (e.target && e.target.id === 'update-les-button') {
        e.preventDefault();
        updatePaydf();
    }
});

document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'months-dropdown') {
        e.preventDefault();
        updatePaydf();
        updateMonthDropdowns(parseInt(e.target.value));
    }
    if (e.target && e.target.id === 'highlight-changes-checkbox') {
        highlight_changes();
    }
    if (e.target && e.target.id === 'show-all-variables-checkbox') {
        show_all_variables();
    }
    if (e.target && e.target.id === 'show-all-options-checkbox') {
        show_all_options();
    }
});

document.addEventListener('mousemove', function(e) {
    if (e.target && e.target.classList.contains('rect-highlight')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }
});

document.addEventListener('mouseleave', function(e) {
    if (e.target && e.target.classList.contains('rect-highlight')) {
        hideTooltip();
    }
}, true);
