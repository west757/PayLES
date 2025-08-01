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




fetch('/update_paydf', {
    method: 'POST',
    body: formData
})
.then(response => response.text())
.then(html => {
    document.getElementById('paydf-table').innerHTML = html;
});