// highlight changes in budget compared to previous month
function highlightChanges(budgetName) {
    const highlight_color = getComputedStyle(document.documentElement).getPropertyValue('--highlight_yellow_color').trim();
    let checkbox, budget;

    if (budgetName === 'pay') {
        checkbox = document.getElementById('checkbox-highlight-pay');
        budget = document.getElementById('budget-pay');
    } else if (budgetName === 'tsp') {
        checkbox = document.getElementById('checkbox-highlight-tsp');
        budget = document.getElementById('budget-tsp');
    }

    var rows = budget.getElementsByTagName('tr');

    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName('td');
        var header = cells[0].textContent.trim();

        //start from month 3 (index 2), skip row header and first month
        for (var j = 2; j < cells.length; j++) {
            var cell = cells[j];
            var prevCell = cells[j - 1];

            if (
                checkbox.checked &&
                cell.textContent.trim() !== prevCell.textContent.trim() &&
                !(header === "Difference" && cell.textContent.trim() === "$0.00")
            ) {
                cell.style.backgroundColor = highlight_color;
            } else {
                cell.style.backgroundColor = '';
            }
        }
    }
}


// toggle display of rows
function toggleRows(rowClass) {
    let checkbox, rows;

    if (rowClass === 'variables') {
        checkbox = document.getElementById('checkbox-variables');
        rows = document.getElementsByClassName('row-variable');
    } else if (rowClass === 'tsp-rates') {
        checkbox = document.getElementById('checkbox-tsp-rates');
        rows = document.getElementsByClassName('row-tsp-rate');
    }

    for (let row of rows) {
        row.style.display = checkbox.checked ? 'table-row' : 'none';
    }
}


function boldEditableCells(active) {
    const editableCells = document.querySelectorAll(
        '#budget-pay-table .button-modal-dynamic, #budget-tsp-table .button-modal-dynamic'
    );
    
    editableCells.forEach(cell => {
        if (active) {
            cell.style.fontWeight = 'bold';
        } else {
            cell.style.fontWeight = '';
        }
    });
}


function buildAccountModal(header) {
    openDynamicModal('short');

    if (header === 'Direct Deposit Account') {
        budget = document.getElementById('budget-pay');
        initial = getRowValue('Direct Deposit Account', window.CONFIG.months[0]);
    } else if (header === 'TSP Account') {
        budget = document.getElementById('budget-tsp');
        initial = getRowValue('TSP Account', window.CONFIG.months[0]);
    }

    const content = document.getElementById('modal-content-dynamic');
    content.innerHTML = '';

    const title = document.createElement('h2');
    title.textContent = "Edit " + header;
    content.appendChild(title);

    const body = document.createElement('div');
    body.className = 'modal-dynamic-body';

    const inputLabel = document.createElement('p');
    inputLabel.textContent = 'Initial Value:';
    body.appendChild(inputLabel);
    body.appendChild(createStandardInput('Initial Value', 'float', initial));

    content.appendChild(body);

    const buttons = document.createElement('div');
    buttons.className = 'modal-dynamic-buttons';

    const buttonUpdate = document.createElement('button');
    buttonUpdate.textContent = 'Update';
    buttonUpdate.classList.add('button-generic', 'button-positive');
    buttonUpdate.onclick = function () {
        submitAccountModal(header);
    };
    buttons.appendChild(buttonUpdate);

    const buttonCancel = document.createElement('button');
    buttonCancel.textContent = 'Cancel';
    buttonCancel.classList.add('button-generic', 'button-negative');
    buttonCancel.onclick = function () {
        document.getElementById('modal-dynamic').checked = false;
    };
    buttons.appendChild(buttonCancel);

    content.appendChild(buttons);
}


function submitAccountModal(header) {
    const input = document.querySelector('#modal-content-dynamic input');
    const initial = input.value;

    if (!validateBudgetInput('float', 'Initial Value', initial)) return;

    document.getElementById('modal-dynamic').checked = false;

    htmx.ajax('POST', '/route_update_account', {
        target: '#budgets',
        swap: 'innerHTML',
        values: {
            header: header,
            initial: initial,
        }
    });
}


// export budget to xlsx or csv using SheetJS
function exportBudget(budgetName) {
    let filename;

    if (budgetName === 'pay') {
        var budget = document.getElementById('budget-pay-table');
        var filetype = document.getElementById('dropdown-export-pay').value;
        filename = 'PayLES_Budget';
    } else if (budgetName === 'tsp') {
        var budget = document.getElementById('budget-tsp-table');
        var filetype = document.getElementById('dropdown-export-tsp').value;
        filename = 'PayLES_TSP_Budget';
    }

    var fullFilename = filetype === 'xlsx' ? filename + '.xlsx' : filename + '.csv';

    var clone = budget.cloneNode(true);

    // exclude remove row buttons from export
    clone.querySelectorAll('.button-remove-row').forEach(btn => btn.remove());

    var workbook = XLSX.utils.table_to_book(clone, {sheet: filename, raw: true});
    if (filetype === 'xlsx') {
        XLSX.writeFile(workbook, fullFilename);
    } else {
        XLSX.writeFile(workbook, fullFilename, {bookType: 'csv'});
    }
}


