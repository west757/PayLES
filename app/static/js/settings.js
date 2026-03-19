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

    const inputRow = document.createElement('div');
    inputRow.className = 'account-row-initial';
    const inputLabel = document.createElement('p');
    inputLabel.textContent = 'Initial Value:';

    inputRow.appendChild(inputLabel);
    inputRow.appendChild(createStandardInput('Initial Value', 'float', initial));
    body.appendChild(inputRow);

    bank = window.CONFIG.bank || null;
    if (header === 'Direct Deposit Account' && bank && bank.trim() !== "") {
        const bankRow = document.createElement('div');
        bankRow.className = 'account-row-bank';
        bankRow.textContent = `Bank: ${bank}`;
        body.appendChild(bankRow);
    }

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




function openEFundCalculator() {
    const MONTHS_SHORT = window.CONFIG.MONTHS.map(([short, long]) => short);
    const months = window.CONFIG.months;

    // Calculate average monthly expense and default goal
    let totalExpenses = 0;
    for (let i = 0; i < months.length; i++) {
        totalExpenses += getRowValue('Total Expenses', months[i]);
    }
    let avgMonthlyExpense = months.length ? Math.abs(totalExpenses / months.length) : 0;
    let defaultGoal = Number((avgMonthlyExpense * 6).toFixed(2));

    // Modal state
    let efundGoal = parseFloat(localStorage.getItem('efund_goal')) || defaultGoal;
    let efundCurrentAmount = parseFloat(localStorage.getItem('efund_current_amount')) || 0;
    let mode = localStorage.getItem('efund_mode') || 'contribution'; // 'contribution' or 'months'
    let monthlyContribution = parseFloat(localStorage.getItem('efund_contribution')) || '';
    let monthsToGoal = parseInt(localStorage.getItem('efund_months')) || Math.min(6, months.length);

    openDynamicModal('wide');
    const modalContent = document.getElementById('modal-content-dynamic');

    function render() {
        let tableMonths = months.map(m => m);

        // Net Pay row: direct from budget
        function buildNetPayRow() {
            let rowHtml = '';
            for (let i = 0; i < tableMonths.length; i++) {
                let val = getRowValue('Net Pay', tableMonths[i]);
                rowHtml += `<td>${val !== null ? formatValue(val) : ''}</td>`;
            }
            return rowHtml;
        }

        // Monthly contribution, percent, and emergency fund amount rows
        let contribArr = [];
        let percentArr = [];
        let efundArr = [];
        let runningTotal = efundCurrentAmount;
        let monthsNeeded = 0;
        let contribValue = 0;
        let goalRemaining = Math.max(efundGoal - efundCurrentAmount, 0);

        if (mode === 'contribution') {
            contribValue = parseFloat(monthlyContribution) || 0;
            monthsNeeded = contribValue > 0 ? Math.ceil(goalRemaining / contribValue) : 0;
        } else {
            monthsNeeded = monthsToGoal;
            contribValue = monthsToGoal > 0 ? goalRemaining / monthsToGoal : 0;
        }

        for (let i = 0; i < tableMonths.length; i++) {
            if (runningTotal >= efundGoal) {
                contribArr.push(0);
            } else {
                let toAdd = Math.min(contribValue, efundGoal - runningTotal);
                contribArr.push(toAdd);
                runningTotal += toAdd;
            }
            efundArr.push(runningTotal);
        }

        // Calculate percent of net pay
        for (let i = 0; i < tableMonths.length; i++) {
            let net = getRowValue('Net Pay', tableMonths[i]);
            let percent = (net && contribArr[i]) ? ((contribArr[i] / net) * 100).toFixed(2) + '%' : '';
            percentArr.push(percent);
        }

        // Table HTML
        let table = `
            <table class="modal-table table-efund-calculator">
                <tr>
                    <td></td>
                    ${tableMonths.map(m => `<td>${m}</td>`).join('')}
                </tr>
                <tr>
                    <td>Net Pay</td>
                    ${buildNetPayRow()}
                </tr>
                <tr>
                    <td>Monthly Contribution</td>
                    ${contribArr.map((v) => `<td>${v ? formatValue(v) : ''}</td>`).join('')}
                </tr>
                <tr>
                    <td>% of Net Pay</td>
                    ${percentArr.map((v) => `<td>${v}</td>`).join('')}
                </tr>
                <tr>
                    <td>Emergency Fund Amount</td>
                    ${efundArr.map((v) => `<td>${formatValue(v)}</td>`).join('')}
                </tr>
            </table>
        `;

        // Modal HTML
        modalContent.innerHTML = `
            <h2>Emergency Fund Calculator</h2>
            <div>
                The Emergency Fund Calculator helps you plan to reach your emergency fund goal by either setting a monthly contribution amount or selecting a target number of months. To account for more months in the calculation table, please increase the number of months the budget displays in the settings.
                <br><br>
                The default goal is your average monthly expenses amount, <b>${formatValue(avgMonthlyExpense)}</b>, multiplied by 6. PayLES recommends having an emergency fund of 6 months worth of expenses, but you can adjust the goal to your desired amount.
            </div>
            <div class="efund-goal-container" style="margin-top:1em;">
                <label>Emergency Fund Goal: </label>
                <div id="efund-goal-location" style="display:inline-block;"></div>
            </div>
            <div class="efund-current-container" style="margin-top:0.5em;">
                <label>Current Fund Amount: </label>
                <div id="efund-current-location" style="display:inline-block;"></div>
            </div>
            <div style="margin-top:1em;">
                <label><input type="radio" name="efund-mode" value="contribution" ${mode === 'contribution' ? 'checked' : ''}> Set Monthly Contribution</label>
                <label style="margin-left:2em;"><input type="radio" name="efund-mode" value="months" ${mode === 'months' ? 'checked' : ''}> Set Number of Months</label>
            </div>
            <div id="efund-mode-inputs" style="margin-top:0.5em;">
                ${mode === 'contribution' ? `
                    <label>Monthly Contribution: </label>
                    <span id="efund-contribution-location"></span>
                    <span style="margin-left:1em;">It will take <b>${contribValue > 0 ? monthsNeeded : ''}</b> months to reach your goal.</span>
                ` : `
                    <label>Number of Months: </label>
                    <select id="efund-months" style="width:60px;">
                        ${Array.from({length: Math.max(1, tableMonths.length - 1)}, (_, i) => i + 2).map(n => `<option value="${n}" ${monthsToGoal == n ? 'selected' : ''}>${n}</option>`).join('')}
                    </select>
                    <span style="margin-left:1em;">You need to contribute <b>${formatValue(contribValue)}</b> per month to reach your goal.</span>
                `}
            </div>
            <div style="margin-top:1.5em;">${table}</div>
            <div style="margin-top:1em;">
                Note: The emergency fund amount does not take into account any interest accrued on the saved value. PayLES recommends keeping your emergency fund in a <a href="https://themilitarywallet.com/the-best-online-high-yield-savings-accounts/" target="_blank" rel="noopener noreferrer">High-Yield Savings Account (HYSA)</a> which provide greater average returns around 3.5% (depending on the bank) while still having the money easily accessible.
            </div>
        `;

        // Attach input handlers
        const goalInputWrapper = createStandardInput('Emergency Fund Goal', 'float', efundGoal);
        const goalInput = goalInputWrapper.querySelector('input');
        goalInput.id = 'efund-goal';
        goalInput.min = 1;
        goalInput.style.width = '120px';
        document.getElementById('efund-goal-location').appendChild(goalInputWrapper);

        goalInput.addEventListener('change', function() {
            efundGoal = parseFloat(goalInput.value) || 0;
            localStorage.setItem('efund_goal', efundGoal);
            render();
        });

        // Current emergency fund input
        const currentInputWrapper = createStandardInput('Current Emergency Fund Amount', 'float', efundCurrentAmount);
        const currentInput = currentInputWrapper.querySelector('input');
        currentInput.id = 'efund-current-amount';
        currentInput.min = 0;
        currentInput.style.width = '120px';
        document.getElementById('efund-current-location').appendChild(currentInputWrapper);

        currentInput.addEventListener('change', function() {
            efundCurrentAmount = parseFloat(this.value) || 0;
            localStorage.setItem('efund_current_amount', efundCurrentAmount);
            render();
        });

        // Radio buttons
        Array.from(modalContent.querySelectorAll('input[name="efund-mode"]')).forEach(radio => {
            radio.addEventListener('change', function() {
                mode = this.value;
                localStorage.setItem('efund_mode', mode);
                render();
            });
        });

        // Monthly contribution input (standard input)
        if (mode === 'contribution') {
            const contribInputWrapper = createStandardInput('Monthly Contribution', 'float', monthlyContribution);
            const contribInput = contribInputWrapper.querySelector('input');
            contribInput.id = 'efund-contribution';
            contribInput.min = 1;
            contribInput.style.width = '100px';
            document.getElementById('efund-contribution-location').appendChild(contribInputWrapper);

            contribInput.addEventListener('change', function() {
                monthlyContribution = parseFloat(this.value) || '';
                localStorage.setItem('efund_contribution', monthlyContribution);
                render();
            });
        }

        // Months dropdown
        const monthsInput = modalContent.querySelector('#efund-months');
        if (monthsInput) {
            monthsInput.addEventListener('change', function() {
                monthsToGoal = parseInt(this.value) || 2;
                localStorage.setItem('efund_months', monthsToGoal);
                render();
            });
        }
    }

    render();
}





