function populateAccountRowList() {
    const listDiv = document.getElementById('account-row-list');
    listDiv.innerHTML = '';
    const budget = window.CONFIG.budget || [];
    const selectable = budget.filter(r => ['e','d','a','c', 'x'].includes(r.type));
    if (selectable.length === 0) {
        listDiv.textContent = 'No eligible rows available.';
        return;
    }
    selectable.forEach(row => {
        const item = document.createElement('div');
        item.className = 'account-row-selectable';
        item.textContent = row.header;
        item.dataset.header = row.header;
        item.tabIndex = 0;
        item.addEventListener('click', function() {
            item.classList.toggle('selected');
        });
        item.addEventListener('keydown', function(e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                item.classList.toggle('selected');
            }
        });
        listDiv.appendChild(item);
    });
}

function getSelectedAccountRows() {
    return Array.from(document.querySelectorAll('.account-row-selectable.selected')).map(div => div.dataset.header);
}

function resetAccountModal() {
    document.getElementById('account-header').value = '';
    document.getElementById('account-value').value = '';
    document.getElementById('account-interest').value = '';
    document.querySelectorAll('input[name="account-calc-type"]').forEach(r => r.checked = false);
    document.querySelector('input[name="account-calc-type"][value="monthly"]').checked = true;
    document.querySelectorAll('.account-row-selectable').forEach(div => div.classList.remove('selected'));
}

function attachAccountModalListeners() {    
    resetAccountModal();
    populateAccountRowList();

    document.getElementById('account-add-button').addEventListener('click', function() {
        const selectedRows = getSelectedAccountRows();
        const header = document.getElementById('account-header').value.trim();
        const value = document.getElementById('account-value').value.trim();
        const interest = document.getElementById('account-interest').value.trim();
        const percent = document.getElementById('account-percent').value.trim();
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
                percent: percent,
                interest: interest,
                calc_type: calcType,
                rows: selectedRows.join(',')
            }
        });
        document.getElementById('account').checked = false;
    });
}