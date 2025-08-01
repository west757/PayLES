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




function updatePaydf() {
    console.log('updatePaydf called');
    const optionsForm = document.getElementById('options-form');
    const settingsForm = document.getElementById('settings-form');
    if (!optionsForm) {
        console.log('No #options-form found');
        return;
    }
    if (!settingsForm) {
        console.log('No #settings-form found');
        return;
    }
    const formData = new FormData(optionsForm);
    const monthsDropdown = settingsForm.querySelector('[name="months_display"]');
    if (!monthsDropdown) {
        console.log('No months_display dropdown found in #settings-form');
        return;
    }
    formData.append('months_display', monthsDropdown.value);

    fetch('/update_paydf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(html => {
        console.log('Received response from /update_paydf');
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
    try {
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
    } catch (error) {
        console.error('Error during file download:', error);
    }
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
        console.log('Delegated: Update LES button clicked');
        updatePaydf();
    }
});

document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'months-dropdown') {
        e.preventDefault();
        console.log('Delegated: Months dropdown changed');
        updatePaydf();
    }
    if (e.target && e.target.id === 'highlight-changes-checkbox') {
        console.log('Delegated: Highlight changes toggled');
        highlight_changes();
    }
    if (e.target && e.target.id === 'show-all-variables-checkbox') {
        console.log('Delegated: Show all variables toggled');
        show_all_variables();
    }
    if (e.target && e.target.id === 'show-all-options-checkbox') {
        console.log('Delegated: Show all options toggled');
        show_all_options();
    }
});

document.addEventListener('mousemove', function(e) {
    if (e.target && e.target.classList.contains('rect-highlight')) {
        // Get tooltip text from data-tooltip attribute
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
