// page load event listener
document.addEventListener('DOMContentLoaded', function() {
    initConfigVars();
});

// htmx response error event listener
document.body.addEventListener('htmx:responseError', function(evt) {
    try {
        const response = JSON.parse(evt.detail.xhr.responseText);
        if (response.message) {
            showToast(response.message);
        }
    } catch (e) {
        // not a JSON response, ignore
    }
});


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
    // open modals when modal button is clicked
    if (e.target.classList.contains('modal-button')) {
        const modalId = e.target.getAttribute('data-modal');
        if (modalId) {
            const modalCheckbox = document.getElementById(modalId);
            if (modalCheckbox) {
                modalCheckbox.checked = true;
            }
        }
    }


    // enter edit mode for clicked cell
    if (e.target.classList.contains('cell-button')) {
        let rowHeader = e.target.getAttribute('data-row');
        let colMonth = e.target.getAttribute('data-col');
        let fieldType = e.target.getAttribute('data-field');
        let value = getBudgetValue(rowHeader, colMonth);
        enterEditMode(e.target, rowHeader, colMonth, value, fieldType);
    }
    

    // export button
    if (e.target && e.target.id === 'export-button') {
        e.preventDefault();
        exportbudget();
    }
});


// change event listeners
document.addEventListener('change', function(e) {
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



// beforeinput event listeners
document.addEventListener('beforeinput', function(e) {
    // restricts decimal inpuit
    if (e.target.classList.contains('input-decimal')) {
        const input = e.target;
        const value = input.value;
        const selectionStart = input.selectionStart;
        const selectionEnd = input.selectionEnd;
        const newChar = e.data || '';
        let newValue;

        // simulate the new value if this input is allowed
        if (e.inputType === 'insertText' || e.inputType === 'insertFromPaste') {
            newValue = value.slice(0, selectionStart) + newChar + value.slice(selectionEnd);
        } else if (e.inputType === 'deleteContentBackward') {
            newValue = value.slice(0, selectionStart - 1) + value.slice(selectionEnd);
        } else if (e.inputType === 'deleteContentForward') {
            newValue = value.slice(0, selectionStart) + value.slice(selectionEnd + 1);
        } else {
            newValue = value;
        }

        if (newValue.length > 7) {
            e.preventDefault();
            return;
        }

        if (!/^\d{0,4}(\.\d{0,2})?$/.test(newValue)) {
            e.preventDefault();
            return;
        }
    }
});




document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.target && evt.target.id === 'content') {
        const budget = document.getElementById('budget');
        const settingsContainer = document.getElementById('settings-container');
        const settings = document.getElementById('settings');

        if (!budget || !settingsContainer || !settings) return;

        // Set settings-container height to match budget
        function syncHeight() {
            settingsContainer.style.height = budget.offsetHeight + 'px';
        }
        syncHeight();
        window.addEventListener('resize', syncHeight);

        // Smart sticky logic
        window.addEventListener('scroll', function() {
            const containerRect = settingsContainer.getBoundingClientRect();
            const settingsHeight = settings.offsetHeight;

            if (containerRect.top > 2 * 16) { // 2rem = 32px
                // At the top: stick to top of container
                settings.style.position = 'absolute';
                settings.style.top = '0px';
            } else if (containerRect.bottom < settingsHeight + 2 * 16) {
                // At the bottom: stick to bottom of container
                settings.style.position = 'absolute';
                settings.style.top = (containerRect.height - settingsHeight) + 'px';
            } else {
                // In between: fixed to top of viewport with 2rem buffer
                settings.style.position = 'fixed';
                settings.style.top = '2rem';
            }
        });
    }

    const budgetDataScript = document.getElementById('budget-data');
    if (budgetDataScript) {
        window.BUDGET_DATA = JSON.parse(budgetDataScript.textContent);
    }
});