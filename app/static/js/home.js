document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.home-tab-btn');
    const tabContents = document.querySelectorAll('.home-tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active from all buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            // Hide all tab contents
            tabContents.forEach(c => c.style.display = 'none');

            // Activate clicked button
            btn.classList.add('active');
            // Show corresponding tab content
            const tabId = 'tab-' + btn.getAttribute('data-tab');
            const tabContent = document.getElementById(tabId);
            if (tabContent) {
                tabContent.style.display = 'block';
            }
        });
    });

    // Ensure default tab is visible on load
    const defaultTab = document.querySelector('.home-tab-btn.active');
    if (defaultTab) {
        const tabId = 'tab-' + defaultTab.getAttribute('data-tab');
        const tabContent = document.getElementById(tabId);
        if (tabContent) {
            tabContent.style.display = 'block';
        }
    }
});