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
    openDynamicModal('wide');

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
    openDynamicModal('wide');

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
    const config = window.CONFIG;
    const months = config.months; // e.g., ["OCT", "NOV", "DEC", "JAN", "FEB"]
    const monthNames = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
    const electiveLimit = config.TSP_ELECTIVE_LIMIT || 23500;
    const tspBudget = document.getElementById('budget-tsp-table');
    if (!tspBudget) return;

    // Get all months in the budget and their years
    let firstMonthIdx = monthNames.indexOf(months[0]);
    let firstYear = config.years ? config.years[0] : config.CURRENT_YEAR;
    let hasSecondYear = false;
    let secondYear = firstYear + 1;
    let monthsByYear = {};
    if (config.years && config.years.length > 1) {
        hasSecondYear = true;
        secondYear = config.years[1];
        monthsByYear[firstYear] = [];
        monthsByYear[secondYear] = [];
        for (let i = 0; i < months.length; i++) {
            monthsByYear[config.years[i]].push(months[i]);
        }
    } else {
        monthsByYear[firstYear] = months;
    }

    // Helper to get Base Pay Total row values for a given month
    function getBasePayTotals() {
        let basePayRow = null;
        for (let row of tspBudget.rows) {
            if (row.cells[0] && row.cells[0].textContent.trim() === "Base Pay Total") {
                basePayRow = row;
                break;
            }
        }
        if (!basePayRow) return [];
        // skip header cell
        let vals = [];
        for (let i = 1; i < basePayRow.cells.length; i++) {
            let val = basePayRow.cells[i].textContent.replace(/[^0-9.\-]/g, "");
            vals.push(parseFloat(val) || 0);
        }
        return vals;
    }

    // Build table for a given year
    function buildTable(year, goal) {
        let basePayTotals = getBasePayTotals();
        let table = `<table class="modal-table tsp-rate-calc-table"><tr><td>Month</td>`;
        for (let m of monthNames) table += `<td>${m}</td>`;
        table += `</tr><tr><td>Required Contribution</td>`;
        let monthsInYear = monthNames.length;
        let budgetMonths = monthsByYear[year] || [];
        let firstBudgetMonthIdx = budgetMonths.length ? monthNames.indexOf(budgetMonths[0]) : 0;
        let lastBudgetMonthIdx = budgetMonths.length ? monthNames.indexOf(budgetMonths[budgetMonths.length-1]) : 0;
        let now = new Date();
        let currentYear = now.getFullYear();
        let currentMonthIdx = now.getMonth();
        let grayoutIdx = (year === currentYear) ? currentMonthIdx : -1;
        let monthsToContribute = 0;
        for (let i = 0; i < monthsInYear; i++) {
            // Only count months that are not grayed out and are in/after first budget month
            if (i > grayoutIdx && (i >= firstBudgetMonthIdx)) monthsToContribute++;
        }
        let reqContrib = monthsToContribute ? goal / monthsToContribute : 0;
        let extrapolate = false;
        for (let i = 0; i < monthsInYear; i++) {
            let gray = (i <= grayoutIdx || i < firstBudgetMonthIdx);
            let cell = `<td${gray ? ' class="tsp-rate-calc-grayout"' : ''}>`;
            if (!gray) cell += `$${reqContrib.toFixed(2)}`;
            cell += `</td>`;
            table += cell;
        }
        table += `</tr><tr><td>Base Pay</td>`;
        for (let i = 0; i < monthsInYear; i++) {
            let gray = (i <= grayoutIdx || i < firstBudgetMonthIdx);
            let val = null;
            let asterisk = "";
            // Try to get base pay from budget, else extrapolate
            let budgetIdx = budgetMonths.indexOf(monthNames[i]);
            if (budgetIdx !== -1 && basePayTotals[budgetIdx] !== undefined) {
                val = basePayTotals[budgetIdx];
            } else if (budgetMonths.length && i > lastBudgetMonthIdx) {
                // extrapolate using last month
                val = basePayTotals[basePayTotals.length-1];
                asterisk = "*";
                extrapolate = true;
            }
            let cell = `<td${gray ? ' class="tsp-rate-calc-grayout"' : ''}>`;
            if (val !== null && !gray) cell += `$${val.toFixed(2)}${asterisk}`;
            cell += `</td>`;
            table += cell;
        }
        table += `</tr><tr><td>Percentage of Base Pay</td>`;
        for (let i = 0; i < monthsInYear; i++) {
            let gray = (i <= grayoutIdx || i < firstBudgetMonthIdx);
            let val = null, pct = "";
            let budgetIdx = budgetMonths.indexOf(monthNames[i]);
            if (budgetIdx !== -1 && basePayTotals[budgetIdx] !== undefined) {
                val = basePayTotals[budgetIdx];
            } else if (budgetMonths.length && i > lastBudgetMonthIdx) {
                val = basePayTotals[basePayTotals.length-1];
            }
            if (val && !gray) pct = ((reqContrib / val) * 100).toFixed(2) + "%";
            let cell = `<td${gray ? ' class="tsp-rate-calc-grayout"' : ''}>`;
            if (val && !gray) cell += pct;
            cell += `</td>`;
            table += cell;
        }
        table += `</tr></table>`;
        if (extrapolate) table += `<div class="tsp-rate-calc-note">* extrapolates previous month data</div>`;
        return table;
    }

    // Modal HTML
    let modalCheckbox = document.getElementById('modal-tsp-rate-calculator');
    let modalDiv = modalCheckbox.nextElementSibling; // .modal
    let modalInner = modalDiv.querySelector('.modal-inner');
    let year1 = firstYear, year2 = secondYear;
    let year1Goal = electiveLimit, year2Goal = electiveLimit;
    let year2Enabled = hasSecondYear;
    let currentYearSelected = true;

    function render() {
        let html = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h2>TSP Rate Calculator</h2>
                    <div style="margin-bottom: 1rem;">This calculator determines the expected TSP contribution percentage to achieve a TSP contribution goal.</div>
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span>Enter TSP Contribution Goal: </span>
                        <input id="tsp-rate-calc-goal" type="number" min="0" step="0.01" value="${currentYearSelected ? year1Goal : year2Goal}" style="margin-left: 1rem; width: 8rem;">
                    </div>
                    <div style="font-size: 0.95em; color: #444; margin-bottom: 1.5rem;">
                        The contribution limit is set to be the elective deferral limit, which is $${electiveLimit.toLocaleString()}
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem; margin-left: 2rem;">
                    <label style="display: flex; align-items: center;">
                        <input type="radio" name="tsp-rate-calc-year" value="year1" ${currentYearSelected ? "checked" : ""}>
                        <span style="margin-left: 0.5em;">${year1}</span>
                    </label>
                    <label style="display: flex; align-items: center; color: ${year2Enabled ? "#000" : "#aaa"};">
                        <input type="radio" name="tsp-rate-calc-year" value="year2" ${!currentYearSelected ? "checked" : ""} ${year2Enabled ? "" : "disabled"}>
                        <span style="margin-left: 0.5em;">${year2}</span>
                    </label>
                </div>
            </div>
            <div id="tsp-rate-calc-table-container" style="margin: 2rem 0 0 0; text-align: center;">
                ${currentYearSelected ? buildTable(year1, year1Goal) : buildTable(year2, year2Goal)}
            </div>
        `;
        modalInner.innerHTML = `
            <button class="button-modal-close" type="button">✖</button>
            ${html}
        `;
        // Add listeners
        modalInner.querySelector('input[name="tsp-rate-calc-year"][value="year1"]').addEventListener('change', function() {
            currentYearSelected = true;
            render();
        });
        modalInner.querySelector('input[name="tsp-rate-calc-year"][value="year2"]').addEventListener('change', function() {
            currentYearSelected = false;
            render();
        });
        modalInner.querySelector('#tsp-rate-calc-goal').addEventListener('input', function(e) {
            if (currentYearSelected) {
                year1Goal = parseFloat(e.target.value) || 0;
            } else {
                year2Goal = parseFloat(e.target.value) || 0;
            }
            render();
        });
    }

    render();
    modalCheckbox.checked = true;
}