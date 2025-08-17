// initialize config variables
function initConfigVars() {
    const configDiv = document.getElementById('config-data');
    if (configDiv) {
        window.DEFAULT_MONTHS_DISPLAY = parseInt(configDiv.dataset.defaultMonthsDisplay);
        window.MAX_CUSTOM_ROWS = parseInt(configDiv.dataset.maxCustomRows);
        window.RESERVED_HEADERS = JSON.parse(configDiv.dataset.reservedHeaders);
    }
}


// open modals when modal button for a row is clicked
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-button')) {
        const modalId = e.target.getAttribute('data-modal');

        if (modalId) {
            const modalCheckbox = document.getElementById(modalId);
            if (modalCheckbox) {
                modalCheckbox.checked = true;
            }
        }
    }
});


// close modals on escape key press
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' || e.key === 'Esc') {
        document.querySelectorAll('.modal-state:checked').forEach(function(input) {
            input.checked = false;
        });
    }
});


// show tooltips on mouse move over
document.addEventListener('mousemove', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }
});


// hide tooltips on mouse leave
document.addEventListener('mouseleave', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        hideTooltip();
    }
}, true);







document.addEventListener('DOMContentLoaded', function() {
    initConfigVars();

    if (document.getElementById('home-form')) {
        attachHomeFormListener();
    }
});


document.body.addEventListener('htmx:afterSwap', function(evt) {
    enableAllInputs();

    if (document.getElementById('home-form')) {
        attachHomeFormListener();
    }

    if (document.getElementById('paydf-group')) {
        stripeTable('options-table');
        stripeTable('settings-table');
        attachTspBaseListeners();
    }

    if (document.getElementById('paydf-table')) {
        stripeTable('paydf-table');
    }

});


// show toast messages after htmx response Error
document.body.addEventListener('htmx:responseError', function(evt) {
    enableAllInputs();
    try {
        const response = JSON.parse(evt.detail.xhr.responseText);
        if (response.message) {
            showToast(response.message);
        }
    } catch (e) {
        // not a JSON response, ignore
    }
});



function attachHomeFormListener() {
    const homeForm = document.getElementById('home-form');
    homeForm.addEventListener('submit', function(e) {
        disableAllInputs();
    });
}



