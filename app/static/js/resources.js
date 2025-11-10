function initResourcesPage() {
    let RESOURCES = window.CONFIG.RESOURCES;
    const MAX_RESOURCES_DISPLAY = window.CONFIG.MAX_RESOURCES_DISPLAY;
    let searchString = '';
    let selectedCategories = [];
    let selectedBranches = [];
    let currentPage = 1;


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

        const resourcesListing = document.getElementById('resources-list-container');
        if (!filteredResources.length) {
            resourcesListing.innerHTML = 'No resources found matching current filters.';
        } else {
            resourcesListing.innerHTML = `<div class="resources-list">${filteredResources.slice((currentPage - 1) * MAX_RESOURCES_DISPLAY, currentPage * MAX_RESOURCES_DISPLAY).map(resource => {
                const star = resource.featured ? `<span class="resource-star" title="Featured Resource">★</span>` : '';
                const category_tag = resource.category ? `<span class="resource-tag resource-tag-category">${resource.category}</span>` : '';
                const branch_tag = resource.branch ? `<span class="resource-tag resource-tag-branch">${resource.branch}</span>` : '';
                const cac_tag = resource.cac ? `<span class="resource-tag resource-tag-cac">CAC Required</span>` : '';

                return `
                    <div class="resource" onclick="window.open('${resource.url}','_blank', 'noopener noreferrer')">
                        <div class="resource-header">
                            ${star}
                            ${resource.name}
                        </div>
                        <div class="resource-description">${resource.desc}</div>
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

    populateFilterPanel('resources-filter-categories', window.CONFIG.RESOURCE_CATEGORIES, 'category');
    populateFilterPanel('resources-filter-branches', window.CONFIG.RESOURCE_BRANCHES, 'branch');
    addFilterButtonEventListener('button-resources-filter-categories', 'resources-filter-categories');
    addFilterButtonEventListener('button-resources-filter-branches', 'resources-filter-branches');
    updateResourceList();
}