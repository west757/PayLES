// stores scroll position of budget, used to restore after htmx swap
let budgetScrollTop = 0;
//stores state of removing row, used for confirmation timeout
let removeRowConfirm = {};


document.body.addEventListener('htmx:responseError', function(evt) {
    const xhr = evt.detail.xhr;
    const contentType = xhr.getResponseHeader("Content-Type");

    // if JSON, show toast/modal
    if (contentType && contentType.includes("application/json")) {
        try {
            const response = JSON.parse(xhr.responseText);
            if (response.message) {
                showToast(response.message); // or showModal(response.message);
            }
        } catch (e) {
            // not a valid JSON, ignore
        }
    } else {
        // HTML error page, swap into body
        document.body.innerHTML = xhr.responseText;
    }
    enableInputs();
});


document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('home')) {
        getConfigData();

        attachDragAndDropListeners();
        attachHomeListeners();
    }
});


// save scroll position before any htmx request that will update the budget
document.body.addEventListener('htmx:beforeRequest', function(evt) {
    // only save if the budget is present
    const budgetContainer = document.getElementById('budget-container');
    if (budgetContainer) {
        budgetScrollTop = budgetContainer.scrollTop;
    }
});


// htmx after swap event listener, runs every time the budget is loaded
document.body.addEventListener('htmx:afterSwap', function(evt) {
    getConfigData();

    //only runs the first time the budget is loaded
    if (evt.target && evt.target.id === 'content') {
        //window.addEventListener('beforeunload', budgetUnloadPrompt);
        attachInjectModalListeners();
        attachAccountModalListeners();
    }

    highlightChanges();
    toggleRows('variables');
    toggleRows('tsp-rates');
    enableInputs();
    disableDrillsButtons();
    disableTSPRateButtons();
    updateRecommendations();

    const budgetContainer = document.getElementById('budget-container');
    if (budgetContainer && typeof budgetScrollTop === 'number') {
        budgetContainer.scrollTop = budgetScrollTop;
    }
});


document.addEventListener('mousemove', function(e) {
    // show tooltip on hover
    if (e.target && e.target.classList && e.target.classList.contains('tooltip')) {
        let tooltipText = e.target.getAttribute('data-tooltip');
        if (tooltipText) {
            showTooltip(e, tooltipText);
            return;
        }

        // only build tooltip if tooltipText is not present
        const row = e.target.getAttribute('data-row');
        const value = e.target.getAttribute('data-value');
        const month = e.target.getAttribute('data-month');
        let tooltip = '';

        if (row === 'Months in Service' && value) {
            const months = parseInt(value, 10) % 12;
            const years = Math.floor(parseInt(value, 10) / 12);
            tooltip = `${years} year${years !== 1 ? 's' : ''} ${months} month${months !== 1 ? 's' : ''}`;
        } 
        else if (row === 'Branch' && value) {
            tooltip = getBudgetValue('Branch Long', month);
        }
        else if (row === 'Component' && value) {
            tooltip = getBudgetValue('Component Long', month);
        }
        else if (row === 'Grade' && value) {
            tooltip = getBudgetValue('Rank Long', month);
        }
        else if (row === 'Military Housing Area' && value) {
            tooltip = getBudgetValue('Military Housing Area Long', month);
        }
        else if (row === 'OCONUS Locality Code' && value) {
            tooltip = getBudgetValue('OCONUS Locality Code Long', month);
        }
        else if (row === 'Home of Record' && value) {
            tooltip = getBudgetValue('Home of Record Long', month);
        }

        if (tooltip) showTooltip(e, tooltip);
    }
});


document.addEventListener('mouseleave', function(e) {
    // hide tooltip when mouse leaves element
    if (e.target && e.target.classList && e.target.classList.contains('tooltip')) {
        hideTooltip();
    }
}, true);


