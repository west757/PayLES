function renderResourceList(resources) {
    const container = document.getElementById('resources-listing');
    if (!resources.length) {
        container.innerHTML = '<div style="margin:2em 0;color:#888;">No resources found.</div>';
        return;
    }
    container.innerHTML = `<div class="resources-list">${resources.map(resource => {
        const star = resource.featured ? `<span class="resource-featured-star" title="Featured Resource">★</span>` : '';
        const cats = resource.category ? `<span class="resource-category-badge">${resource.category}</span>` : '';
        const branches = resource.branch ? `<span class="resource-branch-badge">${resource.branch}</span>` : '';
        const cac = resource.cac ? `<span class="resource-cac-badge">CAC Required</span>` : '';
        return `
            <div class="resource-rect" tabindex="0" onclick="window.open('${resource.url}','_blank', 'noopener noreferrer')" title="${resource.name}">
                <div class="resource-main">
                    <div class="resource-name">
                        ${star}
                        ${resource.name}
                    </div>
                    <div class="resource-desc">${resource.desc || ''}</div>
                    <div class="resource-meta">${cats}${branches}${cac}</div>
                </div>
            </div>
        `;
    }).join('')}</div>`;
}


function initResourcesPage() {
    let RESOURCES = window.CONFIG.RESOURCES;
    const MAX_RESOURCES_DISPLAY = window.CONFIG.MAX_RESOURCES_DISPLAY;
    let searchString = '';
    let selectedCategories = [];
    let selectedBranches = [];
    let currentPage = 1;
    

    function renderDropdownPanel(panelId, options, selected, type) {
        const panel = document.getElementById(panelId);
        panel.innerHTML = options.map(opt => `
            <label class="resources-filter-label">
                <input type="checkbox" class="resources-filter-checkbox" value="${opt}" ${selected.includes(opt) ? 'checked' : ''} data-type="${type}" />
                ${opt}
            </label>
        `).join('');
    }


    function setupDropdown(btnId, panelId) {
        const btn = document.getElementById(btnId);
        const panel = document.getElementById(panelId);
        btn.addEventListener('click', () => {
            panel.classList.toggle('open');
        });
        document.addEventListener('click', (e) => {
            if (!btn.contains(e.target) && !panel.contains(e.target)) {
                panel.classList.remove('open');
            }
        });
    }


    function filterResources() {
        let filtered = RESOURCES;
        if (searchString) {
            const sv = searchString.toLowerCase();
            filtered = filtered.filter(r => r.name.toLowerCase().includes(sv));
        }
        if (selectedCategories.length) {
            filtered = filtered.filter(r =>
                selectedCategories.includes(r.category)
            );
        }
        if (selectedBranches.length) {
            filtered = filtered.filter(r =>
                selectedBranches.includes(r.branch)
            );
        }
        return filtered;
    }


    function renderPagination(total, page) {
        const container = document.getElementById('resources-pagination');
        const totalPages = Math.ceil(total / MAX_RESOURCES_DISPLAY);
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        container.innerHTML = '';
        for (let i = 1; i <= totalPages; i++) {
            container.innerHTML += `<button class="button-resources-pagination ${i === page ? ' active' : ''}" data-page="${i}">${i}</button>`;
        }
        container.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                currentPage = parseInt(btn.getAttribute('data-page'));
                updateResourceList();
                // Scroll to top of the resources page
                const pageContainer = document.getElementById('page-resources');
                if (pageContainer) {
                    pageContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }


    function updateResourceList() {
        const filtered = filterResources();
        const start = (currentPage - 1) * MAX_RESOURCES_DISPLAY;
        const end = start + MAX_RESOURCES_DISPLAY;
        renderResourceList(filtered.slice(start, end));
        renderPagination(filtered.length, currentPage);
        // Update resource count
        const countSpan = document.getElementById('resources-count');
        countSpan.textContent = `${filtered.length} Resource${filtered.length === 1 ? '' : 's'}`;
    }


    document.getElementById('resources-filter-search').addEventListener('input', e => {
        searchString = e.target.value.slice(0, window.CONFIG.MAX_RESOURCES_SEARCH_LENGTH);
        currentPage = 1;
        updateResourceList();
    });

    document.getElementById('resources-filter-categories').addEventListener('change', e => {
        if (e.target.classList.contains('resources-filter-checkbox')) {
            const val = e.target.value;
            if (e.target.checked) {
                if (!selectedCategories.includes(val)) selectedCategories.push(val);
            } else {
                selectedCategories = selectedCategories.filter(c => c !== val);
            }
            currentPage = 1;
            updateResourceList();
        }
    });

    document.getElementById('resources-filter-branches').addEventListener('change', e => {
        if (e.target.classList.contains('resources-filter-checkbox')) {
            const val = e.target.value;
            if (e.target.checked) {
                if (!selectedBranches.includes(val)) selectedBranches.push(val);
            } else {
                selectedBranches = selectedBranches.filter(b => b !== val);
            }
            currentPage = 1;
            updateResourceList();
        }
    });

    renderDropdownPanel('resources-filter-categories', window.CONFIG.RESOURCE_CATEGORIES, selectedCategories, 'category');
    renderDropdownPanel('resources-filter-branches', window.CONFIG.RESOURCE_BRANCHES, selectedBranches, 'branch');
    setupDropdown('button-resources-filter-categories', 'resources-filter-categories');
    setupDropdown('button-resources-filter-branches', 'resources-filter-branches');
    updateResourceList();
};