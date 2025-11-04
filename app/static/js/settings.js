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


function displayDiscrepancies(discrepancies) {
    const discrepancyMetadata = window.CONFIG.DISCREPANCIES || {};

    openDynamicModal('mid');
    displayBadge('discrepancies', []);

    const modalContent = document.getElementById('modal-content-dynamic');

    let html = `
        <h2>Pay Discrepancies</h2>
        <div id="discrepancies-description">
            PayLES performed an analysis to find any discrepancies between the uploaded LES and calculated values for the first month. 
            The calculated values are based upon variables pulled from the LES, such as rank, years of service, and location. 
            <br><br>
            The factors that may cause a discrepancy are outdated data sets used by PayLES, pay errors, or extremely unique individual circumstances.
            If there are any discrepancies, please review them carefully.
            PayLES cannot account for every possible pay scenario, so it is important to verify all information.
            However, the discrepancies can also be an indicator for potential pay issues.
            If you have any questions, please reach out to your local finance office for further assistance.
        </div>
    `;

    if (discrepancies && discrepancies.length > 0) {
        let tableRows = discrepancies.map(row => {
            let meta = discrepancyMetadata[row.header] || {};
            let difference = (!isNaN(parseFloat(row.les_value)) && !isNaN(parseFloat(row.calc_value)))
                ? parseFloat(row.les_value) - parseFloat(row.calc_value)
                : null;
            let formattedDifference = difference !== null ? formatValue(difference) : '';
            let officialSource = meta.url && meta.linkName
                ? `<a href="${meta.url}" target="_blank" rel="noopener noreferrer">${meta.linkName}</a>`
                : '';
            return `
                <tr>
                    <td>${row.header}</td>
                    <td>${formatValue(row.les_value)}</td>
                    <td>${formatValue(row.calc_value)}</td>
                    <td>${formattedDifference}</td>
                    <td>${officialSource}</td>
                </tr>
            `;
        }).join('');

        html += `
            <div id="discrepancies-table-container">
                <table class="modal-table">
                    <tr>
                        <td></td>
                        <td>Value from LES</td>
                        <td>Calculated Value</td>
                        <td>Difference</td>
                        <td>Official Source</td>
                    </tr>
                    ${tableRows}
                </table>
                <div class="modal-list-text">PayLES found these discrepancies.</div>
            </div>
        `;
    } else {
        html += `
            <div id="discrepancies-table-container">
                <div class="modal-list-text">No discrepancies found.</div>
            </div>
        `;
    }

    let messages = '';
    if (discrepancies && discrepancies.length > 0) {
        messages = discrepancies.map(row => {
            let meta = discrepancyMetadata[row.header];
            return meta && meta.message ? `<div class="modal-list-text">${meta.message}</div>` : '';
        }).join('');
    }

    html += `<div id="discrepancies-message-container">${messages}</div>`;

    modalContent.innerHTML = html;
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

    // get a list of all months in TSP budget for the first editable month's year
    let monthsInTSPForYear = [];
    for (let i = 0; i < months.length; i++) {
        if (getRowValue("Year", months[i]) === year) {
            monthsInTSPForYear.push(months[i]);
        }
    }

    // first editable month index is used to determine which months earlier in the year are grayed out
    const firstEditableMonthIndex = MONTHS_SHORT.indexOf(months[1]);
    // last editable month index is used to determine which months later in the year are extrapolated
    const lastEditableMonthIndex = MONTHS_SHORT.indexOf(monthsInTSPForYear[monthsInTSPForYear.length - 1]);

    // set tspGoal from localStorage or default to TSP_ELECTIVE_LIMIT
    let tspGoal = parseFloat(localStorage.getItem('tsp_goal')) || TSP_ELECTIVE_LIMIT;

    openDynamicModal('wide');
    const modalContent = document.getElementById('modal-content-dynamic');

    function render() {
        let electiveDeferralRemaining = getRowValue("Elective Deferral Remaining", months[0]);
        let electiveDeferralContribution = Math.max(TSP_ELECTIVE_LIMIT - electiveDeferralRemaining, 0);
        let tspGoalRemaining = Math.max(tspGoal - electiveDeferralContribution, 0);
        let minimumContribution = tspGoalRemaining / (MONTHS_SHORT.length - (firstEditableMonthIndex));
        let lastBasePayValue = getRowValue("Base Pay Total", monthsInTSPForYear[monthsInTSPForYear.length - 1]);

        let monthsRow = '';
        let minimumContributionRow = '';
        let basePayRow = '';
        let percentageOfBasePayRow = '';
        let showExtrapolatedNote = false;

        for (let i = 0; i < MONTHS_SHORT.length; i++) {
            const month = MONTHS_SHORT[i];
            const isEmpty = i < firstEditableMonthIndex;
            const isExtrapolated = i > lastEditableMonthIndex;
            if (isExtrapolated) showExtrapolatedNote = true;

            monthsRow += `<td>${month}${isExtrapolated ? '*' : ''}</td>`;

            minimumContributionRow += `<td${isEmpty ? ' class="cell-grayout"' : ''}>`;
            if (!isEmpty) minimumContributionRow += `$${minimumContribution.toFixed(2)}`;
            minimumContributionRow += `</td>`;

            let basePay = null;
            if (!isEmpty && !isExtrapolated) {
                basePay = getRowValue("Base Pay Total", month);
            } else if (!isEmpty && isExtrapolated) {
                basePay = lastBasePayValue;
            }
            basePayRow += `<td${isEmpty ? ' class="cell-grayout"' : ''}>`;
            if (basePay !== null && basePay !== undefined && !isEmpty) {
                basePayRow += `$${basePay.toFixed(2)}`;
            }
            basePayRow += `</td>`;

            let percentageOfBasePay = '';
            if (basePay && !isEmpty) {
                percentageOfBasePay = ((minimumContribution / basePay) * 100).toFixed(2) + "%";
            }
            percentageOfBasePayRow += `<td${isEmpty ? ' class="cell-grayout"' : ''}>${percentageOfBasePay}</td>`;
        }

        let table = `
            <table class="modal-table table-tsp-rate-calculator">
                <tr><td></td>${monthsRow}</tr>
                <tr><td>Minimum Contribution</td>${minimumContributionRow}</tr>
                <tr><td>Base Pay</td>${basePayRow}</tr>
                <tr><td>Percent of Base Pay</td>${percentageOfBasePayRow}</tr>
            </table>
            ${showExtrapolatedNote ? `<div id="extrapolated-note">* extrapolates previous month data</div>` : ''}
        `;

        modalContent.innerHTML = `
            <h2>TSP Rate Calculator for ${year}</h2>
            <div>
                The TSP Rate Calculator determines the minimum TSP contribution percentage of your base pay to achieve a TSP contribution goal. 
                Only months remaining in the year where you can make TSP contributions are taken into account.
                This calculator's functionality mirrors the <a href="https://www.tsp.gov/making-contributions/how-much-can-i-contribute/#panel-1" target="_blank" rel="noopener noreferrer">official TSP Contribution Calculator</a>.
                <br><br>
                You cannot set a goal higher than the current yearly elective deferral limit, which is <b>$${TSP_ELECTIVE_LIMIT.toLocaleString()}</b>.
                <br><br>
                Additionally, you have already contributed <b>$${electiveDeferralContribution.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</b> to the TSP year-to-date, meaning the maximum additional amount you can contribute is <b>$${electiveDeferralRemaining.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</b>.
            </div>
            <div class="tsp-rate-calculator-goal-container">
                <span>Enter TSP Contribution Goal: </span>
                <div id="tsp-rate-calculator-goal-location"></div>
                <button id="button-tsp-rate-calculator-update" class="button-generic button-positive">Update</button>
            </div>
            ${table}
        `;

        const location = document.getElementById('tsp-rate-calculator-goal-location');
        const wrapper = createStandardInput('TSP Goal', 'float', tspGoal);
        const input = wrapper.querySelector('input');
        input.id = 'tsp-rate-calculator-goal';
        input.setAttribute('max', TSP_ELECTIVE_LIMIT);
        location.appendChild(wrapper);

        modalContent.querySelector('#button-tsp-rate-calculator-update').addEventListener('click', function() {
            let goal = parseFloat(modalContent.querySelector('#tsp-rate-calculator-goal').value) || 0;
            if (goal > TSP_ELECTIVE_LIMIT) {
                showToast(`Cannot enter a value greater than the TSP elective limit ($${TSP_ELECTIVE_LIMIT.toLocaleString()})`);
                return;
            }
            tspGoal = goal;
            localStorage.setItem('tsp_goal', goal);
            render();
        });
    }

    render();
}