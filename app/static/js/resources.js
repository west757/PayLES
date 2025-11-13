function initResourcesPage() {
    let RESOURCES = window.CONFIG.RESOURCES;
    const MAX_RESOURCES_DISPLAY = window.CONFIG.MAX_RESOURCES_DISPLAY;
    let searchString = '';
    let selectedCategories = [];
    let selectedBranches = [];
    let noCACRequired = false;
    let currentPage = 1;
    let exportResources = [];


    function populateFilterPanel(panelID, options, type) {
        const panel = document.getElementById(panelID);
        panel.innerHTML = options.map(opt => `
            <label class="resources-filter-panel-label">
                <input class="resources-filter-panel-checkbox styled" type="checkbox" value="${opt}" data-type="${type}" />
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

        exportResources = filteredResources;

        const resourcesListing = document.getElementById('resources-list-container');
        if (!filteredResources.length) {
            resourcesListing.innerHTML = 'No resources found matching current filters.';
        } else {
            resourcesListing.innerHTML = `<div class="resources-list">${filteredResources.slice((currentPage - 1) * MAX_RESOURCES_DISPLAY, currentPage * MAX_RESOURCES_DISPLAY).map((resource, idx) => {
                const category_tag = resource.category ? `<span class="resource-tag resource-tag-category">${resource.category}</span>` : '';
                const branch_tag = resource.branch ? `<span class="resource-tag resource-tag-branch">${resource.branch}</span>` : '';
                const cac_tag = resource.cac ? `<span class="resource-tag resource-tag-cac">CAC Required</span>` : '';

                return `
                    <div class="resource" tabindex="0" style="position:relative;" onclick="window.open('${resource.url}','_blank', 'noopener noreferrer')">
                        <div class="resource-header">
                            ${resource.name}
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


    function exportResourcesAsCSV(resources) {
        if (!resources.length) return;
        const headers = Object.keys(resources[0]);
        const csvRows = [
            headers.join(','),
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

    document.getElementById('button-resources-export').addEventListener('click', () => {
        exportResourcesAsCSV(exportResources);
    });


    populateFilterPanel('resources-filter-categories', window.CONFIG.RESOURCE_CATEGORIES, 'category');
    populateFilterPanel('resources-filter-branches', window.CONFIG.RESOURCE_BRANCHES, 'branch');
    addFilterButtonEventListener('button-resources-filter-categories', 'resources-filter-categories');
    addFilterButtonEventListener('button-resources-filter-branches', 'resources-filter-branches');
    updateResourceList();
}