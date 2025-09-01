//stores state of removing row, used for confirmation timeout
let removeRowConfirm = {};


// htmx after swap event listener, runs every time the budget is loaded
document.body.addEventListener('htmx:afterSwap', function(evt) {
    //only runs the first time the budget is loaded
    if (evt.target && evt.target.id === 'content') {
        //window.addEventListener('beforeunload', budgetUnloadPrompt);
        attachInjectModalListeners();
    }

    // capture and parse config data
    const configData = JSON.parse(document.getElementById('config-data').textContent);
    window.CONFIG = Object.assign(window.CONFIG || {}, configData);

    highlightChanges();
    showAllVariables();
    showTSPOptions();
    showYTDRows();
    enableInputs();
    disableTSPRateButtons();
});


document.body.addEventListener('htmx:responseError', function(evt) {
    // show toasts on htmx swap errors
    try {
        const response = JSON.parse(evt.detail.xhr.responseText);
        if (response.message) {
            showToast(response.message);
        }
    } catch (e) {
        // not a JSON response, ignore
    }
    enableInputs();
});


document.addEventListener('mousemove', function(e) {
    // show question mark tooltips
    if (e.target && e.target.classList && e.target.classList.contains('question-tooltip')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }

    //show row modal button tooltips
    if (e.target && e.target.classList && e.target.classList.contains('modal-button')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }

    // show remove row button tooltips
    if (e.target && e.target.classList && e.target.classList.contains('remove-row-button')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }

    // show editing button tooltips
    if (e.target && e.target.classList && e.target.classList.contains('editing-button')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }

    // show LES rectangle tooltips
    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }
});


document.addEventListener('mouseleave', function(e) {
    // hide all tooltips on mouse leave
    if (e.target && e.target.classList && e.target.classList.contains('modal-button')) {
        hideTooltip();
    }

    if (e.target && e.target.classList && e.target.classList.contains('remove-row-button')) {
        hideTooltip();
    }

    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        hideTooltip();
    }

    if (e.target && e.target.classList && e.target.classList.contains('editing-button')) {
        hideTooltip();
    }

    if (e.target && e.target.classList && e.target.classList.contains('question-tooltip')) {
        hideTooltip();
    }
}, true);


document.addEventListener('click', function(e) {
    hideTooltip();
    
    // open modals
    if (e.target.classList.contains('modal-button')) {
        const modalId = e.target.getAttribute('data-modal');
        if (modalId) {
            const modalCheckbox = document.getElementById(modalId);
            if (modalCheckbox) {
                modalCheckbox.checked = true;
            }
        }
    }

    // close modals
    if (e.target.classList.contains('modal-close')) {
        document.querySelectorAll('.modal-state:checked').forEach(function(input) {
            input.checked = false;
        });
    }

    // remove row
    if (e.target.classList.contains('remove-row-button')) {
        let header = e.target.getAttribute('data-row');

        if (!removeRowConfirm[header]) {
            e.target.setAttribute('data-tooltip', 'Please click again to remove row');
            showTooltip(e, 'Please click again to remove row');
            removeRowConfirm[header] = true;
            setTimeout(() => {
                removeRowConfirm[header] = false;
                e.target.setAttribute('data-tooltip', 'Remove Row');
            }, 2500); // reset confirmation after 2.5s
        } else {
            removeRowConfirm[header] = false;
            hideTooltip();
            htmx.ajax('POST', '/remove_row', {
                target: '#budget',
                swap: 'innerHTML',
                values: { header: header }
            });
            showToast("Row " + header + " removed");
        }
        e.stopPropagation();
    }

    // enter edit mode for cell
    if (e.target.classList.contains('cell-button')) {
        let rowHeader = e.target.getAttribute('data-row');
        let month = e.target.getAttribute('data-month');
        let fieldType = e.target.getAttribute('data-field');
        let value = getBudgetValue(rowHeader, month);
        enterEditMode(e.target, rowHeader, month, value, fieldType);
    }

    // open inject modal
    if (e.target && e.target.id === 'button-inject') {
        const injectModalCheckbox = document.getElementById('inject');
        injectModalCheckbox.checked = true;
        resetInjectModal();
    }

    // open account modal
    if (e.target && e.target.id === 'button-account') {
        const accountModalCheckbox = document.getElementById('account');
        accountModalCheckbox.checked = true;
    }

    // open recommendation modal
    if (e.target && e.target.id === 'button-recs') {
        const recsModalCheckbox = document.getElementById('recs');
        recsModalCheckbox.checked = true;
    }

    // export button
    if (e.target && e.target.id === 'button-export') {
        e.preventDefault();
        exportBudget();
    }
});


document.addEventListener('change', function(e) {
    // setting function calls on dropdown or checkbox change
    if (e.target && e.target.id === 'months-num-dropdown') {
        disableInputs();
    }

    if (e.target && e.target.id === 'highlight-changes-checkbox') {
        highlightChanges();
    }

    if (e.target && e.target.id === 'show-all-variables-checkbox') {
        showAllVariables();
    }

    if (e.target && e.target.id === 'show-tsp-options-checkbox') {
        showTSPOptions();
    }

    if (e.target && e.target.id === 'show-ytd-rows-checkbox') {
        showYTDRows();
    }
});


document.addEventListener('keydown', function(e) {
    // close modals on escape key press
    if (e.key === 'Escape' || e.key === 'Esc') {
        document.querySelectorAll('.modal-state:checked').forEach(function(input) {
            input.checked = false;
        });
    }
});