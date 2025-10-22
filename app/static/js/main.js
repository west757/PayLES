// stores scroll position of pay and tsp, used to restore after htmx swap
let payScrollTop = 0;
let tspScrollTop = 0;

//stores state of removing row, used for confirmation timeout
let removeRowConfirm = {};


document.body.addEventListener('htmx:responseError', function(evt) {
    const xhr = evt.detail.xhr;
    const contentType = xhr.getResponseHeader("Content-Type");

    // if JSON error show toast, else show error page
    if (contentType && contentType.includes("application/json")) {
        try {
            const response = JSON.parse(xhr.responseText);
            if (response.message) {
                showToast(response.message);
            }
        } catch (e) {
            console.warn("Failed to parse JSON error response:", e);
        }
    } else {
        document.body.innerHTML = xhr.responseText;
    }
    enableInputs();
});


// initial setup when home page is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('home')) {
        getConfigData();
        attachDragAndDropListeners();
        attachHomeListeners();
    }
});


// save scroll position before any htmx request that will update budgets
document.body.addEventListener('htmx:beforeRequest', function(evt) {
    payScrollTop = document.getElementById('budget-pay') ? document.getElementById('budget-pay').scrollTop : 0;
    tspScrollTop = document.getElementById('budget-tsp') ? document.getElementById('budget-tsp').scrollTop : 0;
});


// htmx after swap event listener, runs every time the pay is loaded
document.body.addEventListener('htmx:afterSwap', function(evt) {
    getConfigData();

    //only runs the first time the pay is loaded
    if (evt.target && evt.target.id === 'content') {
        //window.addEventListener('beforeunload', budgetUnloadPrompt);
        attachInjectModalListeners();
        //displayDiscrepanciesModal(window.CONFIG.discrepancies);
        displayBadge('recommendations-pay', window.CONFIG.pay_recommendations);
        displayBadge('recommendations-tsp', window.CONFIG.tsp_recommendations);
        displayBadge('discrepancies', window.CONFIG.discrepancies);
    }

    highlightChanges('pay');
    highlightChanges('tsp');
    toggleRows('variables');
    toggleRows('tsp-rates');
    enableInputs();
    disableDrillsButtons();
    disableTSPRateButtons();

    document.getElementById('budget-pay').scrollTop = payScrollTop;
    document.getElementById('budget-tsp').scrollTop = tspScrollTop;
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
        const row = e.target.getAttribute('data-header');
        const value = e.target.getAttribute('data-value');
        const month = e.target.getAttribute('data-month');
        let tooltip = '';

        if (row === 'Months in Service' && value) {
            const months = parseInt(value, 10) % 12;
            const years = Math.floor(parseInt(value, 10) / 12);
            tooltip = `${years} year${years !== 1 ? 's' : ''} ${months} month${months !== 1 ? 's' : ''}`;
        } 
        else if (row === 'Branch' && value) {
            tooltip = getRowValue('pay', 'Branch Long', month);
        }
        else if (row === 'Component' && value) {
            tooltip = getRowValue('pay', 'Component Long', month);
        }
        else if (row === 'Grade' && value) {
            tooltip = getRowValue('pay', 'Rank Long', month);
        }
        else if (row === 'Zip Code' && value) {
            tooltip = getRowValue('pay', 'Military Housing Area Long', month);
        }
        else if (row === 'OCONUS Locality Code' && value) {
            tooltip = getRowValue('pay', 'OCONUS Locality Code Long', month);
        }
        else if (row === 'Home of Record' && value) {
            tooltip = getRowValue('pay', 'Home of Record Long', month);
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
    if (e.target.classList.contains('button-modal-info')) {
        const modalId = e.target.getAttribute('data-modal');
        if (modalId) {
            const modalCheckbox = document.getElementById(modalId);
            if (modalCheckbox) {
                modalCheckbox.checked = true;
            }
        }
    }

    if (e.target && e.target.id === 'button-modal-guide-pay') {
        document.getElementById('modal-guide-pay').checked = true;
    }

    if (e.target && e.target.id === 'button-modal-inject') {
        document.getElementById('modal-inject').checked = true;
        resetInjectModal();
    }

    if (e.target && e.target.id === 'button-modal-account-deposit') {
        buildAccountModal("Direct Deposit Account")
    }

    if (e.target && e.target.id === 'button-modal-discrepancies') {
        displayDiscrepancies(window.CONFIG.discrepancies);
    }

    if (e.target && e.target.id === 'button-modal-recommendations-pay') {
        displayRecommendations('pay', window.CONFIG.pay_recommendations);
    }

    if (e.target && e.target.id === 'button-modal-guide-tsp') {
        document.getElementById('modal-guide-tsp').checked = true;
    }

    if (e.target && e.target.id === 'button-modal-account-tsp') {
        buildAccountModal("TSP Account");
    }

    if (e.target && e.target.id === 'button-modal-tsp-analysis') {
        document.getElementById('modal-tsp-analysis').checked = true;
    }

    if (e.target && e.target.id === 'button-modal-recommendations-tsp') {
        displayRecommendations('tsp', window.CONFIG.tsp_recommendations);
    }

    // build edit modal on cell button click
    if (e.target.classList.contains('button-modal-dynamic')) {
        let header = e.target.getAttribute('data-header');
        let month = e.target.getAttribute('data-month');
        let field = e.target.getAttribute('data-field');
        buildEditModal(header, month, field);
    }

    // close modal from close button in modal
    if (e.target.classList.contains('button-modal-close')) {
        document.querySelectorAll('.modal-state:checked').forEach(function(input) {
            input.checked = false;
        });
    }

    // remove row button click
    if (e.target.classList.contains('button-remove-row')) {
        let header = e.target.getAttribute('data-header');

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
                target: '#budgets',
                swap: 'innerHTML',
                values: { header: header }
            });
            showToast("Row " + header + " removed");
        }
        e.stopPropagation();
    }

    // export pay button
    if (e.target && e.target.id === 'button-export-pay') {
        e.preventDefault();
        exportBudget('pay');
    }

    // export tsp button
    if (e.target && e.target.id === 'button-export-tsp') {
        e.preventDefault();
        exportBudget('tsp');
    }
});


document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'dropdown-months-num') {
        disableInputs();
    }

    if (e.target && e.target.id === 'checkbox-highlight-pay') {
        highlightChanges('pay');
    }

    if (e.target && e.target.id === 'checkbox-variables') {
        toggleRows('variables');
    }

    if (e.target && e.target.id === 'checkbox-editable') {
        boldEditableCells(e.target.checked);
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