document.addEventListener('click', function(e) {
    // open dynamic modals
    if (e.target.classList.contains('modal-button')) {
        const modalId = e.target.getAttribute('data-modal');
        if (modalId) {
            const modalCheckbox = document.getElementById(modalId);
            if (modalCheckbox) {
                modalCheckbox.checked = true;
            }
        }
    }

    if (e.target && e.target.id === 'button-guide-budget') {
        const guideBudgetModalCheckbox = document.getElementById('modal-guide-budget');
        guideBudgetModalCheckbox.checked = true;
    }

    if (e.target && e.target.id === 'button-inject') {
        const injectModalCheckbox = document.getElementById('modal-inject');
        injectModalCheckbox.checked = true;
        resetInjectModal();
    }

    if (e.target && e.target.id === 'button-account-bank') {
        const accountBankModalCheckbox = document.getElementById('modal-account-bank');
        accountBankModalCheckbox.checked = true;
        //resetAccountModal();
    }

    if (e.target && e.target.id === 'button-verification') {
        const verificationModalCheckbox = document.getElementById('modal-verification');
        verificationModalCheckbox.checked = true;
    }

    if (e.target && e.target.id === 'button-recommendations') {
        const recommendationsModalCheckbox = document.getElementById('modal-recommendations');
        recommendationsModalCheckbox.checked = true;
    }

    if (e.target && e.target.id === 'button-guide-tsp') {
        const guideTspModalCheckbox = document.getElementById('modal-guide-tsp');
        guideTspModalCheckbox.checked = true;
    }

    if (e.target && e.target.id === 'button-account-tsp') {
        const accountTspModalCheckbox = document.getElementById('modal-account-tsp');
        accountTspModalCheckbox.checked = true;
        //resetAccountModal();
    }

    if (e.target && e.target.id === 'button-tsp-analysis') {
        const tspAnalysisModalCheckbox = document.getElementById('modal-tsp-analysis');
        tspAnalysisModalCheckbox.checked = true;
    }

    if (e.target.classList.contains('modal-close')) {
        document.querySelectorAll('.modal-state:checked').forEach(function(input) {
            input.checked = false;
        });
    }

    // remove row button click
    if (e.target.classList.contains('remove-row-button')) {
        let header = e.target.getAttribute('data-row');

        // sets a confirmation state for 2.5 seconds to prevent accidental row removal
        if (!removeRowConfirm[header]) {
            e.target.setAttribute('data-tooltip', 'Please click again to remove row');
            showTooltip(e, 'Please click again to remove row');
            removeRowConfirm[header] = true;
            setTimeout(() => {
                removeRowConfirm[header] = false;
                e.target.setAttribute('data-tooltip', 'Remove Row');
            }, 2500); // reset confirmation after 2.5s
        } else {
            // remove row confirmed, sends htmx request
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
        let header = e.target.getAttribute('data-row');
        let month = e.target.getAttribute('data-month');
        let fieldType = e.target.getAttribute('data-field');
        let value = getBudgetValue(header, month);
        enterEditMode(e.target, header, month, value, fieldType);
    }

    // export budget button
    if (e.target && e.target.id === 'button-export-budget') {
        e.preventDefault();
        exportTable('budget');
    }

    // export tsp button
    if (e.target && e.target.id === 'button-export-tsp') {
        e.preventDefault();
        exportTable('tsp');
    }
});


document.addEventListener('change', function(e) {
    // setting function calls on dropdown or checkbox change
    if (e.target && e.target.id === 'months-num-dropdown') {
        disableInputs();
    }

    if (e.target && e.target.id === 'checkbox-highlight-budget') {
        highlightChanges('budget');
    }

    if (e.target && e.target.id === 'checkbox-variables') {
        toggleRows('variables');
    }
    
    if (e.target && e.target.id === 'checkbox-highlight-tsp') {
        highlightChanges('tsp');
    }

    if (e.target && e.target.id === 'checkbox-tsp-rates') {
        toggleRows('tsp-rates');
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
