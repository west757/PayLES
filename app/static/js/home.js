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

    // Show default tab on load
    const defaultTab = document.querySelector('.tab-button.active');
    if (defaultTab) {
        const tabId = 'tab-' + defaultTab.getAttribute('data-tab');
        const tabContent = document.getElementById(tabId);
        if (tabContent) {
            tabContent.classList.add('active');
        }
    }

    // Zip code validation
    const zipInput = document.getElementById('form-submit-custom')?.querySelector('input[name="zip_code"]');
    if (zipInput) {
        zipInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 5);
        });
    }

    // Dependents validation
    const depInput = document.getElementById('form-submit-custom')?.querySelector('input[name="dependents"]');
    if (depInput) {
        depInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 1);
        });
    }

    // Disable inputs on any home form submit
    document.querySelectorAll('#form-submit-single, #form-submit-joint, #form-submit-custom, #form-submit-example').forEach(form => {
        form.addEventListener('submit', function(e) {
            disableInputs();
        });
    });
}

// Initial load
document.addEventListener('DOMContentLoaded', attachHomeListeners);

// htmx swap: re-attach listeners when home.html is loaded/swapped in
document.body.addEventListener('htmx:afterSwap', function(evt) {
    // Check if the swap target contains the home content
    if (document.getElementById('home')) {
        attachHomeListeners();
    }
});


(function() {
    const dropContainer = document.getElementById("submit-single-drop");
    const fileInput = document.getElementById("submit-single-input");

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
})();