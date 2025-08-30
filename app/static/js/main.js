// attach home form listener
window.attachHomeFormListener = function() {
    const homeForm = document.getElementById('home-form');
    homeForm.addEventListener('submit', function(e) {
        disableInputs();
    });
};


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
    enableInputs();
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
    if (e.target && e.target.classList && e.target.classList.contains('modal-button')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }

    if (e.target && e.target.classList && e.target.classList.contains('remove-row-button')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }

    if (e.target && e.target.classList && e.target.classList.contains('rect-highlight')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }

    if (e.target && e.target.classList && e.target.classList.contains('editing-button')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }

    if (e.target && e.target.classList && e.target.classList.contains('question-tooltip')) {
        const tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        }
    }
});


// mouse leave event listener
document.addEventListener('mouseleave', function(e) {
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


let removeRowConfirm = {};
// click event listeners
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
            }, 2500); // Reset after 2.5s
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

    // open recs modal
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


// change event listeners
document.addEventListener('change', function(e) {
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


// htmx after swap event listener
document.body.addEventListener('htmx:afterSwap', function(evt) {
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