function displayDiscrepancies(discrepancies) {
    const discrepancyMetadata = window.CONFIG.DISCREPANCIES || {};

    openDynamicModal('mid');
    displayBadge('discrepancies', []);

    const modalContent = document.getElementById('modal-content-dynamic');

    let html = `
        <h2>Pay Discrepancies</h2>
        <div id="discrepancies-description">
            PayLES conducts an analysis to find any discrepancies between the uploaded LES and program-calculated values for the first month. The calculated values are derived from variables pulled from the LES such as rank, years of service, and stationed location. 
            <br><br>
            Discrepancies are not always indicative of errors. Examples could include PayLES accidentally using outdated data sets or expected discrepancies with calculating federal income tax. However, other factors that may cause discrepancies could reveal pay errors. If there are any discrepancies, please review them carefully. PayLES cannot account for every possible pay scenario so it is important to verify all information. If you have any questions, please reach out to your local finance office for further assistance.
        </div>
    `;

    if (discrepancies && discrepancies.length > 0) {
        let tableRows = discrepancies.map(row => {
            let meta = discrepancyMetadata[row.header] || {};
            let difference = (!isNaN(parseFloat(row.les_value)) && !isNaN(parseFloat(row.calc_value)))
                ? parseFloat(row.les_value) - parseFloat(row.calc_value)
                : null;
            let formattedDifference = difference !== null ? formatValue(difference) : '';
            let officialSource = `<a href="${meta.url}" target="_blank" rel="noopener noreferrer">${meta.urlname}</a>`;
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
    if (discrepancies.length > 0) {
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
                You have already contributed <b>$${electiveDeferralContribution.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</b> to the TSP year-to-date, meaning the maximum additional amount you can contribute is <b>$${electiveDeferralRemaining.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</b>.
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


// export budget to xlsx or csv using SheetJS
// export budget to xlsx, csv, or pdf
function exportBudget(budgetName) {
    let filename, budget, filetype;

    let title;
    if (budgetName === 'pay') {
        budget = document.getElementById('budget-pay-table');
        filetype = document.getElementById('dropdown-export-pay').value;
        filename = 'PayLES_Budget';
        title = 'PayLES Budget';
    } else if (budgetName === 'tsp') {
        budget = document.getElementById('budget-tsp-table');
        filetype = document.getElementById('dropdown-export-tsp').value;
        filename = 'PayLES_TSP_Budget';
        title = 'PayLES TSP Budget';
    }

    if (filetype === 'pdf') {
        let clone = budget.cloneNode(true);
        clone.querySelectorAll('.button-remove-row').forEach(btn => btn.remove());
        let tempDiv = document.createElement('div');
        tempDiv.style.position = 'fixed';
        tempDiv.style.left = '-9999px';
        tempDiv.appendChild(clone);
        document.body.appendChild(tempDiv);

        html2canvas(clone, { backgroundColor: "#fff", scale: 2 }).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            const pdf = new window.jspdf.jsPDF({
                orientation: 'portrait',
                unit: 'pt',
                format: 'a4'
            });

            const marginX = 38;
            const marginY = 38;
            const pageWidth = pdf.internal.pageSize.getWidth() - marginX * 2;
            const pageHeight = pdf.internal.pageSize.getHeight() - marginY * 2;

            // Title and date
            const dateStr = "Generated on " + new Date().toLocaleDateString();
            const titleFontSize = 16;
            const dateFontSize = 12;
            const titleY = marginY - 10;
            // Calculate width for right-aligned date
            pdf.setFontSize(dateFontSize);
            const dateWidth = pdf.getTextWidth(dateStr);
            const dateX = pdf.internal.pageSize.getWidth() - marginX - dateWidth;

            // Calculate image scaling
            const imgWidth = canvas.width;
            const imgHeight = canvas.height;
            const ratio = Math.min(pageWidth / imgWidth, 1); // Don't upscale
            const scaledWidth = imgWidth * ratio;
            const scaledHeight = imgHeight * ratio;

            let pageNum = 0;

            // If the image fits on one page
            if (scaledHeight <= pageHeight) {
                pdf.setFontSize(titleFontSize);
                pdf.text(title, marginX, titleY);
                pdf.setFontSize(dateFontSize);
                pdf.text(dateStr, dateX, titleY);
                // Table image below the title/date
                const tableY = marginY + 10;
                pdf.addImage(
                    imgData,
                    'PNG',
                    marginX,
                    tableY,
                    scaledWidth,
                    scaledHeight
                );
            } else {
                // Multi-page logic
                let pageCanvas = document.createElement('canvas');
                let pageCtx = pageCanvas.getContext('2d');
                pageCanvas.width = imgWidth;
                pageCanvas.height = Math.floor(pageHeight / ratio);

                let renderedHeight = 0;
                while (renderedHeight < imgHeight) {
                    // Clear and draw the current slice
                    pageCtx.clearRect(0, 0, pageCanvas.width, pageCanvas.height);
                    pageCtx.drawImage(
                        canvas,
                        0, renderedHeight,
                        imgWidth, pageCanvas.height,
                        0, 0,
                        imgWidth, pageCanvas.height
                    );
                    let pageImgData = pageCanvas.toDataURL('image/png');
                    if (pageNum > 0) pdf.addPage();
                    pdf.setFontSize(titleFontSize);
                    pdf.text(title, marginX, titleY);
                    pdf.setFontSize(dateFontSize);
                    pdf.text(dateStr, dateX, titleY);
                    // Table image below the title/date
                    const tableY = marginY + 10;
                    pdf.addImage(
                        pageImgData,
                        'PNG',
                        marginX,
                        tableY,
                        scaledWidth,
                        pageHeight
                    );
                    renderedHeight += pageCanvas.height;
                    pageNum++;
                }
            }

            pdf.save(filename + '.pdf');
            document.body.removeChild(tempDiv);
        });
    } else {
        let fullFilename = filetype === 'xlsx' ? filename + '.xlsx' : filename + '.csv';
        let clone = budget.cloneNode(true);
        clone.querySelectorAll('.button-remove-row').forEach(btn => btn.remove());
        let workbook = XLSX.utils.table_to_book(clone, { sheet: filename, raw: true });
        if (filetype === 'xlsx') {
            XLSX.writeFile(workbook, fullFilename);
        } else {
            XLSX.writeFile(workbook, fullFilename, { bookType: 'csv' });
        }
    }
}