function getDiscrepancyMessage(header) {
    const messages = {
        'SGLI Rate': "There is a discrepancy with the SGLI Rate. This sometimes happens when the SGLI rate dataset has not been recently updated.",
        'BAH': "There is a discrepancy with the BAH. This may be due to recent changes in locality rates.",
        'Federal Taxes': "There is a discrepancy with Federal Taxes. This may be due to differences in withholding or filing status.",
    };
    return messages[header] || null;
}


function displayDiscrepancies(discrepancies) {
    openDynamicModal('mid');

    displayBadge('discrepancies', []);

    const content = document.getElementById('modal-content-dynamic');
    content.innerHTML = '';

    const titleText = 'Pay Discrepancies';
    const title = document.createElement('h2');
    title.textContent = titleText;
    content.appendChild(title);

    const description = document.createElement('p');
    description.innerHTML = 'PayLES performs analysis to find any discrepancies between the uploaded LES and calculated values for the first month. Factors that may cause a discrepancy are an LES older than one month, pay errors, outdated data sets used by PayLES, and certain specific individual circumstances.';
    content.appendChild(description);

    const tableContainer = document.createElement('div');
    tableContainer.id = 'discrepancies-table-container';
    content.appendChild(tableContainer);
    const messageContainer = document.createElement('div');
    messageContainer.id = 'discrepancies-message-container';
    content.appendChild(messageContainer);

    if (!discrepancies || discrepancies.length === 0) {
        return;
    }

    let tableHTML = `<table class="modal-table">
        <tr>
            <td>Header</td>
            <td>Value from LES</td>
            <td>Calculated Value</td>
        </tr>`;
    let messages = [];

    discrepancies.forEach(row => {
        tableHTML += `<tr>
            <td>${row.header}</td>
            <td>${formatValue(row.les_value)}</td>
            <td>${formatValue(row.calc_value)}</td>
        </tr>`;
        const msg = getDiscrepancyMessage(row.header);
        if (msg) messages.push(`<div class="modal-list-text">${msg}</div>`);
    });

    tableHTML += `</table>
        <div class="modal-list-text">PayLES found these discrepancies.</div>`;

    tableContainer.innerHTML = tableHTML;
    messageContainer.innerHTML = messages.join('');
}


function displayRecommendations(budgetName, recommendations) {
    openDynamicModal('mid');

    if (budgetName === 'pay') {
        displayBadge('recommendations-pay', []);
    } else if (budgetName === 'tsp') {
        displayBadge('recommendations-tsp', []);
    }

    const content = document.getElementById('modal-content-dynamic');
    content.innerHTML = '';

    const title = document.createElement('h2');
    title.textContent = budgetName === 'pay' ? 'Budget Recommendations' : 'TSP Recommendations';
    content.appendChild(title);

    const recommendationsList = document.createElement('div');
    if (recommendations.length > 0) {
        recommendationsList.className = 'modal-list-text';
        recommendationsList.innerHTML = recommendations.map(r => `<div>${r}</div>`).join('');
    } else {
        recommendationsList.className = 'modal-list-text';
        recommendationsList.textContent = 'No current recommendations.';
    }
    content.appendChild(recommendationsList);
}





