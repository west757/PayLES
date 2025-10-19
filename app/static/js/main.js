// stores scroll position of pay and tsp, used to restore after htmx swap
let payScrollTop = 0;
let tspScrollTop = 0;
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


// save scroll position before any htmx request that will update budgets
document.body.addEventListener('htmx:beforeRequest', function(evt) {
    // only save if the pay is present
    const budgetPay = document.getElementById('budget-pay');
    if (budgetPay) {
        payScrollTop = budgetPay.scrollTop;
    }
    // only save if the tsp is present
    const budgetTSP = document.getElementById('budget-tsp');
    if (budgetTSP) {
        tspScrollTop = budgetTSP.scrollTop;
    }
});


// htmx after swap event listener, runs every time the pay is loaded
document.body.addEventListener('htmx:afterSwap', function(evt) {
    getConfigData();

    //only runs the first time the pay is loaded
    if (evt.target && evt.target.id === 'content') {
        //window.addEventListener('beforeunload', payUnloadPrompt);
        //attachInjectModalListeners();
        displayDiscrepanciesModal(window.CONFIG.discrepancies);
    }

    highlightChanges('pay');
    highlightChanges('tsp');
    toggleRows('variables');
    toggleRows('tsp-rates');
    enableInputs();
    disableDrillsButtons();
    disableTSPRateButtons();
    displayRecommendations(window.CONFIG.recommendations);

    const budgetPay = document.getElementById('budget-pay');
    if (budgetPay && typeof payScrollTop === 'number') {
        budgetPay.scrollTop = payScrollTop;
    }
    const budgetTSP = document.getElementById('budget-tsp');
    if (budgetTSP && typeof tspScrollTop === 'number') {
        budgetTSP.scrollTop = tspScrollTop;
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
        document.getElementById('modal-discrepancies').checked = true;
        const badge = document.getElementById('badge-discrepancies');
        if (badge) badge.style.display = 'none';
    }

    if (e.target && e.target.id === 'button-modal-recommendations') {
        document.getElementById('modal-recommendations').checked = true;
        const badge = document.getElementById('badge-recommendations');
        if (badge) badge.style.display = 'none';
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

    // open dynamic modal on cell button click
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
