// Add this script to your page (e.g., at the end of budget.html)
(function() {
    const container = document.getElementById('budget-container');
    let fadeTimeout;

    function showScrollbar() {
        container.classList.remove('hide-scrollbar');
        clearTimeout(fadeTimeout);
        fadeTimeout = setTimeout(() => {
            container.classList.add('hide-scrollbar');
        }, 2000); // 2 seconds of inactivity
    }

    if (container) {
        container.addEventListener('scroll', showScrollbar);
        container.addEventListener('mouseenter', showScrollbar);
        container.addEventListener('mousemove', showScrollbar);
        // Start faded out
        container.classList.add('hide-scrollbar');
    }
})();