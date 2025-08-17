function initConfigVars() {
    const configDiv = document.getElementById('config-data');
    if (configDiv) {
        window.RESERVED_HEADERS = JSON.parse(configDiv.dataset.reservedHeaders);
        window.DEFAULT_MONTHS_DISPLAY = parseInt(configDiv.dataset.defaultMonthsDisplay);
        window.MAX_CUSTOM_ROWS = parseInt(configDiv.dataset.maxCustomRows);
    }
}


// =========================
// delegate event listeners
// =========================

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



document.addEventListener('mousemove', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }
});

document.addEventListener('mouseleave', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        hideTooltip();
    }
}, true);


// close modals on Escape key press
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' || e.key === 'Esc') {
        document.querySelectorAll('.modal-state:checked').forEach(function(input) {
            input.checked = false;
        });
    }
});


// disable buttons on form submission to prevent multiple submissions
document.addEventListener('DOMContentLoaded', function() {
    initConfigVars();
    attachTspBaseListeners();

    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function() {
            form.querySelectorAll('button, input[type="submit"]').forEach(function(btn) {
                btn.disabled = true;
            });
        });
    });
});




document.body.addEventListener('htmx:afterSwap', function(evt) {
    initConfigVars();
    stripeTable('paydf-table');
    stripeTable('options-table');
    stripeTable('settings-table');
    attachTspBaseListeners();
    updateTspInputs();
});


document.body.addEventListener('htmx:beforeRequest', function(evt) {
    if (evt.target && evt.target.id === 'home-form') {
        evt.target.querySelectorAll('button, input[type="submit"]').forEach(function(btn) {
            btn.disabled = true;
        });
    }
});
