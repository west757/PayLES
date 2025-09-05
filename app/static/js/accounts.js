function resetAccountModal() {
    document.getElementById('account-header').value = '';
    document.getElementById('account-value').value = '';
    document.getElementById('account-interest').value = '';
    document.querySelectorAll('input[name="account-calc-type"]').forEach(r => r.checked = false);
    document.querySelector('input[name="account-calc-type"][value="monthly"]').checked = true;
    // Uncheck all in row list
    document.querySelectorAll('.account-row-checkbox').forEach(cb => cb.checked = false);
}

function populateAccountRowList() {
    const listDiv = document.getElementById('account-row-list');
    listDiv.innerHTML = '';
    const budget = window.CONFIG.budget || [];
    const selectable = budget.filter(r => ['e','d','a','c'].includes(r.type));
    selectable.forEach(row => {
        const label = document.createElement('label');
        label.className = 'account-row-label';
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.className = 'account-row-checkbox';
        cb.value = row.header;
        label.appendChild(cb);
        label.appendChild(document.createTextNode(' ' + row.header));
        listDiv.appendChild(label);
    });
}

function attachAccountModalListeners() {
    // Reset and populate on open
    document.getElementById('account').addEventListener('change', function() {
        if (this.checked) {
            resetAccountModal();
            populateAccountRowList();
        }
    });

    document.getElementById('account-add-button').addEventListener('click', function() {
        const selectedRows = Array.from(document.querySelectorAll('.account-row-checkbox:checked')).map(cb => cb.value);
        const header = document.getElementById('account-header').value.trim();
        const value = document.getElementById('account-value').value.trim();
        const interest = document.getElementById('account-interest').value.trim();
        const calcType = document.querySelector('input[name="account-calc-type"]:checked').value;

        if (!header || selectedRows.length === 0) {
            showToast('Please enter an account header and select at least one row.');
            return;
        }
        if (!/^\d{0,7}(\.\d{0,2})?$/.test(value)) {
            showToast('Please enter a valid initial value.');
            return;
        }
        if (interest && !/^\d{0,2}(\.\d{0,2})?%?$/.test(interest)) {
            showToast('Please enter a valid interest rate.');
            return;
        }

        htmx.ajax('POST', '/route_accounts', {
            target: '#budget',
            swap: 'innerHTML',
            values: {
                header: header,
                value: value,
                interest: interest,
                calc_type: calcType,
                rows: selectedRows.join(',')
            }
        });
        document.getElementById('account').checked = false;
    });
}

// Call attachAccountModalListeners() on page load
document.addEventListener('DOMContentLoaded', attachAccountModalListeners);