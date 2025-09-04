//stores state of removing row, used for confirmation timeout
let removeRowConfirm = {};


document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('home')) {
        // capture and parse config data
        const configData = JSON.parse(document.getElementById('config-data').textContent);
        window.CONFIG = Object.assign(window.CONFIG || {}, configData);

        attachHomeListeners();
        attachDragAndDropListeners();
    }
});


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
    toggleRows('var');
    toggleRows('tsp');
    toggleRows('ytd');
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
    if (e.target && e.target.classList && e.target.classList.contains('tooltip')) {
        let tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
        } else {
            // Dynamic tooltips for budget cells
            const row = e.target.getAttribute('data-row');
            const value = e.target.getAttribute('data-value');
            let tooltip = '';

            if (row === 'Months in Service' && value) {
                const months = parseInt(value, 10);
                const years = Math.floor(months / 12);
                const remMonths = months % 12;
                tooltip = `${years} year${years !== 1 ? 's' : ''} ${remMonths} month${remMonths !== 1 ? 's' : ''}`;
            } 
            //else if (row === 'Grade' && value) {
            //    tooltip = window.CONFIG.GRADES_RANKS[value] || '';
            //} 
            else if (row === 'Home of Record' && value) {
                const record = window.CONFIG.HOME_OF_RECORDS.find(hor => hor.abbr === value);
                if (record) {
                    tooltip = record.home_of_record;
                }
                console.log("home of record: ", tooltip);
            } 
            else if (row === 'Military Housing Area' && value) {
                const record = window.CONFIG.MHA_ZIP_CODES.find(mhaObj => mhaObj.mha === value);
                if (record) {
                    tooltip = record.mha_name;
                }
            }

            if (tooltip) showTooltip(e, tooltip);
        }
    }
});


document.addEventListener('mouseleave', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('tooltip')) {
        hideTooltip();
    }
}, true);


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
            }, 2500); // reset confirmation after 2.5s
        } else {
            removeRowConfirm[header] = false;
            hideTooltip();
            htmx.ajax('POST', '/route_remove_row', {
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

    // open instructions modal
    if (e.target && e.target.id === 'button-instructions') {
        const instructionsModalCheckbox = document.getElementById('instructions');
        instructionsModalCheckbox.checked = true;
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

    if (e.target && e.target.id === 'checkbox-highlight') {
        highlightChanges();
    }

    if (e.target && e.target.id === 'checkbox-var') {
        toggleRows('var');
    }

    if (e.target && e.target.id === 'checkbox-tsp') {
        toggleRows('tsp');
    }

    if (e.target && e.target.id === 'checkbox-ytd') {
        toggleRows('ytd');
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