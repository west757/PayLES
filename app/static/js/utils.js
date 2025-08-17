// =========================
// drag and drop file upload
// =========================

(function() {
    var dropContainer = document.getElementById("home-drop");
    var fileInput = document.getElementById("home-input");
    var form = dropContainer.closest("form");

    if (!dropContainer || !fileInput || !form) return;

    //prevent default drag behaviors
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






function enableAllInputs() {
    document.querySelectorAll('button, input, select, textarea').forEach(function(el) {
        el.disabled = false;
    });
}

function disableAllInputs() {
    document.querySelectorAll('button, input, select, textarea').forEach(function(el) {
        el.disabled = true;
    });
}


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
// export paydf
// =========================

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
// tooltip functionality
// =========================

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




document.addEventListener('click', function(e) {
    if (e.target && e.target.id === 'export-button') {
        e.preventDefault();
        exportPaydf();
    }
});