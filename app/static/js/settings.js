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
    const months = window.CONFIG.MONTHS; // [["JAN", "January"], ...]
    const monthShorts = months.map(([short, long]) => short);
    const electiveLimit = window.CONFIG.TSP_ELECTIVE_LIMIT || 23500;
    const tspBudget = document.getElementById('budget-tsp-table');

    // Use getRowValue to get years for first and last month
    const firstMonth = monthShorts[0];
    const lastMonth = monthShorts[monthShorts.length - 1];
    const current_year = getRowValue("year", firstMonth);
    const next_year = current_year + 1;
    const last_year = getRowValue("year", lastMonth);

    // Only enable next year if last month is in next_year
    const hasSecondYear = (last_year === next_year);

    // Modal state
    let yearGoals = {};
    [current_year, next_year].forEach(y => {
        let stored = localStorage.getItem('tsp_goal_' + y);
        yearGoals[y] = stored !== null ? parseFloat(stored) : electiveLimit;
    });
    let selectedYear = current_year;

    // Open modal in wide mode
    openDynamicModal('wide');
    const modalContent = document.getElementById('modal-content-dynamic');

    // Helper: get row values by header
    function getRowValues(header) {
        let row = null;
        for (let r of tspBudget.rows) {
            if (r.cells[0] && r.cells[0].textContent.trim() === header) {
                row = r;
                break;
            }
        }
        if (!row) return [];
        let vals = [];
        for (let i = 1; i < row.cells.length; i++) {
            let val = row.cells[i].textContent.replace(/[^0-9.\-]/g, "");
            vals.push(parseFloat(val) || 0);
        }
        return vals;
    }

    // Helper: get YTD TSP Contribution Total for a year
    function getYTDContribution(year) {
        // Find the first month index for this year in the budget
        let idx = -1;
        for (let i = 0; i < monthShorts.length; i++) {
            let colYear = getRowValue("year", monthShorts[i]);
            if (colYear === year) {
                idx = i;
                break;
            }
        }
        if (idx === -1) return 0;
        let ytdVals = getRowValues("YTD TSP Contribution Total");
        return ytdVals[idx] || 0;
    }

    function buildTable(year, goal) {
        let basePayTotals = getRowValues("Base Pay Total");
        let ytdVals = getRowValues("YTD TSP Contribution Total");

        // The actual months present in the TSP budget (e.g., ["MAR", "APR", ...])
        const tspMonths = window.CONFIG.months;
        // Map TSP months to their year
        const tspMonthYears = tspMonths.map(m => getRowValue("year", m));

        // Find the first and last index for this year in the TSP budget
        let firstBudgetIdx = tspMonths.findIndex((m, i) => getRowValue("year", m) === year);
        let lastBudgetIdx = tspMonths.length - 1;
        for (let i = tspMonths.length - 1; i >= 0; i--) {
            if (getRowValue("year", tspMonths[i]) === year) {
                lastBudgetIdx = i;
                break;
            }
        }

        // In canonical month order, find the index of the first TSP month for this year
        let firstTspMonthShort = tspMonths[firstBudgetIdx];
        let firstMonthIdx = monthShorts.indexOf(firstTspMonthShort);
        let lastTspMonthShort = tspMonths[lastBudgetIdx];
        let lastMonthIdx = monthShorts.indexOf(lastTspMonthShort);

        // Grayout: all months before and including the first TSP month for this year
        let grayoutIdx = firstMonthIdx; // inclusive

        // Extrapolation: months after the last TSP month for this year
        let extrapolateIdx = lastMonthIdx;

        // For extrapolation asterisk
        let extrapolatedMonths = {};

        // Calculate how many months are available for contribution (not grayed out)
        let monthsToContribute = 0;
        for (let i = 0; i < monthShorts.length; i++) {
            if (i > grayoutIdx) monthsToContribute++;
        }

        // Get YTD contributed for this year
        function getYTDContributionForMonthIdx(idx) {
            // Find the TSP budget column index for this month
            let tspIdx = tspMonths.findIndex((m, i) => getRowValue("year", m) === year && m === monthShorts[idx]);
            if (tspIdx === -1) tspIdx = firstBudgetIdx;
            return ytdVals[tspIdx] || 0;
        }
        let ytdContributed = getYTDContributionForMonthIdx(firstMonthIdx);

        // The remaining goal is the goal minus YTD contributed, but not less than zero
        let remainingGoal = Math.max(goal - ytdContributed, 0);

        // Required contribution per month (for months not grayed out)
        let reqContrib = monthsToContribute ? remainingGoal / monthsToContribute : 0;

        // Build table
        let table = `<table class="modal-table tsp-rate-calc-table"><tr><td>Month</td>`;
        for (let i = 0; i < monthShorts.length; i++) {
            let extrap = (i > extrapolateIdx && lastMonthIdx !== -1);
            table += `<td>${monthShorts[i]}${extrap ? '*' : ''}</td>`;
            if (extrap) extrapolatedMonths[i] = true;
        }
        table += `</tr><tr><td>Required Contribution</td>`;
        for (let i = 0; i < monthShorts.length; i++) {
            let gray = (i <= grayoutIdx);
            let cell = `<td${gray ? ' class="tsp-rate-calc-grayout"' : ''}>`;
            if (!gray) cell += `$${reqContrib.toFixed(2)}`;
            cell += `</td>`;
            table += cell;
        }
        table += `</tr><tr><td>Base Pay</td>`;
        for (let i = 0; i < monthShorts.length; i++) {
            let gray = (i <= grayoutIdx);
            let val = null;
            // Find the TSP budget column index for this month
            let tspIdx = tspMonths.findIndex((m, idx) => getRowValue("year", m) === year && m === monthShorts[i]);
            if (tspIdx !== -1 && basePayTotals[tspIdx] !== undefined) {
                val = basePayTotals[tspIdx];
            } else if (i > extrapolateIdx && lastBudgetIdx !== -1) {
                // extrapolate using last month
                val = basePayTotals[lastBudgetIdx];
            }
            let cell = `<td${gray ? ' class="tsp-rate-calc-grayout"' : ''}>`;
            if (val !== null && !gray) cell += `$${val.toFixed(2)}`;
            cell += `</td>`;
            table += cell;
        }
        table += `</tr><tr><td>Percentage of Base Pay</td>`;
        for (let i = 0; i < monthShorts.length; i++) {
            let gray = (i <= grayoutIdx);
            let val = null, pct = "";
            let tspIdx = tspMonths.findIndex((m, idx) => getRowValue("year", m) === year && m === monthShorts[i]);
            if (tspIdx !== -1 && basePayTotals[tspIdx] !== undefined) {
                val = basePayTotals[tspIdx];
            } else if (i > extrapolateIdx && lastBudgetIdx !== -1) {
                val = basePayTotals[lastBudgetIdx];
            }
            if (val && !gray) pct = ((reqContrib / val) * 100).toFixed(2) + "%";
            let cell = `<td${gray ? ' class="tsp-rate-calc-grayout"' : ''}>`;
            if (val && !gray) cell += pct;
            cell += `</td>`;
            table += cell;
        }
        table += `</tr></table>`;
        if (Object.keys(extrapolatedMonths).length > 0) {
            table += `<div class="tsp-rate-calc-note">* extrapolates previous month data</div>`;
        }
        return table;
    }

    function render() {
        // Get YTD and remainder for selected year
        let ytdContributed = getYTDContribution(selectedYear);
        let goal = yearGoals[selectedYear];
        let remainder = Math.max(electiveLimit - ytdContributed, 0);

        // Modal content
        modalContent.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                <div style="flex: 1;">
                    <h2>TSP Rate Calculator</h2>
                    <div style="margin-bottom: 1rem;">This calculator determines the expected TSP contribution percentage to achieve a TSP contribution goal.</div>
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span>Enter TSP Contribution Goal: </span>
                        <span id="tsp-rate-calc-goal-wrapper" style="margin-left: 1rem;"></span>
                        <button id="tsp-rate-calc-update" class="button-generic button-positive" style="margin-left: 0.5rem; height: 2rem; font-size: 0.95em;">Update</button>
                    </div>
                    <div style="font-size: 0.95em; color: #444; margin-bottom: 0.5rem;">
                        The contribution limit is set to be the elective deferral limit, which is $${electiveLimit.toLocaleString()}
                    </div>
                    <div style="font-size: 0.95em; color: #444; margin-bottom: 1.5rem;">
                        You have currently contributed <b>$${ytdContributed.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</b> to the TSP. The remainder you can contribute is: <b>$${remainder.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</b>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 0.5rem; margin-left: 2rem; margin-bottom: 1.5rem;">
                    <label style="display: flex; align-items: center;">
                        <input type="radio" name="tsp-rate-calc-year" value="${current_year}" ${selectedYear === current_year ? "checked" : ""}>
                        <span style="margin-left: 0.5em;">${current_year}</span>
                    </label>
                    <label style="display: flex; align-items: center; color: ${hasSecondYear ? "#000" : "#aaa"};">
                        <input type="radio" name="tsp-rate-calc-year" value="${next_year}" ${selectedYear === next_year ? "checked" : ""} ${hasSecondYear ? "" : "disabled"}>
                        <span style="margin-left: 0.5em;">${next_year}</span>
                    </label>
                </div>
            </div>
            <div id="tsp-rate-calc-table-container" style="margin: 2rem 0 0 0; text-align: center;">
                ${buildTable(selectedYear, goal)}
            </div>
        `;

        // Insert standard float input for goal
        const wrapper = document.getElementById('tsp-rate-calc-goal-wrapper');
        const inputWrapper = createStandardInput('TSP Goal', 'float', goal);
        inputWrapper.querySelector('input').id = 'tsp-rate-calc-goal';
        wrapper.appendChild(inputWrapper);

        // Listeners
        modalContent.querySelectorAll('input[name="tsp-rate-calc-year"]').forEach(radio => {
            radio.addEventListener('change', function() {
                selectedYear = parseInt(this.value);
                render();
            });
        });
        modalContent.querySelector('#tsp-rate-calc-update').addEventListener('click', function() {
            let val = parseFloat(modalContent.querySelector('#tsp-rate-calc-goal').value) || 0;
            yearGoals[selectedYear] = val;
            // Save to localStorage
            localStorage.setItem('tsp_goal_' + selectedYear, val);
            render();
        });
    }

    render();
}