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



function show_all_variables() {
    // Get the checkbox element
    var checkbox = document.getElementById('show-all-variables-checkbox');
    // Determine if the checkbox is checked
    var isChecked = checkbox.checked;
    // Get all rows with the class 'paydf-variable-row'
    var variableRows = document.getElementsByClassName('paydf-variable-row');
    // Loop through each variable row
    for (var row of variableRows) {
        if (isChecked) {
            // If checked, show the row as a table row
            row.style.display = 'table-row';
        } else {
            // If not checked, hide the row
            row.style.display = 'none';
        }
    }
}
