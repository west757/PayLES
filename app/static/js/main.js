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
}, true);


let removeRowConfirm = {};
// click event listeners
document.addEventListener('click', function(e) {
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

    // open inject modal
    if (e.target && e.target.id === 'button-inject') {
        const injectModalCheckbox = document.getElementById('inject');
        injectModalCheckbox.checked = true;
        resetInjectModal();
    }

    // enter edit mode for cell
    if (e.target.classList.contains('cell-button')) {
        let rowHeader = e.target.getAttribute('data-row');
        let colMonth = e.target.getAttribute('data-col');
        let fieldType = e.target.getAttribute('data-field');
        let value = getBudgetValue(rowHeader, colMonth);
        enterEditMode(e.target, rowHeader, colMonth, value, fieldType);
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
        syncSettingsContainerHeight();
    }

    if (e.target && e.target.id === 'show-tsp-options-checkbox') {
        showTSPOptions();
        syncSettingsContainerHeight();
    }
});


// htmx after swap event listener
document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.target && evt.target.id === 'content') {
        //window.addEventListener('beforeunload', budgetUnloadPrompt);
        attachInjectModalListeners();

        const budget = document.getElementById('budget');
        const settingsContainer = document.getElementById('settings-container');
        const settings = document.getElementById('settings');
        syncSettingsContainerHeight();

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


        // inject custom header event listener
        const customHeaderInput = document.getElementById('inject-custom-header');
        if (customHeaderInput) {
            customHeaderInput.addEventListener('input', setInputRestriction('text', 20));
        }


        // inject template and custom value event listeners
        ['inject-template-value', 'inject-custom-value'].forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', setInputRestriction('money'));
            }
        });
    }

    // capture and parse config data
    const configData = JSON.parse(document.getElementById('config-data').textContent);
    window.CONFIG = Object.assign(window.CONFIG || {}, configData);

    highlightChanges();
    showAllVariables();
    showTSPOptions();
    enableInputs();
    disableTSPRateButtons();
});