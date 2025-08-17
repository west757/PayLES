// page load event listener
document.addEventListener('DOMContentLoaded', function() {
    initConfigVars();
});


// htmx after swap event listener
document.body.addEventListener('htmx:afterSwap', function(evt) {
    enableAllInputs();

    if (document.getElementById('paydf-group')) {
        stripeTable('options-table');
        stripeTable('settings-table');
        attachTspBaseListeners();
    }

    if (document.getElementById('paydf-table')) {
        stripeTable('paydf-table');
    }

});


// htmx response error event listener
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


// attach home form listener
window.attachHomeFormListener = function() {
    const homeForm = document.getElementById('home-form');
    homeForm.addEventListener('submit', function(e) {
        disableAllInputs();
    });
};


// keydown event listener
document.addEventListener('keydown', function(e) {
    // close modals on escape key press
    if (e.key === 'Escape' || e.key === 'Esc') {
        document.querySelectorAll('.modal-state:checked').forEach(function(input) {
            input.checked = false;
        });
    }
});


// mouse move event listener
document.addEventListener('mousemove', function(e) {
    // show tooltips on mouse move over
    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }
});


// mouse leave event listener
document.addEventListener('mouseleave', function(e) {
    // hide tooltips on mouse leave
    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        hideTooltip();
    }
}, true);


// click event listeners
document.addEventListener('click', function(e) {
    // open modals when modal button for a row is clicked
    if (e.target.classList.contains('modal-button')) {
        const modalId = e.target.getAttribute('data-modal');

        if (modalId) {
            const modalCheckbox = document.getElementById(modalId);
            if (modalCheckbox) {
                modalCheckbox.checked = true;
            }
        }
    }

    if (e.target && e.target.id === 'update-les-button') {
        e.preventDefault();
        disableAllInputs();
        updatePaydf();
    }

    if (e.target && e.target.id === 'export-button') {
        e.preventDefault();
        exportPaydf();
    }
});


// change event listeners
document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'months-display-dropdown') {
        e.preventDefault();
        disableAllInputs();
        updatePaydf();
    }

    if (e.target && e.target.id === 'highlight-changes-checkbox') {
        highlight_changes();
    }

    if (e.target && e.target.id === 'show-all-variables-checkbox') {
        show_all_variables();
    }

    if (e.target && e.target.id === 'show-tsp-options-checkbox') {
        show_tsp_options();
    }
});
