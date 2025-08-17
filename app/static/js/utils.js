// initialize config variables
function initConfigVars() {
    const configDiv = document.getElementById('config-data');
    if (configDiv) {
        window.DEFAULT_MONTHS_DISPLAY = parseInt(configDiv.dataset.defaultMonthsDisplay);
        window.MAX_CUSTOM_ROWS = parseInt(configDiv.dataset.maxCustomRows);
        window.RESERVED_HEADERS = JSON.parse(configDiv.dataset.reservedHeaders);
    }
}


// enable all inputs
function enableAllInputs() {
    document.querySelectorAll('button, input, select, textarea').forEach(function(el) {
        el.disabled = false;
    });
}


// disable all inputs
function disableAllInputs() {
    document.querySelectorAll('button, input, select, textarea').forEach(function(el) {
        el.disabled = true;
    });
}


// show tooltip
function showTooltip(evt, text) {
    const tooltip = document.getElementById('tooltip');
    tooltip.innerText = text;
    tooltip.style.left = (evt.pageX + 10) + 'px';
    tooltip.style.top = (evt.pageY + 10) + 'px';
    tooltip.style.display = 'block';
}


// hide tooltip
function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    tooltip.style.display = 'none';
}


// show toast messages
function showToast(message, duration = 6500) {
    const MAX_TOASTS = 3;
    const container = document.getElementById('toast-container');

    while (container.children.length >= MAX_TOASTS) {
        container.removeChild(container.firstChild);
    }

    let toast = document.createElement('div');
    toast.className = 'toast shadow';
    toast.textContent = message;

    let closeBtn = document.createElement('span');
    closeBtn.textContent = '✖';
    closeBtn.className = 'toast-close';
    closeBtn.onclick = () => toast.remove();
    toast.appendChild(closeBtn);

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, duration);
}


// stripe table rows
function stripeTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    let rowIndex = 0;
    table.querySelectorAll('tbody').forEach(function(tbody) {
        tbody.querySelectorAll('tr').forEach(function(tr) {
            if (rowIndex % 2 === 1) {
                tr.classList.add('even-row');
            } else {
                tr.classList.remove('even-row');
            }
            rowIndex++;
        });
    });
}


// export paydf
function exportPaydf() {
    var table = document.getElementById('paydf-table');
    var filetype = document.getElementById('export-dropdown').value;
    var filename = filetype === 'csv' ? 'payles.csv' : 'payles.xlsx';

    var workbook = XLSX.utils.table_to_book(table, {sheet: "PayDF", raw: true});
    if (filetype === 'csv') {
        XLSX.writeFile(workbook, filename, {bookType: 'csv'});
    } else {
        XLSX.writeFile(workbook, filename);
    }
}





// =========================
// update buttons
// =========================

function updateButtonStates() {
    const buttonIds = [
        'update-les-button',
        'add-entitlement-button',
        'add-deduction-button',
        'export-button'
    ];

    const disable = editingIndex !== null;
    buttonIds.forEach(function(id) {
        const btn = document.getElementById(id);
        if (btn) {
            btn.disabled = disable;
        }
    });
}



// =========================
// drag and drop file upload
// =========================

(function() {
    var dropContainer = document.getElementById("home-drop");
    var fileInput = document.getElementById("home-input");
    var form = dropContainer.closest("form");

    if (!dropContainer || !fileInput || !form) return;

    // prevent default drag behaviors
    ["dragenter", "dragover", "dragleave", "drop"].forEach(function(eventName) {
        dropContainer.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    dropContainer.addEventListener("dragenter", function() {
        dropContainer.classList.add("drag-active");
    });

    dropContainer.addEventListener("dragleave", function(e) {
        if (e.target === dropContainer) {
            dropContainer.classList.remove("drag-active");
        }
    });

    dropContainer.addEventListener("drop", function(e) {
        dropContainer.classList.remove("drag-active");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
        }
    });
})();