function openTSPRateCalculator() {
    const MONTHS_SHORT = window.CONFIG.MONTHS.map(([short, long]) => short);
    const TSP_ELECTIVE_LIMIT = window.CONFIG.TSP_ELECTIVE_LIMIT;
    const months = window.CONFIG.months;
    const year = getRowValue("Year", months[1]);

    // Build a list of TSP budget months for this year only
    let monthsInTSPForYear = [];
    for (let i = 0; i < months.length; i++) {
        if (getRowValue("Year", months[i]) === year) {
            monthsInTSPForYear.push(months[i]);
        }
    }

    // Find the index of the first and last ediitable month in MONTHS_SHORT
    const firstEditableMonthIndex = MONTHS_SHORT.indexOf(months[1]);
    const lastEditableMonthIndex = MONTHS_SHORT.indexOf(monthsInTSPForYear[monthsInTSPForYear.length - 1]);

    // set tspGoal from localStorage or default to TSP_ELECTIVE_LIMIT
    let tspGoal = parseFloat(localStorage.getItem('tsp_goal')) || TSP_ELECTIVE_LIMIT;

    openDynamicModal('wide');
    const modalContent = document.getElementById('modal-content-dynamic');

    function render() {
        let electiveDeferralRemaining = getRowValue("Elective Deferral Remaining", months[0]);
        let electiveDeferralContribution = Math.max(TSP_ELECTIVE_LIMIT - electiveDeferralRemaining, 0);

        // How many months to contribute (not grayed out)
        let monthsLeftToContribute = MONTHS_SHORT.length - (firstEditableMonthIndex);
        let goalRemaining = Math.max(tspGoal - electiveDeferralContribution, 0);
        let reqContrib = monthsLeftToContribute > 0 ? goalRemaining / monthsLeftToContribute : 0;

        // Get last base pay value from the TSP budget for this year
        let lastBasePayValue = getRowValue("Base Pay Total", monthsInTSPForYear[monthsInTSPForYear.length - 1]);

        let monthsRow = '';
        let minimumContributionRow = '';
        let basePayRow = '';
        let percentageOfBasePayRow = '';
        let extrapolated = false;

        for (let i = 0; i < MONTHS_SHORT.length; i++) {
            const month = MONTHS_SHORT[i];
            // Grayed out if before or equal to months[1]
            const gray = i < firstEditableMonthIndex;
            // Is this an extrapolated month?
            const extrap = i > lastEditableMonthIndex;
            if (extrap) extrapolated = true;

            // Month header
            monthsRow += `<td>${month}${extrap ? '*' : ''}</td>`;

            // Required Contribution
            minimumContributionRow += `<td${gray ? ' class="tsp-rate-calc-grayout"' : ''}>`;
            if (!gray) minimumContributionRow += `$${reqContrib.toFixed(2)}`;
            minimumContributionRow += `</td>`;

            // Base Pay
            let basePay = null;
            if (!gray && !extrap) {
                // Use actual value from TSP budget if available for this year
                if (monthsInTSPForYear.includes(month)) {
                    basePay = getRowValue("Base Pay Total", month);
                }
            } else if (!gray && extrap) {
                basePay = lastBasePayValue;
            }
            basePayRow += `<td${gray ? ' class="tsp-rate-calc-grayout"' : ''}>`;
            if (basePay !== null && basePay !== undefined && !gray) basePayRow += `$${basePay.toFixed(2)}`;
            basePayRow += `</td>`;

            // Percentage of Base Pay
            let pct = '';
            if (basePay && !gray) pct = ((reqContrib / basePay) * 100).toFixed(2) + "%";
            percentageOfBasePayRow += `<td${gray ? ' class="tsp-rate-calc-grayout"' : ''}>${pct}</td>`;
        }

        // Build table
        let table = `
            <table class="modal-table tsp-rate-calc-table">
                <tr><td></td>${monthsRow}</tr>
                <tr><td>Minimum Contribution</td>${minimumContributionRow}</tr>
                <tr><td>Base Pay</td>${basePayRow}</tr>
                <tr><td>Percentage of Base Pay</td>${percentageOfBasePayRow}</tr>
            </table>
            ${extrapolated ? `<div class="tsp-rate-calc-note">* extrapolates previous month data</div>` : ''}
        `;

        modalContent.innerHTML = `
            <div class="tsp-rate-calc-modal-header-row">
                <div class="tsp-rate-calc-modal-header-main">
                    <h2 class="tsp-rate-calc-title">TSP Rate Calculator for ${year}</h2>
                    <div class="tsp-rate-calc-desc">
                        This calculator determines the minimum TSP contribution percentage of your base pay to achieve a TSP contribution goal. The calculator also only takes into account the months remaining in the year where TSP contributions can be made.
                    </div>
                    <div class="tsp-rate-calc-goal-row">
                        <span>Enter TSP Contribution Goal: </span>
                        <span id="tsp-rate-calc-goal-wrapper"></span>
                        <button id="tsp-rate-calc-update" class="button-generic button-positive tsp-rate-calc-update-btn">Update</button>
                    </div>
                    <div class="tsp-rate-calc-limit">
                        The contribution limit is set to be the elective deferral limit, which is $${TSP_ELECTIVE_LIMIT.toLocaleString()}
                    </div>
                    <div class="tsp-rate-calc-ytd">
                        You have currently contributed <b>$${electiveDeferralContribution.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</b> to the TSP. The remainder you can contribute is: <b>$${electiveDeferralRemaining.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</b>
                    </div>
                </div>
            </div>
            <div id="tsp-rate-calc-table-container">
                ${table}
            </div>
        `;

        // Insert standard float input for goal
        const wrapper = document.getElementById('tsp-rate-calc-goal-wrapper');
        const inputWrapper = createStandardInput('TSP Goal', 'float', tspGoal);
        inputWrapper.querySelector('input').id = 'tsp-rate-calc-goal';
        wrapper.appendChild(inputWrapper);

        // Listener for update button
        modalContent.querySelector('#tsp-rate-calc-update').addEventListener('click', function() {
            let val = parseFloat(modalContent.querySelector('#tsp-rate-calc-goal').value) || 0;
            tspGoal = val;
            localStorage.setItem('tsp_goal', val);
            render();
        });
    }

    render();
}