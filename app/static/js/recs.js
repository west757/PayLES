function getFirstMonth() {
    if (!window.CONFIG || !window.CONFIG.budget || !Array.isArray(window.CONFIG.budget) || window.CONFIG.budget.length === 0) return null;
    const months = Object.keys(window.CONFIG.budget[0]).filter(k => !['header','type','sign','field','tax','editable','modal'].includes(k));
    return months.length ? months[0] : null;
}

function getRow(header) {
    if (!window.CONFIG || !window.CONFIG.budget || !Array.isArray(window.CONFIG.budget)) return null;
    return window.CONFIG.budget.find(r => r.header === header);
}

function getRowValue(header, month, parseFn = x => x) {
    const row = window.CONFIG.budget.find(r => r.header && r.header.toLowerCase().includes(header));
    return row && month in row ? parseFn(row[month]) : (parseFn === parseFloat || parseFn === parseInt ? 0 : '');
}

function getHomeOfRecordRow(abbr) {
    if (!window.CONFIG || !window.CONFIG.HOME_OF_RECORDS || !Array.isArray(window.CONFIG.HOME_OF_RECORDS)) return null;
    return window.CONFIG.HOME_OF_RECORDS.find(r => String(r.abbr).toUpperCase() === String(abbr).toUpperCase());
}

function addRecommendations() {
    const month = getFirstMonth();
    if (!month) return;
    const recs = [];

    // SGLI recommendation
    const sgliCoverage = getRowValue('SGLI Coverage', month, parseFloat);
    if (sgliCoverage === 0) {
        recs.push(`<div class="rec-item"><b>SGLI Coverage:</b> You currently have no SGLI coverage. It is recommended to
             have at least the minimum amount of SGLI coverage, which is a $3.50 monthly premium for $50,000. This ensures you 
             are also provided with Traumatic Injury Protection Coverage (TSGLI).</div>`);
    }


    // TSP recommendation
    const monthsInService = getRowValue('Months in Service', month, parseInt);
    const trad = getRowValue('Trad TSP Base Rate', month, parseFloat);
    const roth = getRowValue('Roth TSP Base Rate', month, parseFloat);
    if (monthsInService >= 24 && (trad + roth) < 5) {
        recs.push(`<div class="rec-item"><b>TSP Base Rate:</b> You are fully vested in the Thrift Savings Plan, however 
            are not currently taking advantage of the service agency automatic matching up to 5%. It is recommended to 
            increase the Traditional TSP or Roth TSP Base Rate contribution percentages to at least 5% to receive the full 
            matching contributions.</div>`);
    }


    // State income tax recommendation
    const homeOfRecord = getRowValue('home of record', month);
    const mha = getRowValue('mha', month);
    const horRow = getHomeOfRecordRow(homeOfRecord);
    if (horRow) {
        const incomeType = horRow.income ? horRow.income.toLowerCase() : '';
        const tooltip = horRow.tooltip || '';
        let showStateTaxMsg = false;

        if (incomeType === 'partial' || incomeType === 'full') {
            showStateTaxMsg = true;
        } else if (incomeType === 'outside' && mha != "Not Found") {
            const mhaState = mha.substring(0,2).toUpperCase();
            if (mhaState === String(homeOfRecord).toUpperCase()) {
                showStateTaxMsg = true;
            }
        }

        if (showStateTaxMsg) {
            let msg = `<div class="rec-item"><b>State Income Tax:</b> You are currently paying state income tax. It is 
            recommended to investigate options and requirements relating to your home of record, as you may be eligible to 
            avoid paying state income tax. This can include changing your home of record to a state which does not tax military 
            income, or meeting certain exemptions for your current home of record.`;
            if (tooltip) msg += `<br><span class="rec-tooltip">${tooltip}</span>`;
            msg += `</div>`;
            recs.push(msg);
        }
    }

    // Render to modal
    const recContent = document.getElementById('rec-content');
    recContent.innerHTML = recs.length === 0 ? '<p>No recommendations at this time.</p>' : recs.join('');
}