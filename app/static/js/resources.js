function initResourcesPage() {
    let RESOURCES = window.CONFIG.RESOURCES;
    const MAX_RESOURCES_DISPLAY = window.CONFIG.MAX_RESOURCES_DISPLAY;
    let searchString = '';
    let selectedCategories = [];
    let selectedBranches = [];
    let noCACRequired = false;
    let currentPage = 1;
    let lastFilteredResources = [];


    function populateFilterPanel(panelID, options, type) {
        const panel = document.getElementById(panelID);
        panel.innerHTML = options.map(opt => `
            <label class="resources-filter-panel-label">
                <input class="resources-filter-panel-checkbox" type="checkbox" value="${opt}" data-type="${type}" />
                ${opt}
            </label>
        `).join('');
    }


    function addFilterButtonEventListener(buttonID, panelID) {
        const button = document.getElementById(buttonID);
        const panel = document.getElementById(panelID);

        button.addEventListener('click', () => {
            panel.classList.toggle('open');
        });

        document.addEventListener('click', (e) => {
            if (!button.contains(e.target) && !panel.contains(e.target)) {
                panel.classList.remove('open');
            }
        });
    }


    function updateResourceList() {
        let filteredResources = RESOURCES;

        if (searchString) {
            filteredResources = filteredResources.filter(r => r.name.toLowerCase().includes(searchString.toLowerCase()));
        }
        if (selectedCategories.length) {
            filteredResources = filteredResources.filter(r => selectedCategories.includes(r.category));
        }
        if (selectedBranches.length) {
            filteredResources = filteredResources.filter(r => selectedBranches.includes(r.branch));
        }
        if (noCACRequired) {
            filteredResources = filteredResources.filter(r => !r.cac);
        }

        lastFilteredResources = filteredResources; // for export

        const resourcesListing = document.getElementById('resources-list-container');
        if (!filteredResources.length) {
            resourcesListing.innerHTML = 'No resources found matching current filters.';
        } else {
            resourcesListing.innerHTML = `<div class="resources-list">${filteredResources.slice((currentPage - 1) * MAX_RESOURCES_DISPLAY, currentPage * MAX_RESOURCES_DISPLAY).map((resource, idx) => {
                const star = resource.featured ? `<span class="resource-star" title="Featured Resource">★</span>` : '';
                const category_tag = resource.category ? `<span class="resource-tag resource-tag-category">${resource.category}</span>` : '';
                const branch_tag = resource.branch ? `<span class="resource-tag resource-tag-branch">${resource.branch}</span>` : '';
                const cac_tag = resource.cac ? `<span class="resource-tag resource-tag-cac">CAC Required</span>` : '';
                // Bookmark button and tooltip
                const bookmarkBtnId = `bookmark-btn-${currentPage}-${idx}`;
                return `
                    <div class="resource" tabindex="0" style="position:relative;" onclick="window.open('${resource.url}','_blank', 'noopener noreferrer')">
                        <div class="resource-header">
                            ${star}
                            ${resource.name}
                            <button type="button" class="resource-bookmark-btn" id="${bookmarkBtnId}" tabindex="0" onclick="event.stopPropagation(); downloadBookmark('${escapeForAttr(resource.name)}', '${escapeForAttr(resource.url)}', '${bookmarkBtnId}')">Bookmark</button>
                            <span class="resource-bookmark-tooltip" id="${bookmarkBtnId}-tooltip">Press Ctrl+D to instantly bookmark this page</span>
                        </div>
                        <div class="resource-description">${resource.description || ''}</div>
                        <div class="resource-tag-container">${category_tag}${branch_tag}${cac_tag}</div>
                    </div>
                `;
            }).join('')}</div>`;
        }

        const paginationContainer = document.getElementById('resources-pagination');
        const totalPages = Math.ceil(filteredResources.length / MAX_RESOURCES_DISPLAY);

        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
        } else {
            paginationContainer.innerHTML = '';
            for (let i = 1; i <= totalPages; i++) {
                paginationContainer.innerHTML += `<button class="button-resources-pagination${i === currentPage ? ' active' : ''}" data-page="${i}">${i}</button>`;
            }
            paginationContainer.querySelectorAll('button').forEach(button => {
                button.addEventListener('click', () => {
                    currentPage = parseInt(button.getAttribute('data-page'));
                    updateResourceList();
                    const pageContainer = document.getElementById('page-resources');
                    pageContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                });
            });
        }

        const countSpan = document.getElementById('resources-count');
        countSpan.textContent = `${filteredResources.length} Result${filteredResources.length === 1 ? '' : 's'}`;
    }


    // Utility for escaping quotes in attribute values
    function escapeForAttr(str) {
        return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
    }


    // Download .url file for bookmark
    window.downloadBookmark = function(name, url, btnId) {
        const content = `[InternetShortcut]\nURL=${url}\n`;
        const blob = new Blob([content], { type: 'text/plain' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `${name}.url`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(a.href), 100);

        // Show tooltip
        const tooltip = document.getElementById(btnId + '-tooltip');
        if (tooltip) {
            tooltip.style.display = 'block';
            setTimeout(() => { tooltip.style.display = 'none'; }, 2500);
        }
    };

    
    // Export filtered resources as CSV
    function exportResourcesAsCSV(resources) {
        if (!resources.length) return;
        const headers = Object.keys(resources[0]);
        const csvRows = [
            headers.join(','), // header row
            ...resources.map(r => headers.map(h => `"${(r[h] ?? '').toString().replace(/"/g, '""')}"`).join(','))
        ];
        const csvContent = csvRows.join('\r\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'resources_export.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }


    document.getElementById('resources-filter-search').addEventListener('input', e => {
        searchString = e.target.value.slice(0, window.CONFIG.MAX_RESOURCES_SEARCH_LENGTH);
        currentPage = 1;
        updateResourceList();
    });

    document.getElementById('resources-filter-categories').addEventListener('change', e => {
        if (e.target.classList.contains('resources-filter-panel-checkbox')) {
            const option = e.target.value;
            if (e.target.checked) {
                if (!selectedCategories.includes(option)) selectedCategories.push(option);
            } else {
                selectedCategories = selectedCategories.filter(c => c !== option);
            }
            currentPage = 1;
            updateResourceList();
        }
    });

    document.getElementById('resources-filter-branches').addEventListener('change', e => {
        if (e.target.classList.contains('resources-filter-panel-checkbox')) {
            const option = e.target.value;
            if (e.target.checked) {
                if (!selectedBranches.includes(option)) selectedBranches.push(option);
            } else {
                selectedBranches = selectedBranches.filter(b => b !== option);
            }
            currentPage = 1;
            updateResourceList();
        }
    });

    document.getElementById('resources-filter-no-cac').addEventListener('change', e => {
        noCACRequired = e.target.checked;
        currentPage = 1;
        updateResourceList();
    });

    document.getElementById('resources-export-btn').addEventListener('click', () => {
        exportResourcesAsCSV(lastFilteredResources);
    });


    populateFilterPanel('resources-filter-categories', window.CONFIG.RESOURCE_CATEGORIES, 'category');
    populateFilterPanel('resources-filter-branches', window.CONFIG.RESOURCE_BRANCHES, 'branch');
    addFilterButtonEventListener('button-resources-filter-categories', 'resources-filter-categories');
    addFilterButtonEventListener('button-resources-filter-branches', 'resources-filter-branches');
    updateResourceList();
}