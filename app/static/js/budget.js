function updateBudget(monthsNum) {
    htmx.ajax('POST', '/update_budget', {
        target: '#budget',
        swap: 'outerHTML',
        values: { months_display: monthsNum }
    });
}