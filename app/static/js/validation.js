document.addEventListener('input', function(e) {
    if (e.target.classList.contains('tsp-rate-input')) {
        // Remove non-digit characters and limit to 2 digits
        let val = e.target.value.replace(/\D/g, '');
        if (val.length > 2) val = val.slice(0, 2);
        e.target.value = val;
    }

    if (e.target.classList.contains('input-num')) {
        // Allow only digits and one decimal point
        let val = e.target.value;
        // Remove invalid characters
        val = val.replace(/[^0-9.]/g, '');
        // Only one decimal point allowed
        let parts = val.split('.');
        if (parts.length > 2) {
            val = parts[0] + '.' + parts.slice(1).join('');
        }
        e.target.value = val;
    }
});