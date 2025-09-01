document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active from all buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            // Remove active from all tab contents
            tabContents.forEach(c => c.classList.remove('active'));

            // Activate clicked button
            btn.classList.add('active');
            // Show corresponding tab content
            const tabId = 'tab-' + btn.getAttribute('data-tab');
            const tabContent = document.getElementById(tabId);
            if (tabContent) {
                tabContent.classList.add('active');
            }
        });
    });

    // Ensure default tab is visible on load
    const defaultTab = document.querySelector('.tab-button.active');
    if (defaultTab) {
        const tabId = 'tab-' + defaultTab.getAttribute('data-tab');
        const tabContent = document.getElementById(tabId);
        if (tabContent) {
            tabContent.classList.add('active');
        }
    }
});
